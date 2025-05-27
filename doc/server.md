[server]

# Lista de carpetas que no deben ser monitoreadas para cambios.
folderWatchBlacklist = []

# Define el método de monitoreo de archivos en la aplicación.
# Opciones:
# - "auto"     → Usa watchdog si está disponible, si no, usa polling.
# - "watchdog" → Obliga el uso de watchdog (más eficiente).
# - "poll"     → Usa polling, menos eficiente pero más compatible.
# - "none"     → No monitorea cambios en archivos.
fileWatcherType = "auto"

# Clave secreta utilizada para firmar cookies en la aplicación.
cookieSecret = "a-random-key-appears-here"

# Define si Streamlit debe abrir automáticamente el navegador al iniciar.
headless = false

# Define si la aplicación debe recargarse cuando un archivo sea modificado.
runOnSave = false

# Puerto donde el servidor escucha conexiones.
port = 8501

# Activa protección contra accesos no autorizados desde otros dominios.
enableCORS = true

# Activa protección contra falsificación de solicitudes entre sitios.
enableXsrfProtection = true

# Tamaño máximo de archivos subidos (MB).
maxUploadSize = 200

# Tamaño máximo de mensajes WebSocket (MB).
maxMessageSize = 200

# Permite servir archivos estáticos desde la carpeta `static`.
enableStaticServing = false

# Tiempo de vida de sesiones desconectadas (segundos).
disconnectedSessionTTL = 120
