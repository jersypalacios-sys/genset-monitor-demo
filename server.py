"""GENSET MONITOR 360 - servidor online para piloto controlado.

Acceso administrativo y operadores mediante HTTP Basic sobre HTTPS.
Posiciones GPS voluntarias de móvil y actualización de datos manuales de flota.
NO hay conexión a controladores/ECU de grupos electrógenos.
NO despliegue OT productivo sin aprobación TI/OT, SSO, auditoría y hardening.
"""
from __future__ import annotations

import hmac
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional, Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Request, status
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import (
    Column, Float, Integer, MetaData, String, Table, Text, create_engine,
    desc, func, insert, select, update
)

BASE = Path(__file__).resolve().parent
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///" + str(BASE / "genset_local.sqlite3")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len("postgres://"):]
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len("postgresql://"):]

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True, connect_args={"check_same_thread":False} if DATABASE_URL.startswith("sqlite:") else {})
meta = MetaData()
positions = Table(
    "positions", meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("genset_id", String(40), nullable=False, index=True),
    Column("latitude", Float, nullable=False),
    Column("longitude", Float, nullable=False),
    Column("accuracy_m", Float),
    Column("timestamp", String(40), nullable=False),
    Column("received_at", String(40), nullable=False),
    Column("source", String(100), nullable=False),
)
fleet_changes = Table(
    "fleet_changes", meta,
    Column("genset_id", String(40), primary_key=True),
    Column("payload", Text, nullable=False),
    Column("updated_at", String(40), nullable=False),
)
meta.create_all(engine)

MOBILE_IDS = [5,10,11,12,13,17,20,26,28,29,30,31,33,34,9,24,7,15]
MOBILE = frozenset(f"GENSET-{i:02d}" for i in MOBILE_IDS)
# Se valida por formato para permitir los estacionarios multimarca documentados.
TAG_RE = re.compile(r"^[A-Z0-9][A-Z0-9_-]{2,39}$")

ADMIN_USER = os.getenv("GENSET_ADMIN_USER", "administrador")
ADMIN_PASS = os.getenv("GENSET_ADMIN_PASSWORD", "")
OP_USER = os.getenv("GENSET_OPERATOR_USER", "operador")
OP_PASS = os.getenv("GENSET_OPERATOR_PASSWORD", "")
DEVICE_TOKEN = os.getenv("GENSET_DEVICE_TOKEN", "")

security = HTTPBasic(auto_error=False)
app = FastAPI(title="GENSET MONITOR 360 - ONLINE", version="1.0-demo", docs_url=None, redoc_url=None, openapi_url=None)

@app.middleware("http")
async def privacy_headers(request:Request, call_next):
    response = await call_next(request)
    response.headers.update({
        "Cache-Control":"no-store, max-age=0",
        "X-Content-Type-Options":"nosniff",
        "X-Frame-Options":"DENY",
        "Referrer-Policy":"no-referrer",
        "Permissions-Policy":"geolocation=(self)",
        "Content-Security-Policy":"frame-ancestors 'none'",
    })
    return response


def _fail():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales requeridas.",
        headers={"WWW-Authenticate": 'Basic realm="GENSET MONITOR 360"'},
    )


def user_role(c: Optional[HTTPBasicCredentials] = Depends(security)) -> str:
    if not ADMIN_PASS or not OP_PASS or len(ADMIN_PASS) < 16 or len(OP_PASS) < 16:
        raise HTTPException(status_code=503,detail="Configurar contraseñas ADMIN/OPERADOR de 16+ caracteres en el servidor.")
    if c is None:
        _fail()
    if hmac.compare_digest(c.username.encode(),ADMIN_USER.encode()) and hmac.compare_digest(c.password.encode(),ADMIN_PASS.encode()):
        return "admin"
    if hmac.compare_digest(c.username.encode(),OP_USER.encode()) and hmac.compare_digest(c.password.encode(),OP_PASS.encode()):
        return "operador"
    _fail()


def require_admin(role:str=Depends(user_role)):
    if role != "admin":
        raise HTTPException(status_code=403,detail="Solo el administrador puede consultar toda la flota.")
    return role


def require_mobile(tag:str):
    if tag not in MOBILE:
        raise HTTPException(status_code=404,detail="Este TAG no está en el inventario de móviles.")


def require_fleet(tag:str):
    if not TAG_RE.fullmatch(tag):
        raise HTTPException(status_code=400,detail="TAG de equipo inválido.")

class PositionIn(BaseModel):
    latitude: float = Field(ge=-90,le=90)
    longitude: float = Field(ge=-180,le=180)
    accuracy_m: Optional[float] = Field(default=None,ge=0,le=100000)

class DeviceIn(PositionIn):
    timestamp: Optional[datetime]=None

class FleetIn(BaseModel):
    brand: str = Field(max_length=100)
    model: str = Field(max_length=130)
    location: str = Field(max_length=150)
    state: Literal["running","stopped"]
    hours: Optional[float] = Field(default=None,ge=0,le=10000000)
    worked: Optional[float] = Field(default=None,ge=0,le=10000000)
    lastPM: Optional[float] = Field(default=None,ge=0,le=10000000)
    manualAlarm: bool = False
    manualAlarmNote: str = Field(default="", max_length=200)

    @model_validator(mode="after")
    def last_pm_guard(self):
        if self.hours is not None and self.lastPM is not None and self.lastPM>self.hours:
            raise ValueError("El último PM no puede superar el horómetro total.")
        return self


def db_latest(tag):
    with engine.connect() as con:
        row=con.execute(select(positions).where(positions.c.genset_id==tag).order_by(desc(positions.c.id)).limit(1)).mappings().first()
        return dict(row) if row else None


def save_point(tag, data, source, moment=None):
    require_mobile(tag)
    now=datetime.now(timezone.utc)
    at=moment or now
    if at.tzinfo is None:
        at=at.replace(tzinfo=timezone.utc)
    at=at.astimezone(timezone.utc)
    if at>now+timedelta(minutes=5) or at<now-timedelta(days=30):
        raise HTTPException(status_code=400,detail="La fecha del GPS está fuera del rango admitido.")
    rec={
        "genset_id":tag, "latitude":data.latitude, "longitude":data.longitude,
        "accuracy_m":data.accuracy_m, "timestamp":at.isoformat(),
        "received_at":now.isoformat(), "source":source,
    }
    with engine.begin() as con:
        con.execute(insert(positions).values(**rec))
    return rec

@app.get("/health")
def health():
    return {"status":"ok", "mode":"online", "telemetry_connected":False, "gps_checkin":True}

@app.get("/")
@app.get("/index.html")
def page_admin(role=Depends(require_admin)):
    return FileResponse(BASE/"index.html",media_type="text/html")

@app.get("/mobile")
def page_mobile(tag:str=Query(...), role=Depends(user_role)):
    require_mobile(tag)
    return FileResponse(BASE/"mobile.html",media_type="text/html")

@app.get("/api/v1/mobiles/positions",dependencies=[Depends(require_admin)])
def last_mobiles():
    max_ids=select(func.max(positions.c.id)).group_by(positions.c.genset_id)
    with engine.connect() as con:
        rows=con.execute(select(positions).where(positions.c.id.in_(max_ids)).order_by(positions.c.genset_id)).mappings().all()
        return {"items":[dict(r) for r in rows]}

@app.get("/api/v1/mobiles/{tag}/location",dependencies=[Depends(user_role)])
def last_mobile(tag:str):
    require_mobile(tag)
    rec=db_latest(tag)
    if not rec:raise HTTPException(404,"Aún no hay una posición reportada.")
    return rec

@app.post("/api/v1/mobiles/{tag}/checkin",dependencies=[Depends(user_role)])
def mobile_checkin(tag:str,point:PositionIn):
    return save_point(tag,point,"GPS del teléfono / escaneo QR autorizado")

@app.post("/api/v1/mobiles/{tag}/telemetry")
def mobile_telemetry(tag:str,point:DeviceIn,request:Request):
    # Un token distinto para un futuro dispositivo GNSS; no se crea por el QR.
    credential=request.headers.get("Authorization","")
    if not DEVICE_TOKEN or len(DEVICE_TOKEN)<24 or not credential.startswith("Bearer ") or not hmac.compare_digest(credential[7:],DEVICE_TOKEN):
        raise HTTPException(status_code=401,detail="Autenticación del dispositivo requerida.")
    return save_point(tag,point,"GNSS de dispositivo conectado / API",point.timestamp)

@app.get("/api/v1/fleet",dependencies=[Depends(require_admin)])
def get_fleet_overrides():
    with engine.connect() as con:
        rows=con.execute(select(fleet_changes)).mappings().all()
        return {"overrides":{r["genset_id"]:json.loads(r["payload"]) for r in rows}}

@app.put("/api/v1/fleet/{tag}",dependencies=[Depends(require_admin)])
def put_fleet(tag:str,point:FleetIn):
    require_fleet(tag)
    now=datetime.now(timezone.utc).isoformat()
    vals={"genset_id":tag,"payload":point.model_dump_json(),"updated_at":now}
    with engine.begin() as con:
        existing=con.execute(select(fleet_changes.c.genset_id).where(fleet_changes.c.genset_id==tag)).first()
        if existing:
            con.execute(update(fleet_changes).where(fleet_changes.c.genset_id==tag).values(payload=vals["payload"],updated_at=now))
        else:
            con.execute(insert(fleet_changes).values(**vals))
    return {"ok":True,"genset_id":tag,"updated_at":now}
