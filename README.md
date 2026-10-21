# Mova — calistenia personal

Ubicación: C:\App Ejercicio

Web: https://nmillana.github.io/Mova/

Repositorio: https://github.com/nmillana/Mova

## Abrir
Haz doble clic en **Abrir Mova.cmd**. Abre http://127.0.0.1:5178/ y usa los archivos compilados de dist. Requiere Node.js (ya disponible en este equipo). No requiere instalar dependencias para abrir esta versión compilada. El servicio escucha solo en este equipo.

La encuesta configura objetivo, experiencia, 10/12/15 minutos, 2/3/4 días por semana, silla, movimientos a evitar, modo cuidadoso para diástasis y narración. Cada ejercicio usa un GIF local del avatar; la app no incrusta ni reproduce vídeos externos. En Microsoft Edge se puede elegir una voz Microsoft disponible.

## Desarrollo
- npm install
- npm run dev
- npm run build
- npm test
- node tests/browser.mjs (con servidor activo y Edge instalado)
- node tests/media.mjs (valida GIF de diástasis y ausencia de reproductores externos)

React + Vite + Tailwind. Datos en localStorage bajo mova-personal-v1. Sin backend, variables de entorno, claves, login ni conexión a Supabase. La exportación JSON es un respaldo de lectura; aún no hay importador.

Las rutinas incluyen 2 minutos de calentamiento, 7/9/12 bloques de un minuto (trabajo + descanso) y 1 minuto final. Pausas voluntarias extienden la duración de reloj. Al cambiar de pestaña se pausa por seguridad. Sesiones interrumpidas se recuperan pausadas. Omitir bloques o terminar antes queda como registro parcial; no desbloquea logros de sesión completa.

Los datos pertenecen al navegador y al origen exacto http://127.0.0.1:5178/; usar localhost, otro navegador o borrar datos del sitio crea otro espacio. No hay sincronización entre dispositivos. Las notas y preferencias no se envían al servidor. Los GIF funcionan localmente y no contactan proveedores de vídeo.

## Referencias
Revisión documental de flujos públicos, sin extracción de código propietario.
- https://help.calisteniapp.com/en/docs/explore
- https://www.freeletics.com/en/blog/posts/coach-feedback/
- https://www.nhs.uk/live-well/exercise/strength-and-flex-exercise-plan-how-to-videos/
- https://www.royalberkshire.nhs.uk/media/mqjfxwgj/physio-separation-of-the-abdominal-muscles.pdf
- https://my.clevelandclinic.org/health/diseases/22346-diastasis-recti
- https://www.southtees.nhs.uk/resources/combined-press-ups/
- https://www.youtube.com/watch?v=xEDnlOxeJH4

Los personajes 3D y sus GIF son originales y orientativos. Los GIF están en public/animations; los WebP estáticos en public/characters; los PNG fuente y fotogramas se conservan en artifacts. Los vídeos citados se usaron como referencia técnica y no se reproducen dentro de la app.
Los ejercicios no sustituyen una evaluación profesional. El modo de diástasis usa activación profunda, inclinación pélvica y basculación suave; excluye planchas, flexiones y movimientos no marcados como compatibles. La selección automática no diagnostica ni prescribe rehabilitación.

El prototipo inicial BASE se conserva como respaldo en archive/base-v0.html.
