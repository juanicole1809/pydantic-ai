import streamlit as st
import groq
import os
from typing import List, Dict
from dotenv import load_dotenv
import time
import base64
import importlib.util

# Verificar si pydantic_ai está instalado
pydantic_available = importlib.util.find_spec("pydantic_ai") is not None

# Verificar si nest_asyncio está instalado (para entornos Jupyter)
nest_asyncio_available = importlib.util.find_spec("nest_asyncio") is not None

# Importar pydantic_ai y nest_asyncio si están disponibles
if pydantic_available:
    try:
        from pydantic_ai import Agent
        # Aplicar nest_asyncio si está disponible (para compatibilidad con Jupyter)
        if nest_asyncio_available:
            import nest_asyncio
            nest_asyncio.apply()
    except ImportError:
        pydantic_available = False

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Asistente IA con Groq",
    page_icon="🤖",
    layout="centered"
)

# Estilo CSS personalizado
st.markdown("""
<style>
/* Estilos generales para los contenedores de chat */
.chat-container {
    border-radius: 12px;
    margin-bottom: 15px;
    padding: 15px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    border: 1px solid rgba(0,0,0,0.05);
}

/* Estilos para mensajes del usuario */
.user-message {
    background-color: var(--primary-color-light);
    text-align: right;
    color: var(--text-color);
    font-weight: 500;
    margin-left: 20%;
}

/* Estilos para mensajes del asistente */
.assistant-message {
    background-color: var(--secondary-background-color);
    color: var(--text-color);
    font-weight: 500;
    margin-right: 20%;
}

/* Estilos para el texto del chat */
.chat-text {
    font-size: 16px;
    line-height: 1.5;
    color: var(--text-color) !important;
}

/* Estilos para encabezados de los mensajes */
.user-header, .assistant-header {
    font-weight: 700;
    margin-bottom: 5px;
}

.user-header {
    color: var(--primary-color);
}

.assistant-header {
    color: var(--text-color);
}

/* Ajustes para la zona de entrada de texto */
.stTextInput input {
    border-radius: 20px;
    padding: 10px 15px;
}

/* Estilos para la sección de razonamiento */
.reasoning-section {
    background-color: rgba(var(--primary-color-rgb, 75, 75, 255), 0.05);
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0 15px 0;
    border-left: 4px solid var(--primary-color);
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.thinking-title {
    font-weight: 700;
    color: var(--primary-color);
    margin-bottom: 8px;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
}

.thinking-title:before {
    content: "💭";
    margin-right: 6px;
}

/* Contenido del razonamiento con estilo diferenciado */
.reasoning-content {
    font-family: monospace;
    font-size: 14px;
    line-height: 1.6;
    color: var(--text-color);
    opacity: 0.85;
    background-color: rgba(0,0,0,0.03);
    padding: 10px;
    border-radius: 4px;
}

/* Estilo para el mensaje de advertencia */
.warning-message {
    background-color: rgba(255, 152, 0, 0.15);
    border-left: 3px solid #FF9800;
    padding: 10px;
    border-radius: 4px;
    margin: 10px 0;
}

/* Estilos para botones de conversación */
.conversation-button {
    background-color: var(--primary-color);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 12px;
    margin: 5px 0;
    cursor: pointer;
    width: 100%;
    font-weight: bold;
    text-align: center;
    transition: all 0.3s ease;
}

.conversation-button:hover {
    opacity: 0.9;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}

.conversation-button.new {
    background-color: var(--primary-color);
}

.conversation-button.clear {
    background-color: #f44336;
}

.conversation-button.cancel {
    background-color: #9e9e9e;
}

.conversation-button.confirm {
    background-color: #4CAF50;
}

/* Crear variables personalizadas basadas en el tema actual */
:root {
    --primary-color-light: rgba(var(--primary-color-rgb, 255, 75, 75), 0.1);
}

/* Mejoras para la legibilidad en tema oscuro */
[data-testid="stMarkdown"] {
    color: var(--text-color);
}

/* Estilo mejorado para botones de Streamlit */
button[data-testid="baseButton-secondary"] {
    background-color: var(--primary-color);
    color: white !important;
    border: none !important;
    border-radius: 8px;
    padding: 10px 15px;
    font-weight: bold;
    text-align: center;
    transition: all 0.2s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

button[data-testid="baseButton-secondary"]:hover {
    opacity: 0.9;
    box-shadow: 0 2px 5px rgba(0,0,0,0.3);
    transform: translateY(-1px);
}

/* Botón de limpiar chat */
.element-container:has(button:contains("🗑️")) button[data-testid="baseButton-secondary"] {
    background-color: #f44336;
}

/* Botón de confirmación */
.element-container:has(button:contains("✅")) button[data-testid="baseButton-secondary"] {
    background-color: #4CAF50;
}

/* Botón de cancelar */
.element-container:has(button:contains("❌")) button[data-testid="baseButton-secondary"] {
    background-color: #9e9e9e;
}
</style>
""", unsafe_allow_html=True)


# Inicializar las variables de la sesión
if 'messages' not in st.session_state:
    st.session_state.messages = []
    
if 'pydantic_agent' not in st.session_state:
    st.session_state.pydantic_agent = None
    
if 'pydantic_history' not in st.session_state:
    st.session_state.pydantic_history = []
    
if 'memoria_activa' not in st.session_state:
    st.session_state.memoria_activa = False
    
# Inicializar variables de modelo y tipo
if 'modelo_seleccionado' not in st.session_state:
    st.session_state.modelo_seleccionado = "llama-3.3-70b-versatile"
    
if 'tipo_modelo' not in st.session_state:
    st.session_state.tipo_modelo = "Conversación"
    
if 'temperatura' not in st.session_state:
    st.session_state.temperatura = 0.4
    
if 'max_tokens' not in st.session_state:
    st.session_state.max_tokens = 1024
    
if 'system_prompt' not in st.session_state:
    st.session_state.system_prompt = "Eres un asistente de inteligencia artificial útil, claro y conciso. Tu objetivo es ayudar al usuario proporcionando respuestas precisas y fáciles de entender. Siempre responde en español, y si el usuario hace una pregunta ambigua, pedí amablemente más detalles."
    
if 'last_used_system_prompt' not in st.session_state:
    st.session_state.last_used_system_prompt = st.session_state.system_prompt
    
if 'confirmar_limpiar_chat' not in st.session_state:
    st.session_state.confirmar_limpiar_chat = False
    
# Variables para el modo configuración/chat
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = 'configuracion'  # Valores: 'configuracion' o 'chat'
    
if 'config_guardada' not in st.session_state:
    st.session_state.config_guardada = False
    
if 'confirmar_cambio_config' not in st.session_state:
    st.session_state.confirmar_cambio_config = False
    
if 'configuraciones_guardadas' not in st.session_state:
    st.session_state.configuraciones_guardadas = {}
    
if 'config_actual' not in st.session_state:
    st.session_state.config_actual = {
        'modelo_seleccionado': st.session_state.modelo_seleccionado,
        'tipo_modelo': st.session_state.tipo_modelo,
        'system_prompt': st.session_state.system_prompt,
        'temperatura': 0.4,
        'max_tokens': 1024
    }

# Función para limpiar la conversación
def clear_conversation():
    # Guardar system prompt actual 
    current_system_prompt = st.session_state.system_prompt
    
    # Limpiar mensajes y reiniciar el historial
    st.session_state.messages = []
    if pydantic_available and st.session_state.memoria_activa:
        st.session_state.pydantic_history = []
    if 'last_request_params' in st.session_state:
        del st.session_state['last_request_params']
    
    # Restaurar el system prompt
    st.session_state.system_prompt = current_system_prompt
    
    # Reiniciar confirmación de limpieza
    st.session_state.confirmar_limpiar_chat = False
    
    st.rerun()

# Función para nueva conversación
def new_conversation():
    # Limpiar mensajes y reiniciar el historial
    st.session_state.messages = []
    if pydantic_available and st.session_state.memoria_activa:
        st.session_state.pydantic_history = []
    if 'last_request_params' in st.session_state:
        del st.session_state['last_request_params']
    
    # Reiniciar el agente para que use el system prompt actual
    reset_pydantic_agent()
    
    st.rerun()

# Reiniciar agente pydantic cuando cambia la memoria
def reset_pydantic_agent():
    if "pydantic_agent" in st.session_state:
        st.session_state.pydantic_agent = None
    # Ya no eliminamos el historial al cambiar de modelo
    # if "pydantic_history" in st.session_state:
    #     st.session_state.pydantic_history = []
    
# Funciones para manejar cambios entre pantallas
def ir_a_configuracion():
    """Cambia a la pantalla de configuración"""
    st.session_state.pagina_actual = 'configuracion'
    
def ir_a_chat():
    """Cambia a la pantalla de chat"""
    st.session_state.pagina_actual = 'chat'
    
def guardar_configuracion():
    """Guarda la configuración actual y va a la pantalla de chat"""
    # Guardar la configuración actual
    st.session_state.config_actual = {
        'modelo_seleccionado': st.session_state.modelo_seleccionado,
        'tipo_modelo': st.session_state.tipo_modelo,
        'system_prompt': st.session_state.system_prompt,
        'temperatura': st.session_state.temperatura,
        'max_tokens': st.session_state.max_tokens
    }
    
    # Marcar configuración como guardada
    st.session_state.config_guardada = True
    
    # Reiniciar el agente para usar la nueva configuración
    reset_pydantic_agent()
    
    # Cambiar a la pantalla de chat
    ir_a_chat()
    
def confirmar_cambio_configuracion():
    """Pide confirmación para cambiar a configuración si hay mensajes"""
    if len(st.session_state.messages) > 0:
        st.session_state.confirmar_cambio_config = True
    else:
        ir_a_configuracion()
    
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

# Función para obtener la API key de Groq de forma segura
def get_groq_api_key():
    # Primero intentar obtenerla del archivo .env
    api_key = os.getenv("GROQ_API_KEY")
    
    # Si no está en el archivo .env, intentar obtenerla del entorno
    if not api_key:
        # Como último recurso, pedirla al usuario (solo en desarrollo)
        api_key = st.sidebar.text_input("Introduce tu API key de Groq:", type="password")
        if not api_key:
            st.sidebar.warning("Por favor, introduce tu API key de Groq para continuar.")
    
    return api_key

# Configuración del cliente de Groq
@st.cache_resource
def get_groq_client(api_key):
    if not api_key:
        return None
    return groq.Groq(api_key=api_key)

# Función para inicializar o actualizar el agente PydanticAI
def setup_pydantic_agent(api_key, model_name):
    if not pydantic_available:
        st.error("La biblioteca pydantic-ai no está instalada. La función de memoria no está disponible.")
        return None
        
    try:
        # Configurar el nombre del modelo para Groq
        agent_name = f"groq:{model_name}"
        
        # Configurar las variables de entorno para el agente
        os.environ["GROQ_API_KEY"] = api_key
        
        # Obtener el system prompt personalizado o usar el valor por defecto
        system_prompt = st.session_state.system_prompt
        
        # Crear un nuevo agente con el system prompt personalizado
        agent = Agent(
            agent_name,
            system_prompt=system_prompt
        )
        return agent
    except Exception as e:
        st.error(f"Error al inicializar el agente PydanticAI: {str(e)}")
        return None

# Sidebar - Selección de modelo
st.sidebar.title("Gestión de Conversaciones")

# Manejo de confirmación de limpieza de chat
if st.session_state.confirmar_limpiar_chat:
    # Mostrar mensaje de confirmación para limpiar chat
    st.sidebar.warning("⚠️ Se perderá todo el historial de la conversación. ¿Estás seguro?")
    
    # Botones uno debajo del otro
    if st.sidebar.button("✅ Sí, limpiar chat", key="confirmar_limpiar_btn", use_container_width=True):
        clear_conversation()
    
    if st.sidebar.button("❌ Cancelar", key="cancelar_limpiar_btn", use_container_width=True):
        st.session_state.confirmar_limpiar_chat = False
        st.rerun()

# Manejo de confirmación para cambio de configuración
elif st.session_state.confirmar_cambio_config:
    st.sidebar.warning("⚠️ Cambiar a configuración iniciará una nueva conversación. Se perderá el historial actual. ¿Estás seguro?")
    
    if st.sidebar.button("✅ Sí, ir a configuración", key="confirmar_config_btn", use_container_width=True):
        # Limpiar mensajes y reiniciar historial
        st.session_state.messages = []
        if pydantic_available and st.session_state.memoria_activa:
            st.session_state.pydantic_history = []
        st.session_state.confirmar_cambio_config = False
        ir_a_configuracion()
        st.rerun()
    
    if st.sidebar.button("❌ Cancelar", key="cancelar_config_btn", use_container_width=True):
        st.session_state.confirmar_cambio_config = False
        st.rerun()
        
# Si estamos en la página de chat, mostramos botones de gestión
elif st.session_state.pagina_actual == 'chat':
    # Definir las variables de sesión para control de eventos si no existen
    if 'nueva_conv_pendiente' not in st.session_state:
        st.session_state.nueva_conv_pendiente = False
    
    # Botones uno debajo del otro
    if st.sidebar.button("⚙️ Cambiar configuración", key="cambiar_config_btn", use_container_width=True):
        confirmar_cambio_configuracion()
        st.rerun()
    
    if st.sidebar.button("🔄 Nueva conversación", key="nueva_conv_btn", use_container_width=True):
        # Evitar st.rerun() en callbacks
        st.session_state.nueva_conv_pendiente = True
    
    st.sidebar.button("🗑️ Limpiar chat", key="limpiar_chat_btn", use_container_width=True, 
             on_click=lambda: setattr(st.session_state, 'confirmar_limpiar_chat', True))
            
    # Procesar acción pendiente si existe
    if st.session_state.nueva_conv_pendiente:
        st.session_state.nueva_conv_pendiente = False
        new_conversation()

# Control de flujo principal de la aplicación
if st.session_state.pagina_actual == 'configuracion':
    # Mostrar la página de configuración
    st.title("Configuración del Asistente IA")
    st.markdown("### Configura tu asistente antes de comenzar la conversación")
    
    # Sección de selección de modelo
    st.subheader("1. Selección de Modelo")
    
    # Selección de tipo de modelo (ahora como dropdown)
    tipo_modelo = st.selectbox(
        "Tipo de modelo:",
        list(MODELOS.keys()),
        index=list(MODELOS.keys()).index(st.session_state.tipo_modelo),
        key="tipo_modelo_select_config"
    )
    
    # Actualizar el tipo de modelo en la sesión
    if st.session_state.tipo_modelo != tipo_modelo:
        st.session_state.tipo_modelo = tipo_modelo
        # Establecer un modelo predeterminado para este tipo
        st.session_state.modelo_seleccionado = MODELOS[tipo_modelo][0]
        st.rerun()
    
    # Selección del modelo específico
    modelo_seleccionado = st.selectbox(
        "Modelo:",
        MODELOS[tipo_modelo],
        index=(MODELOS[tipo_modelo].index(st.session_state.modelo_seleccionado) 
               if st.session_state.modelo_seleccionado in MODELOS[tipo_modelo] 
               else 0)
    )
    
    # Actualizar el modelo seleccionado en la sesión
    if st.session_state.modelo_seleccionado != modelo_seleccionado:
        st.session_state.modelo_seleccionado = modelo_seleccionado
    
    # Información del modelo
    st.info(f"Modelo seleccionado: {modelo_seleccionado}")
    
    # Sección de parámetros
    st.subheader("2. Parámetros del Modelo")
    
    # Ajustes de temperatura y tokens
    col1, col2 = st.columns(2)
    with col1:
        temperatura = st.slider("Temperatura:", min_value=0.0, max_value=1.0, value=0.4, step=0.1)
        st.session_state.temperatura = temperatura
    
    with col2:
        max_tokens = st.slider("Tokens máximos:", min_value=256, max_value=4096, value=1024, step=128)
        st.session_state.max_tokens = max_tokens
    
    # Configuración del System Prompt
    st.subheader("3. Instrucciones para el Asistente (System Prompt)")
    
    # Definir algunos system prompts predefinidos como opciones
    system_prompts_predefinidos = {
        "Asistente predeterminado": "Eres un asistente de inteligencia artificial útil, claro y conciso. Tu objetivo es ayudar al usuario proporcionando respuestas precisas y fáciles de entender. Siempre responde en español, y si el usuario hace una pregunta ambigua, pedí amablemente más detalles.",
        "Experto técnico": "Eres un experto técnico con amplio conocimiento en programación, ciencias de la computación y tecnología. Proporciona explicaciones detalladas y precisas, utilizando terminología técnica cuando sea apropiado. Siempre responde en español.",
        "Profesor": "Eres un profesor paciente y didáctico. Tu objetivo es explicar conceptos de manera clara y educativa, adaptando tu nivel de explicación para que sea comprensible. Usa analogías y ejemplos para ilustrar ideas complejas. Siempre responde en español.",
        "Escritor creativo": "Eres un escritor creativo con un estilo vivaz e imaginativo. Puedes crear historias, poemas o textos creativos a partir de las peticiones del usuario. Usa un lenguaje rico y expresivo. Siempre responde en español.",
        "Asesor de negocios": "Eres un asesor de negocios experimentado. Proporciona consejos estratégicos, análisis de situaciones comerciales y recomendaciones basadas en buenas prácticas empresariales. Siempre responde en español."
    }
    
    # Dropdown para seleccionar un prompt predefinido
    prompt_predefinido = st.selectbox(
        "Seleccionar un perfil predefinido:",
        list(system_prompts_predefinidos.keys())
    )
    
    # Botón para cargar el prompt predefinido
    if st.button("Cargar perfil predefinido", use_container_width=True):
        st.session_state.system_prompt = system_prompts_predefinidos[prompt_predefinido]
        st.rerun()
    
    # Área de texto para editar el system prompt
    system_prompt = st.text_area(
        "Instrucciones personalizadas:",
        value=st.session_state.system_prompt,
        height=150,
        help="Define cómo debe comportarse el asistente en este chat."
    )
    st.session_state.system_prompt = system_prompt
    
    # Botón para guardar la configuración e ir al chat
    if st.button("💾 Guardar configuración e iniciar chat", use_container_width=True, type="primary"):
        guardar_configuracion()
        st.rerun()
        
elif st.session_state.pagina_actual == 'chat':
    # Verificar si hay configuración guardada
    if not st.session_state.config_guardada:
        st.warning("Por favor, configura tu asistente antes de comenzar la conversación.")
        if st.button("Ir a configuración"):
            ir_a_configuracion()
            st.rerun()
    else:
        # Mostrar la página de chat con la configuración actual
        st.title("Asistente IA con Groq 🤖")
        
        # Mostrar información de la configuración actual
        with st.expander("Ver configuración actual"):
            st.markdown(f"**Modelo:** {st.session_state.config_actual['tipo_modelo']} - {st.session_state.config_actual['modelo_seleccionado']}")
            st.markdown(f"**Temperatura:** {st.session_state.config_actual['temperatura']}")
            st.markdown(f"**Tokens máximos:** {st.session_state.config_actual['max_tokens']}")
            st.markdown("**System Prompt:**")
            st.code(st.session_state.config_actual['system_prompt'])
        
        # Actualizar el sidebar con información
        st.sidebar.markdown("---")
        st.sidebar.subheader("Configuración Actual")
        st.sidebar.info(f"**Modelo:** {st.session_state.config_actual['modelo_seleccionado']}")
        st.sidebar.caption(f"Temperatura: {st.session_state.config_actual['temperatura']}")
        st.sidebar.caption(f"Tokens máximos: {st.session_state.config_actual['max_tokens']}")
        
        # Mantenemos esta información en el sidebar
        st.sidebar.markdown("---")

# Mantenemos esta información en el sidebar
st.sidebar.markdown("---")

# Obtener API key y cliente
api_key = get_groq_api_key()
client = get_groq_client(api_key)

# Si estamos en la página de chat, inicializar el agente con la configuración guardada
if st.session_state.pagina_actual == 'chat' and st.session_state.config_guardada:
    # Establecer parámetros actuales para el chat
    tipo_modelo = st.session_state.config_actual['tipo_modelo']
    modelo_seleccionado = st.session_state.config_actual['modelo_seleccionado']
    temperatura = st.session_state.config_actual['temperatura']
    max_tokens = st.session_state.config_actual['max_tokens']
    
    # Establecer formato de razonamiento para modelos de razonamiento
    razonamiento_formato = None
    if tipo_modelo == "Razonamiento":
        razonamiento_formato = "raw"
    
    # Activar la memoria siempre si pydantic está disponible
    if pydantic_available and tipo_modelo in ["Conversación", "Razonamiento"]:
        # Siempre activar la memoria
        st.session_state.memoria_activa = True
        
        # Inicializar el agente PydanticAI si no existe
        if api_key and (st.session_state.pydantic_agent is None):
            st.session_state.pydantic_agent = setup_pydantic_agent(api_key, modelo_seleccionado)
            if st.session_state.pydantic_agent is None:
                st.session_state.memoria_activa = False

# Subida de archivos para modelos de audio
uploaded_file = None
if st.session_state.pagina_actual == 'chat' and st.session_state.config_guardada:
    if tipo_modelo == "Audio a Texto":
        uploaded_file = st.file_uploader("Sube un archivo de audio (mp3, wav, m4a, ogg)", type=["mp3", "wav", "m4a", "ogg"])
        if uploaded_file is not None:
            # Determinar el formato correcto para reproducir el audio
            file_type = uploaded_file.type.split('/')[1] if '/' in uploaded_file.type else 'audio/ogg'
            st.audio(uploaded_file, format=file_type)

# Procesar archivo de audio
def process_audio_file(file, model):
    try:
        # Leer el archivo y codificarlo en base64
        file_bytes = file.getvalue()
        
        # Determinar el tipo de archivo para casos donde no se detecta correctamente
        file_type = file.type
        if not file_type or '/' not in file_type:
            # Inferir tipo basado en la extensión
            if file.name.lower().endswith('.ogg'):
                file_type = 'audio/ogg'
            elif file.name.lower().endswith('.mp3'):
                file_type = 'audio/mpeg'
            elif file.name.lower().endswith('.wav'):
                file_type = 'audio/wav'
            elif file.name.lower().endswith('.m4a'):
                file_type = 'audio/m4a'
            else:
                file_type = 'audio/ogg'  # Default para archivos de WhatsApp
        
        # Crear la solicitud a la API
        transcription = client.audio.transcriptions.create(
            model=model,
            file=(file.name, file_bytes)
        )
        
        return transcription.text
    except Exception as e:
        return f"Error al procesar el audio: {str(e)}"

# Función para enviar mensajes a Groq y obtener respuestas con streaming
def get_response_streaming(messages: List[Dict[str, str]], placeholder):
    try:
        if not client:
            return "Por favor, configura tu API key de Groq en un archivo .env"
        
        # Preparar para streaming
        response_text = ""  # Para almacenar el texto puro sin HTML
        
        # Registrar valores para verificación
        st.session_state['last_request_params'] = {
            'temperatura': temperatura,
            'max_tokens': max_tokens,
            'modelo': modelo_seleccionado
        }
        
        # Configurar los parámetros base
        params = {
            "model": modelo_seleccionado,
            "messages": messages,
            "temperature": temperatura,
            "max_tokens": max_tokens,
            "top_p": 1,
            "stream": True,
            "stop": None,
        }
        
        # Añadir el formato de razonamiento si es un modelo de razonamiento
        if tipo_modelo == "Razonamiento" and razonamiento_formato:
            params["reasoning_format"] = razonamiento_formato
        
        # Crear la solicitud de chat
        completion = client.chat.completions.create(**params)
        
        # Procesar la respuesta en streaming
        for chunk in completion:
            content = chunk.choices[0].delta.content or ""
            if content:
                # Añadir al texto de respuesta puro (para almacenar)
                response_text += content
                
                # Escapar caracteres especiales HTML para la visualización
                safe_response = response_text.replace("<", "&lt;").replace(">", "&gt;")
                
                # Para modelos de razonamiento con formato "raw", formatear la salida
                if tipo_modelo == "Razonamiento" and razonamiento_formato == "raw":
                    # Comprobar si hay etiquetas think incluso cuando no estamos en modelo de razonamiento
                    # Buscar el patrón <think> y </think> en cualquier tipo de modelo
                    thinking_start = -1
                    thinking_end = -1
                    offset = 0
                    end_offset = 0
                    
                    # Buscar las etiquetas escapadas en la respuesta ya procesada
                    if "&lt;think&gt;" in safe_response and "&lt;/think&gt;" in safe_response:
                        thinking_start = safe_response.find("&lt;think&gt;")
                        thinking_end = safe_response.find("&lt;/think&gt;")
                        offset = 12
                        end_offset = 13
                    # Buscar las etiquetas sin escapar en el texto original
                    elif "<think>" in response_text and "</think>" in response_text:
                        # Trabajamos directamente con el texto sin escapar
                        thinking_start = response_text.find("<think>")
                        thinking_end = response_text.find("</think>")
                        
                        # Extraer pensamiento y respuesta del texto original sin escapar
                        thinking_content = response_text[thinking_start + 7:thinking_end].strip()
                        answer_content = response_text[thinking_end + 8:].strip()
                        
                        # Escapar para visualización
                        thinking_content = thinking_content.replace("<", "&lt;").replace(">", "&gt;")
                        answer_content = answer_content.replace("<", "&lt;").replace(">", "&gt;")
                        
                        # Si el answer_content está vacío, añadir un mensaje predeterminado
                        if not answer_content:
                            answer_content = "El modelo está proporcionando sólo su razonamiento. Puedes continuar la conversación."
                        
                        # Usar st.markdown directamente con el contenido ya procesado
                        placeholder.markdown(
                            f"""
                            <div class="chat-container assistant-message">
                                <div class="assistant-header">
                                    Asistente:
                                </div>
                                <div class="reasoning-section">
                                    <div class="thinking-title">Razonamiento:</div>
                                    <div class="reasoning-content">{thinking_content}</div>
                                </div>
                                <div class="chat-text">{answer_content}</div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        # Salimos de esta rama, ya procesamos el mensaje
                        return response_text
                    
                    if thinking_start != -1 and thinking_end != -1 and thinking_start < thinking_end:
                        thinking_content = safe_response[thinking_start + offset:thinking_end].strip()
                        answer_content = safe_response[thinking_end + end_offset:].strip()
                        
                        # Si el answer_content está vacío, añadir un mensaje predeterminado
                        if not answer_content:
                            answer_content = "El modelo está proporcionando sólo su razonamiento. Puedes continuar la conversación."
                        
                        # Usar st.markdown directamente en lugar de formatear HTML
                        placeholder.markdown(
                            f"""
                            <div class="chat-container assistant-message">
                                <div class="assistant-header">
                                    Asistente:
                                </div>
                                <div class="reasoning-section">
                                    <div class="thinking-title">Razonamiento:</div>
                                    <div class="reasoning-content">{thinking_content}</div>
                                </div>
                                <div class="chat-text">{answer_content}</div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                    else:
                        # Usar st.markdown directamente si no hay etiquetas think
                        placeholder.markdown(
                            f"""
                            <div class="chat-container assistant-message">
                                <div class="assistant-header">
                                    Asistente:
                                </div>
                                <div class="chat-text">{safe_response}</div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                else:
                    # Comprobar si hay etiquetas think incluso cuando no estamos en modelo de razonamiento
                    # Buscar el patrón <think> y </think> en cualquier tipo de modelo
                    thinking_start = -1
                    thinking_end = -1
                    offset = 0
                    end_offset = 0
                    
                    # Buscar las etiquetas escapadas en la respuesta ya procesada
                    if "&lt;think&gt;" in safe_response and "&lt;/think&gt;" in safe_response:
                        thinking_start = safe_response.find("&lt;think&gt;")
                        thinking_end = safe_response.find("&lt;/think&gt;")
                        offset = 12
                        end_offset = 13
                    # Buscar las etiquetas sin escapar en el texto original
                    elif "<think>" in response_text and "</think>" in response_text:
                        # Trabajamos directamente con el texto sin escapar
                        thinking_start = response_text.find("<think>")
                        thinking_end = response_text.find("</think>")
                        
                        # Extraer pensamiento y respuesta del texto original sin escapar
                        thinking_content = response_text[thinking_start + 7:thinking_end].strip()
                        answer_content = response_text[thinking_end + 8:].strip()
                        
                        # Escapar para visualización
                        thinking_content = thinking_content.replace("<", "&lt;").replace(">", "&gt;")
                        answer_content = answer_content.replace("<", "&lt;").replace(">", "&gt;")
                        
                        # Si el answer_content está vacío, añadir un mensaje predeterminado
                        if not answer_content:
                            answer_content = "El modelo está proporcionando sólo su razonamiento. Puedes continuar la conversación."
                        
                        # Usar st.markdown directamente con el contenido ya procesado
                        placeholder.markdown(
                            f"""
                            <div class="chat-container assistant-message">
                                <div class="assistant-header">
                                    Asistente:
                                </div>
                                <div class="reasoning-section">
                                    <div class="thinking-title">Razonamiento:</div>
                                    <div class="reasoning-content">{thinking_content}</div>
                                </div>
                                <div class="chat-text">{answer_content}</div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                        # Salimos de esta rama, ya procesamos el mensaje
                        return response_text
                    
                    if thinking_start != -1 and thinking_end != -1 and thinking_start < thinking_end:
                        thinking_content = safe_response[thinking_start + offset:thinking_end].strip()
                        answer_content = safe_response[thinking_end + end_offset:].strip()
                        
                        # Si el answer_content está vacío, añadir un mensaje predeterminado
                        if not answer_content:
                            answer_content = "El modelo está proporcionando sólo su razonamiento. Puedes continuar la conversación."
                        
                        # Usar st.markdown directamente en lugar de formatear HTML
                        placeholder.markdown(
                            f"""
                            <div class="chat-container assistant-message">
                                <div class="assistant-header">
                                    Asistente:
                                </div>
                                <div class="reasoning-section">
                                    <div class="thinking-title">Razonamiento:</div>
                                    <div class="reasoning-content">{thinking_content}</div>
                                </div>
                                <div class="chat-text">{answer_content}</div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
                    else:
                        # Usar st.markdown directamente si no hay etiquetas think
                        placeholder.markdown(
                            f"""
                            <div class="chat-container assistant-message">
                                <div class="assistant-header">
                                    Asistente:
                                </div>
                                <div class="chat-text">{safe_response}</div>
                            </div>
                            """, 
                            unsafe_allow_html=True
                        )
        
        # Limpiar posibles etiquetas HTML en la respuesta antes de devolverla
        html_patterns = [
            "</div>", 
            '<div class="chat-text">', 
            '<div class=', 
            '</div>', 
            '<span', 
            '</span>'
        ]
        
        # Verificar si hay etiquetas HTML incorrectas
        clean_response_text = response_text
        for pattern in html_patterns:
            if pattern in clean_response_text:
                clean_response_text = clean_response_text.replace(pattern, '')
                
        # Devolver el texto limpio
        return clean_response_text.strip()
    except Exception as e:
        return f"Error al comunicarse con Groq: {str(e)}"

# Función para obtener respuesta usando PydanticAI (con memoria)
def get_response_with_memory(user_prompt):
    try:
        # Verificar que pydantic está disponible
        if not pydantic_available:
            return "La función de memoria requiere la biblioteca 'pydantic-ai'"
        
        # Verificar si el system prompt ha cambiado desde el último uso
        system_prompt_changed = st.session_state.system_prompt != st.session_state.last_used_system_prompt
        
        # Verificar que el agente existe y asegurarse de que esté usando el system prompt actual
        if st.session_state.pydantic_agent is None or system_prompt_changed:
            st.session_state.pydantic_agent = setup_pydantic_agent(api_key, modelo_seleccionado)
            # Actualizar el último system prompt utilizado
            st.session_state.last_used_system_prompt = st.session_state.system_prompt
            
            if st.session_state.pydantic_agent is None:
                return "No se pudo inicializar el agente de memoria"
        
        # Ejecutar el agente con la historia de mensajes
        try:
            result = st.session_state.pydantic_agent.run_sync(
                user_prompt, 
                message_history=st.session_state.pydantic_history
            )
            
            # Actualizar la historia de mensajes - usar all_messages() en lugar de message_history
            st.session_state.pydantic_history = result.all_messages()
            
            return result.data
        except Exception as inner_e:
            # Si hay un error específico con la ejecución, intentar sin message_history
            st.warning(f"Ajustando configuración: {str(inner_e)}")
            result = st.session_state.pydantic_agent.run_sync(user_prompt)
            
            # Actualizar la historia de mensajes
            st.session_state.pydantic_history = result.all_messages()
            return result.data
            
    except Exception as e:
        return f"Error al utilizar la memoria: {str(e)}"

# Mostrar historial de mensajes
if st.session_state.pagina_actual == 'chat' and st.session_state.config_guardada:
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            # Escapar caracteres especiales HTML en el mensaje del usuario
            safe_content = content.replace("<", "&lt;").replace(">", "&gt;")
            
            st.markdown(f"""
            <div class="chat-container user-message">
                <div class="user-header">Tú:</div>
                <div class="chat-text">{safe_content}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Limpiar agresivamente cualquier etiqueta HTML incorrecta
            # Patrones comunes de etiquetas que podrían aparecer incorrectamente
            html_patterns = [
                "</div>", 
                '<div class="chat-text">', 
                '<div class=', 
                '</div>', 
                '<span', 
                '</span>'
            ]
            
            # Crear una copia para procesar
            clean_content = content
            
            # Verificar si el contenido ya tiene etiquetas HTML incorrectas
            has_html_tags = any(pattern in clean_content for pattern in html_patterns)
            
            # Limpiar todas las etiquetas HTML posibles
            if has_html_tags:
                for pattern in html_patterns:
                    clean_content = clean_content.replace(pattern, '')
                clean_content = clean_content.strip()
            
            # Escapar caracteres especiales HTML en el mensaje limpio
            safe_content = clean_content.replace("<", "&lt;").replace(">", "&gt;")
            
            # Para modelos de razonamiento con formato "raw", comprobar si hay etiquetas <think>
            if tipo_modelo == "Razonamiento" and ("<think>" in content or "&lt;think&gt;" in safe_content):
                # Buscar con y sin escape en HTML
                thinking_start = -1
                thinking_end = -1
                offset = 0
                end_offset = 0
                
                # Probar formato sin escapar
                if "<think>" in content:
                    thinking_start = content.find("<think>")
                    offset = 7
                    thinking_end = content.find("</think>")
                    end_offset = 8
                # Probar formato escapado
                elif "&lt;think&gt;" in safe_content:
                    thinking_start = safe_content.find("&lt;think&gt;")
                    offset = 12
                    thinking_end = safe_content.find("&lt;/think&gt;")
                    end_offset = 13
                
                if thinking_start != -1 and thinking_end != -1 and thinking_start < thinking_end:
                    # Extraer contenido basado en el formato detectado
                    if "<think>" in content:
                        thinking_content = content[thinking_start + offset:thinking_end].strip()
                        answer_content = content[thinking_end + end_offset:].strip()
                    else:
                        thinking_content = safe_content[thinking_start + offset:thinking_end].strip()
                        answer_content = safe_content[thinking_end + end_offset:].strip()
                    
                    # Limpiar y escapar el contenido de razonamiento
                    for pattern in html_patterns:
                        thinking_content = thinking_content.replace(pattern, '')
                        answer_content = answer_content.replace(pattern, '')
                    
                    # Escapar caracteres especiales HTML 
                    safe_thinking = thinking_content.replace("<", "&lt;").replace(">", "&gt;")
                    safe_answer = answer_content.replace("<", "&lt;").replace(">", "&gt;")
                    
                    # Si el answer_content está vacío, añadir un mensaje predeterminado
                    if not safe_answer:
                        safe_answer = "El modelo proporcionó sólo su razonamiento."
                    
                    st.markdown(f"""
                    <div class="chat-container assistant-message">
                        <div class="assistant-header">
                            Asistente:
                        </div>
                        <div class="reasoning-section">
                            <div class="thinking-title">Razonamiento:</div>
                            <div class="reasoning-content">{safe_thinking}</div>
                        </div>
                        <div class="chat-text">{safe_answer}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-container assistant-message">
                        <div class="assistant-header">
                            Asistente:
                        </div>
                        <div class="chat-text">{safe_content}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Check if content contains '<think>' pattern without specific model type
                # This handles cases where reasoning model messages are viewed in other model types
                thinking_start = -1
                thinking_end = -1
                
                # Check for unescaped think tags first
                if "<think>" in content and "</think>" in content:
                    thinking_start = content.find("<think>")
                    thinking_end = content.find("</think>")
                    offset = 7
                    end_offset = 8
                # Check for escaped think tags
                elif "&lt;think&gt;" in safe_content and "&lt;/think&gt;" in safe_content:
                    thinking_start = safe_content.find("&lt;think&gt;")
                    thinking_end = safe_content.find("&lt;/think&gt;")
                    offset = 12
                    end_offset = 13
                
                if thinking_start != -1 and thinking_end != -1 and thinking_start < thinking_end:
                    # Extract thinking content and answer content
                    thinking_content = ""
                    answer_content = ""
                    
                    if "<think>" in content:
                        thinking_content = content[thinking_start + offset:thinking_end].strip()
                        answer_content = content[thinking_end + end_offset:].strip()
                    else:
                        thinking_content = safe_content[thinking_start + offset:thinking_end].strip()
                        answer_content = safe_content[thinking_end + end_offset:].strip()
                    
                    # Clean and escape
                    for pattern in html_patterns:
                        thinking_content = thinking_content.replace(pattern, '')
                        answer_content = answer_content.replace(pattern, '')
                    
                    safe_thinking = thinking_content.replace("<", "&lt;").replace(">", "&gt;")
                    safe_answer = answer_content.replace("<", "&lt;").replace(">", "&gt;")
                    
                    if not safe_answer:
                        safe_answer = "El modelo proporcionó sólo su razonamiento."
                    
                    st.markdown(f"""
                    <div class="chat-container assistant-message">
                        <div class="assistant-header">
                            Asistente:
                        </div>
                        <div class="reasoning-section">
                            <div class="thinking-title">Razonamiento:</div>
                            <div class="reasoning-content">{safe_thinking}</div>
                        </div>
                        <div class="chat-text">{safe_answer}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-container assistant-message">
                        <div class="assistant-header">
                            Asistente:
                        </div>
                        <div class="chat-text">{safe_content}</div>
                    </div>
                    """, unsafe_allow_html=True)

# Input del usuario o procesamiento de audio
if st.session_state.pagina_actual == 'chat' and st.session_state.config_guardada:
    if tipo_modelo == "Audio a Texto" and uploaded_file is not None:
        if st.button("Transcribir Audio"):
            with st.spinner("Transcribiendo audio..."):
                transcription = process_audio_file(uploaded_file, modelo_seleccionado)
                
                # Agregar mensaje del usuario al historial
                archivo_mensaje = f"[Audio: {uploaded_file.name}]"
                st.session_state.messages.append({"role": "user", "content": archivo_mensaje})
                
                # Mostrar el mensaje del usuario
                st.markdown(f"""
                <div class="chat-container user-message">
                    <div class="user-header">Tú:</div>
                    <div class="chat-text">{archivo_mensaje}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Crear un placeholder para la respuesta
                response_placeholder = st.empty()
                
                # Mostrar la transcripción
                response_placeholder.markdown(f"""
                <div class="chat-container assistant-message">
                    <div class="assistant-header">Transcripción:</div>
                    <div class="chat-text">{transcription}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Guardar la respuesta completa en el historial
                st.session_state.messages.append({"role": "assistant", "content": transcription})
                
                # Limpiar el archivo subido
                uploaded_file = None
                st.rerun()
    else:
        # Input de texto normal para otros tipos de modelos
        prompt = st.chat_input("Escribe tu mensaje aquí...")
        
        # Procesar input del usuario
        if prompt and api_key:
            # Agregar mensaje del usuario al historial
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Mostrar el mensaje del usuario
            st.markdown(f"""
            <div class="chat-container user-message">
                <div class="user-header">Tú:</div>
                <div class="chat-text">{prompt}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Crear un placeholder para la respuesta en streaming
            response_placeholder = st.empty()
            
            # Usar pydantic sólo si la memoria está activada manualmente por el usuario
            if pydantic_available and st.session_state.memoria_activa and tipo_modelo in ["Conversación", "Razonamiento"]:
                # Obtener respuesta con memoria usando PydanticAI
                with st.spinner("Pensando..."):
                    response = get_response_with_memory(prompt)
                    
                    # Escapar caracteres especiales HTML en la respuesta
                    safe_response = response.replace("<", "&lt;").replace(">", "&gt;")
                    
                    # Formatear la respuesta
                    formatted_response = f"""
                    <div class="chat-container assistant-message">
                        <div class="assistant-header">
                            Asistente:
                        </div>
                        <div class="chat-text">{safe_response}</div>
                    </div>
                    """
                    
                    # Mostrar la respuesta
                    response_placeholder.markdown(formatted_response, unsafe_allow_html=True)
                    
                    # Guardar la respuesta en el historial
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response
                    })
            else:
                # Mostrar mensaje si pydantic no está disponible pero se intenta usar memoria
                if tipo_modelo in ["Conversación", "Razonamiento"] and st.session_state.memoria_activa and not pydantic_available:
                    st.warning("Se recomienda instalar pydantic-ai para una mejor experiencia con modelos de conversación y razonamiento.")
                
                # Preparar los mensajes para la API (sin memoria)
                messages_for_api = []
                
                # Añadir sistema como primer mensaje con el system prompt actualizado
                messages_for_api.append({
                    "role": "system", 
                    "content": st.session_state.system_prompt  # Usar el system prompt actualizado
                })
                
                # Añadir último mensaje del usuario
                last_user_msg = {"role": "user", "content": prompt}
                messages_for_api.append(last_user_msg)
                
                # Obtener respuesta del modelo con streaming (sin memoria)
                response = get_response_streaming(messages_for_api, response_placeholder)
                
                # Limpiar cualquier etiqueta HTML antes de guardar en el historial
                html_patterns = [
                    "</div>", 
                    '<div class="chat-text">', 
                    '<div class=', 
                    '</div>', 
                    '<span', 
                    '</span>'
                ]
                
                # Verificar si el contenido tiene etiquetas HTML incorrectas
                has_html_tags = any(pattern in response for pattern in html_patterns)
                
                # Limpiar la respuesta si es necesario
                clean_response = response
                if has_html_tags:
                    for pattern in html_patterns:
                        clean_response = clean_response.replace(pattern, '')
                
                # Eliminar espacios extras y asegurarse de que la respuesta esté limpia
                clean_response = clean_response.strip()
                
                # Guardar la respuesta limpia en el historial
                st.session_state.messages.append({"role": "assistant", "content": clean_response})

# Mostrar los últimos parámetros utilizados si existen
if 'last_request_params' in st.session_state:
    st.sidebar.markdown("---")
    st.sidebar.subheader("Última solicitud")
    st.sidebar.text(f"Modelo: {st.session_state['last_request_params']['modelo']}")
    st.sidebar.text(f"Temperatura: {st.session_state['last_request_params']['temperatura']}")
    st.sidebar.text(f"Tokens máximos: {st.session_state['last_request_params']['max_tokens']}")

# Información sobre cómo obtener API key de Groq
if st.session_state.pagina_actual == 'configuracion':
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### Configuración de la API key
    Para mayor seguridad, guarda tu API key en un archivo .env:
    1. Crea un archivo llamado `.env` en la raíz del proyecto
    2. Añade la línea `GROQ_API_KEY=tu_api_key_aquí`
    3. Este archivo está incluido en .gitignore y no se subirá a Github
    """) 