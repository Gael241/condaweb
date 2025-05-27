[runner]

# Permite escribir variables directamente sin necesidad de usar `print()`.
# Opciones:
# - true  → Activa la función mágica.
# - false → Desactiva la función mágica.
magicEnabled = true

# Controla si Streamlit recarga el script inmediatamente tras interacción del usuario.
# Opciones:
# - true  → Recarga rápida.
# - false → Espera puntos específicos de ejecución.
fastReruns = true

# Activa una verificación para detectar datos no serializables en `session_state`.
# Opciones:
# - true  → Lanza una excepción si se detecta un objeto no serializable.
# - false → No aplica restricciones de serialización.
enforceSerializableSessionState = false

# Controla cómo Streamlit maneja los valores de clases `Enum` en widgets.
# Opciones:
# - "off"          → No aplica conversión.
# - "nameOnly"     → Convierte valores si los nombres coinciden.
# - "nameAndValue" → Convierte valores si nombres y valores coinciden exactamente.
enumCoercion = "nameOnly"
