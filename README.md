# GENSET MONITOR 360 — KMZ original corregido

Esta versión sustituye los puntos ficticios de la versión anterior. Incluye exactamente 19 posiciones de GENSET estacionarios y el punto de inicio Taller de Electricidad, extraídos del archivo `GENSET ESTACIONARIOS .kmz`. Los nombres y coordenadas están incrustados en `index.html` y aparecen automáticamente en Ubicaciones.

## Aviso de seguridad importante

El repositorio `genset-monitor-demo` y GitHub Pages son **PÚBLICOS**. Si subes este archivo, **cualquier persona puede leer las coordenadas exactas del KMZ**, aunque no active el mapa satelital. Publícalo solamente si la autorización de Chinalco cubre expresamente la divulgación pública de las ubicaciones. De lo contrario, utiliza la versión segura con importación local.

## Cómo reemplazar el archivo web

1. Entra al repositorio `genset-monitor-demo` (no al privado).
2. Usa **Add file → Upload files** y sube el nuevo `index.html` para sustituir el anterior.
3. Confirma el commit en la rama `principal`.
4. Revisa **Settings → Pages** y abre la URL del sitio después de que termine la publicación.
5. Abre **Ubicaciones**. Los 19 estacionarios y el Taller estarán precargados.

**Alcance:** solo las coordenadas y nombres son documentales del KMZ. Los estados, marcas no indicadas en el KMZ y horómetros de demostración **no son datos operativos reales**. El recorrido dibujado es por segmentos rectos, no una ruta vehicular validada. GitHub Pages no ofrece seguimiento GNSS en tiempo real.
