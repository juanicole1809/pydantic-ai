"""
Archivo de configuración global para la aplicación.
Contiene constantes y configuraciones usadas en toda la aplicación.
"""

# Definición de modelos disponibles
MODELOS = {
    "Conversación": [
        "llama-3.3-70b-versatile",
        "qwen-2.5-32b",
        "qwen-2.5-coder-32b",
        "qwen-qwq-32b"
    ],
    "Audio a Texto": [
        "whisper-large-v3",
        "whisper-large-v3-turbo",
        "distil-whisper-large-v3-en"
    ],
    "Razonamiento": [
        "deepseek-r1-distill-llama-70b",
        "deepseek-r1-distill-qwen-32b"
    ]
}

# Configuraciones predeterminadas
DEFAULT_SYSTEM_PROMPT = ("Eres un asistente de inteligencia artificial útil, claro y conciso. "
                         "Tu objetivo es ayudar al usuario proporcionando respuestas precisas y "
                         "fáciles de entender. Siempre responde en español, y si el usuario hace "
                         "una pregunta ambigua, pide amablemente más detalles.")

DEFAULT_TEMPERATURE = 0.9
DEFAULT_MAX_TOKENS = 1024
DEFAULT_MODEL_TYPE = "Conversación"
DEFAULT_MODEL = "llama-3.3-70b-versatile" 