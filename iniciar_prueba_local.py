"""Demo local con dos cuentas temporales y SQLite persistente.
No abre el servicio al exterior: solo escucha 127.0.0.1.
"""
import os
import secrets
import webbrowser
from threading import Timer

os.environ.setdefault("GENSET_ADMIN_PASSWORD", secrets.token_urlsafe(24))
os.environ.setdefault("GENSET_OPERATOR_PASSWORD", secrets.token_urlsafe(24))
os.environ.setdefault("GENSET_ADMIN_USER", "administrador")
os.environ.setdefault("GENSET_OPERATOR_USER", "operador")

print("\n"+"="*65)
print("GENSET MONITOR 360 - PRUEBA LOCAL")
print("Abra: http://127.0.0.1:8000")
print("ADMIN usuario:",os.environ["GENSET_ADMIN_USER"])
print("ADMIN contraseña:",os.environ["GENSET_ADMIN_PASSWORD"])
print("OPERADOR usuario:",os.environ["GENSET_OPERATOR_USER"])
print("OPERADOR contraseña:",os.environ["GENSET_OPERATOR_PASSWORD"])
print("Datos de prueba guardados en genset_local.sqlite3")
print("No es accesible desde otro equipo ni es un despliegue online.")
print("="*65+"\n")

if __name__=="__main__":
    Timer(1.5,lambda:webbrowser.open("http://127.0.0.1:8000")).start()
    import uvicorn
    uvicorn.run("server:app",host="127.0.0.1",port=8000,log_level="warning")
