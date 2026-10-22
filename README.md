# GENSET MONITOR 360 · Repositorio privado de Chinalco (piloto)

> **ESTADO: preparado para GitHub; NO está desplegado online**. No contiene conexión real a los controladores de los GENSET. Antes de usar coordenadas reales fuera de la red corporativa, obtener autorización TI/OT.

## Qué incluye

- `index.html`: dashboard de 37 equipos y visualización del mapa de estacionarios.
- `mobile.html`: pantalla que abre un QR en un móvil autorizado para registrar su GPS al momento de un escaneo.
- `server.py`: API FastAPI con roles administrador/operador y datos compartidos.
- `render.yaml`: propuesta de servidor web + PostgreSQL en Render (**servicios externos, costes por comprobar**).
- `Dockerfile`: alternativa de alojamiento autorizado.
- `.github/workflows/validate.yml`: comprueba sintaxis y endpoints básicos con cada cambio.
- `ubicaciones_kmz.geojson` y `ESTACIONARIOS_Y_TALLER_ACTUALIZADO.kml`: **coordenadas reales procedentes del KMZ, datos sensibles**.

## 1. Crear un repositorio PRIVADO en GitHub

1. Solicita autorización a TI/OT para subir el código y **especialmente los ficheros de coordenadas** a un proveedor externo.
2. En [github.com/new](https://github.com/new) crea un repositorio llamado, por ejemplo, `genset-monitor-360`.
3. Selecciona **Private (privado)**. No marques la creación automática de README o .gitignore.
4. Descomprime este ZIP y abre PowerShell en esta carpeta.
5. Si ya instalaste Git, ejecuta (sustituye `TU_USUARIO` por el tuyo):

```powershell
git init
git branch -M main
git add .
git commit -m "Versión inicial GENSET MONITOR 360"
git remote add origin https://github.com/TU_USUARIO/genset-monitor-360.git
git push -u origin main
```

También puedes usar **GitHub Desktop** para publicar la carpeta como repositorio privado. Nunca subas contraseñas ni archivos `.env`.

## 2. Publicar la aplicación ONLINE (no GitHub Pages)

**GitHub aloja y versiona el código, pero no ejecuta FastAPI/PostgreSQL con GitHub Pages**. Para que los QR actualicen ubicaciones entre celulares necesitas ejecutar el backend.

- **Producción minera:** preferir servidor autorizado de Chinalco, VPN, HTTPS y base de datos corporativa.
- **Demo externa aprobada:** desde [dashboard.render.com](https://dashboard.render.com/), conectar tu cuenta GitHub y elegir **New → Blueprint**, seleccionando este repo privado. El servicio utiliza `render.yaml`.
- Establecer en Render las variables secretas `GENSET_ADMIN_PASSWORD` y `GENSET_OPERATOR_PASSWORD` con claves distintas de al menos 16 caracteres. El `GENSET_DEVICE_TOKEN` es opcional y se reservará para equipos GNSS futuros (24+ caracteres).
- Revisar plan/costos, región, persistencia, copias de seguridad y políticas TI/OT **antes de confirmar**.
- Cuando Render proporcione HTTPS, abrir la URL con credenciales de administrador y revisar el panel **QR móviles**.

Si el repositorio y los servicios ya están publicados, los cambios que envíes a la rama `main` se podrán desplegar mediante la integración GitHub→Render. La fecha y automatización concreta dependen de la configuración elegida.

## 3. Probar localmente sin publicar

En Windows, ejecutar `INICIAR_PRUEBA_LOCAL_WINDOWS.bat` (Python 3.10+). Esta prueba **no es online**. Puedes también usar:

```bash
python -m pip install -r requirements.txt
# Definir GENSET_ADMIN_PASSWORD y GENSET_OPERATOR_PASSWORD en tu entorno
uvicorn server:app --host 127.0.0.1 --port 8000
```

Abrir http://127.0.0.1:8000, ingresar como `administrador` y su contraseña. En el menú QR móviles, una etiqueta abre `/mobile?tag=GENSET-05`. Si se autoriza el GPS del teléfono, se guarda una posición puntual (no rastreo continuo).

## 4. Limitaciones importantes

- El HTML puede abrirse offline como demostración, pero el modo multiusuario solo funciona desde el servidor.
- El botón de escaneo **no convierte automáticamente un QR en rastreador**. Cada posición del teléfono requiere autorización y envío de datos. Posición GNSS automática requiere hardware instalado y cobertura.
- Los 19 estacionarios son ubicaciones documentales de KMZ, no telemetría GNSS continua.
- El controlador y la compatibilidad real de cada generador todavía deben verificarse. No hay arranque/parada remoto en este software.
- Mantener el repositorio privado **no sustituye** aprobación TI/OT ni cifrado/acceso empresarial.

Lee también [SEGURIDAD.md](SEGURIDAD.md), [LEEME_DESPLEGAR_ONLINE.txt](LEEME_DESPLEGAR_ONLINE.txt).
