# Seguridad y uso de ubicaciones

Este repositorio contiene coordenadas de infraestructura industrial suministradas por el usuario. **Se debe mantener privado y contar con autorización corporativa para alojarlo en servicios externos.**

- No usar **GitHub Pages público** con mapas reales del proyecto.
- No almacenar claves, tokens, contraseñas, cookies ni certificados dentro del repositorio, QR o direcciones URL.
- Rotar y revocar cualquier credencial expuesta accidentalmente, incluso si se elimina en un commit posterior.
- Usar HTTPS, acceso autenticado, control de roles, registro de auditoría, copias de seguridad y segmentación TI/OT antes de un piloto real.
- En la versión actual, el backend usa HTTP Basic como **demostración controlada**, no es solución empresarial final. Coordinar SSO/MFA/VPN con TI/OT.
- Si un teléfono envía una ubicación mediante QR, comprobar presencia física y consentimiento; no presentar esa lectura como posición automática del GENSET.
- Los mapas satelitales de terceros pueden recibir peticiones relacionadas con coordenadas: habilitarlos solo después de autorización.

> Las ubicaciones del KMZ pueden tener diferencias en códigos TAG; validar inventario y placas antes de usar en operaciones.
