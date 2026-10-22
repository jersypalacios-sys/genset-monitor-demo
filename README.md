# GENSET MONITOR 360 · Demostración pública segura

Esta carpeta contiene un **prototipo estático** para GitHub Pages. No incluye el inventario ni las coordenadas reales de Chinalco, y no necesita un servidor Python.

## ¿Cómo veo los estacionarios reales sin publicarlos?

1. Abre `index.html` o la página publicada en GitHub Pages.
2. Entra en **Ubicaciones**.
3. En «Cargar ubicaciones desde tu computadora», elige tu archivo privado `GENSET ESTACIONARIOS .kmz`.
4. Verás los marcadores, coordenadas y el recorrido desde Taller de Electricidad en tu propio navegador.
5. Al recargar la página, desaparecen los puntos reales: no se guardan ni se envían al servidor.

**Advertencia:** el botón «Vista satelital» está desactivado por defecto. Si lo habilitas, el navegador solicita mosaicos de Esri y puede transmitir el área del mapa al proveedor externo. Su uso con coordenadas reales debe estar autorizado.

## Subir a GitHub Pages

1. En tu cuenta, crea un **repositorio nuevo y público exclusivo para esta demo**, por ejemplo `genset-monitor-demo`.
2. **Sube solamente `index.html` y este `README.md`** (no subas el KMZ, KML, GeoJSON, ni el ZIP privado anterior).
3. En GitHub: **Settings → Pages → Build and deployment → Source: Deploy from a branch**.
4. Selecciona rama `main` (o la rama predeterminada que exista), carpeta `/(root)`, y presiona **Save**.
5. Tras publicarse, visita la dirección indicada por GitHub en Pages. La URL habitualmente será `https://TU_USUARIO.github.io/genset-monitor-demo/`.

### Privacidad

- No se incluyen ubicaciones reales ni TAG originales en el código público.
- La importación usa File API, DOMParser y DecompressionStream del navegador, sin subir el KMZ.
- No hay `fetch` para transmitir ubicaciones; no hay almacenamiento local persistente de puntos importados.
- El ejemplo de flota, alarmas y horómetros es ficticio y no constituye monitoreo real.
- GitHub Pages no ejecuta `server.py`, ni guarda GPS de QR, ni proporciona una API privada.
- Evita usar una computadora compartida para consultar datos sensibles.
