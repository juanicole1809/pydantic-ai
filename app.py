import streamlit as st
import groq
import os
from typing import List, Dict, Optional, Union
from dotenv import load_dotenv
import time
import base64
import importlib.util
from datetime import datetime

# Verificar si pydantic_ai está instalado
pydantic_available = importlib.util.find_spec("pydantic_ai") is not None

# Verificar si tavily-python está instalado
tavily_available = importlib.util.find_spec("tavily") is not None

# Verificar si duckduckgo-search está instalado
duckduckgo_available = importlib.util.find_spec("duckduckgo_search") is not None

# Verificar si nest_asyncio está instalado (para entornos Jupyter)
nest_asyncio_available = importlib.util.find_spec("nest_asyncio") is not None

# Importar pydantic_ai y nest_asyncio si están disponibles
if pydantic_available:
    try:
        from pydantic_ai import Agent, RunContext
        from pydantic import BaseModel
        # No importamos directamente duckduckgo_search_tool debido a incompatibilidad con Python 3.9
        # Usaremos nuestra propia implementación para búsqueda DuckDuckGo
        # Aplicar nest_asyncio si está disponible (para compatibilidad con Jupyter)
        if nest_asyncio_available:
            import nest_asyncio
            nest_asyncio.apply()
    except ImportError:
        pydantic_available = False

# Importar tavily-python si está disponible
if tavily_available:
    try:
        from tavily import TavilyClient
    except ImportError:
        tavily_available = False

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

# Variable para activar/desactivar herramientas
if 'usar_tavily' not in st.session_state:
    st.session_state.usar_tavily = True
    
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
    st.session_state.system_prompt = "Eres un asistente de inteligencia artificial útil, claro y conciso. Tu objetivo es ayudar al usuario proporcionando respuestas precisas y fáciles de entender. Siempre responde en español, y si el usuario hace una pregunta ambigua, pide amablemente más detalles."
    
if 'last_used_system_prompt' not in st.session_state:
    st.session_state.last_used_system_prompt = st.session_state.system_prompt
    
if 'confirmar_limpiar_chat' not in st.session_state:
    st.session_state.confirmar_limpiar_chat = False
    
if 'force_rerun' not in st.session_state:
    st.session_state.force_rerun = False
    
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
        'max_tokens': 1024,
        'usar_tavily': True
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
    # Guardar la configuración anterior para comparar
    config_anterior = st.session_state.config_actual.copy() if 'config_actual' in st.session_state else None
    cambio_modo = False
    
    # Verificar si se cambió el tipo de modelo
    if config_anterior and config_anterior['tipo_modelo'] != st.session_state.tipo_modelo:
        cambio_modo = True
    
    # Guardar la configuración actual
    st.session_state.config_actual = {
        'modelo_seleccionado': st.session_state.modelo_seleccionado,
        'tipo_modelo': st.session_state.tipo_modelo,
        'system_prompt': st.session_state.system_prompt,
        'temperatura': st.session_state.temperatura,
        'max_tokens': st.session_state.max_tokens,
        'usar_tavily': st.session_state.usar_tavily
    }
    
    # Actualizar las variables globales para que se apliquen de inmediato
    global tipo_modelo, modelo_seleccionado, temperatura, max_tokens, razonamiento_formato
    tipo_modelo = st.session_state.tipo_modelo
    modelo_seleccionado = st.session_state.modelo_seleccionado
    temperatura = st.session_state.temperatura
    max_tokens = st.session_state.max_tokens
    
    # Establecer formato de razonamiento para modelos de razonamiento
    razonamiento_formato = None
    if tipo_modelo == "Razonamiento":
        razonamiento_formato = "raw"
        # Si cambiamos a modo razonamiento, forzar recarga completa 
        if cambio_modo:
            st.session_state.force_rerun = True
    
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

# Función para obtener la API key de Tavily de forma segura
def get_tavily_api_key():
    # Intentar obtenerla del archivo .env
    api_key = os.getenv("TAVILY_API_KEY")
    
    # Si no está en el archivo .env, mostrar mensaje informativo
    if not api_key and tavily_available:
        st.sidebar.info("Para habilitar la búsqueda web, añade TAVILY_API_KEY en tu archivo .env")
    
    return api_key

# Función para buscar en internet con Tavily Search API
def buscar_en_internet(query: str, num_results: int = 5) -> str:
    """
    Realiza una búsqueda en internet utilizando Tavily Search API.
    
    Args:
        query (str): La consulta a buscar
        num_results (int): Número de resultados a devolver (default: 5)
        
    Returns:
        str: Resultados de la búsqueda formateados como texto
    """
    try:
        if not tavily_available:
            return "Error: La biblioteca tavily-python no está instalada. Instálala con 'pip install tavily-python'."
        
        api_key = get_tavily_api_key()
        if not api_key:
            return "Error: No se encontró la API key de Tavily. Configura TAVILY_API_KEY en el archivo .env."
        
        # Inicializa el cliente de Tavily
        client = TavilyClient(api_key=api_key)
        
        # Realiza la búsqueda
        search_results = client.search(query=query, max_results=num_results, search_depth="advanced", include_answer=True)
        
        # Formatea los resultados como texto
        results_text = f"Resultados de búsqueda para: '{query}'\n\n"
        
        # Añadir respuesta generada por Tavily si está disponible
        if "answer" in search_results and search_results["answer"]:
            results_text += f"RESPUESTA GENERADA:\n{search_results['answer']}\n\n"
        
        # Añadir resultados de la búsqueda
        if "results" in search_results and search_results["results"]:
            results_text += "FUENTES:\n"
            for i, result in enumerate(search_results["results"][:num_results], 1):
                title = result.get("title", "Sin título")
                url = result.get("url", "Sin URL")
                content = result.get("content", "Sin contenido")
                score = result.get("score", 0)
                
                results_text += f"{i}. {title}\n   URL: {url}\n   Relevancia: {score:.2f}\n   {content[:200]}...\n\n"
        
        # Registrar la búsqueda para depuración
        st.session_state["ultima_busqueda"] = {
            "query": query,
            "resultados": results_text
        }
        
        return results_text
    except Exception as e:
        error_msg = f"Error al realizar la búsqueda: {str(e)}"
        st.session_state["ultima_busqueda_error"] = error_msg
        return error_msg

# Función para buscar en DuckDuckGo
def buscar_en_duckduckgo(query: str, num_results: int = 5) -> str:
    """
    Realiza una búsqueda en internet utilizando DuckDuckGo Search.
    
    Args:
        query (str): La consulta a buscar
        num_results (int): Número de resultados a devolver (default: 5)
        
    Returns:
        str: Resultados de la búsqueda formateados como texto
    """
    try:
        if not duckduckgo_available:
            return "Error: La biblioteca duckduckgo-search no está instalada. Instálala con 'pip install duckduckgo-search'."
        
        # Importamos aquí para evitar problemas de importación si no está disponible
        from duckduckgo_search import DDGS
        
        # Inicializa el cliente de DuckDuckGo
        ddgs = DDGS()
        
        # Realiza la búsqueda
        search_results = list(ddgs.text(query, max_results=num_results))
        
        # Formatea los resultados como texto
        results_text = f"Resultados de búsqueda en DuckDuckGo para: '{query}'\n\n"
        
        # Añadir resultados de la búsqueda
        if search_results:
            for i, result in enumerate(search_results, 1):
                title = result.get("title", "Sin título")
                url = result.get("href", "Sin URL")
                content = result.get("body", "Sin contenido")
                
                results_text += f"{i}. {title}\n   URL: {url}\n   {content[:200]}...\n\n"
        else:
            results_text += "No se encontraron resultados para esta consulta.\n"
        
        # Registrar la búsqueda para depuración
        st.session_state["ultima_busqueda_ddg"] = {
            "query": query,
            "resultados": results_text
        }
        
        return results_text
    except Exception as e:
        error_msg = f"Error al realizar la búsqueda en DuckDuckGo: {str(e)}"
        st.session_state["ultima_busqueda_ddg_error"] = error_msg
        return error_msg

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
        
        # Obtener la API key de Tavily
        tavily_api_key = get_tavily_api_key()
        
        # Obtener el system prompt personalizado del usuario
        base_system_prompt = st.session_state.system_prompt
        
        # Obtener la fecha y hora actuales
        now = datetime.now()
        date_time_str = now.strftime("%d/%m/%Y %H:%M:%S")
        
        # Añadir información sobre fecha y hora actuales
        system_prompt = f"{base_system_prompt} La fecha y hora actuales son: {date_time_str}."
        
        # Añadir información sobre la búsqueda web solo si está habilitada
        if st.session_state.usar_tavily and tavily_api_key and tavily_available:
            # Añadir instrucción sobre el uso de la herramienta de búsqueda web
            if not "búsqueda web" in system_prompt.lower() and not "tavily" in system_prompt.lower():
                system_prompt += " Cuando el usuario solicite información actualizada o sobre eventos recientes, utiliza la herramienta de búsqueda web de Tavily para obtener y proporcionar información en tiempo real de fuentes confiables."
        
        # Guardar el system prompt realmente usado
        st.session_state.system_prompt_actual = system_prompt
        
        # Crear un nuevo agente con el system prompt actualizado
        agent = Agent(
            agent_name,
            system_prompt=system_prompt
        )
        
        # Registrar la herramienta de búsqueda web solo si está habilitada y disponible
        if st.session_state.usar_tavily and tavily_api_key and tavily_available:
            @agent.tool
            def search_web(ctx: RunContext[str], query: str, num_results: int = 5) -> str:
                """
                Busca información en internet utilizando Tavily Search.
                
                Args:
                    query (str): La consulta a buscar en internet
                    num_results (int, optional): Número de resultados a mostrar. Default: 5
                    
                Returns:
                    str: Resultados de la búsqueda formateados
                """
                resultado = buscar_en_internet(query, num_results)
                # Registrar el uso de la herramienta para verificación
                if "herramientas_usadas" not in st.session_state:
                    st.session_state.herramientas_usadas = []
                st.session_state.herramientas_usadas.append({
                    "tool": "search_web", 
                    "query": query,
                    "resultado_corto": resultado[:100] + "..." if len(resultado) > 100 else resultado
                })
                return resultado
        
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
    
    # Área de texto para editar el system prompt
    system_prompt = st.text_area(
        "Instrucciones personalizadas:",
        value=st.session_state.system_prompt,
        height=150,
        help="Define cómo debe comportarse el asistente en este chat."
    )
    st.session_state.system_prompt = system_prompt
    
    # Sección de herramientas
    st.subheader("4. Herramientas")
    
    # Información sobre Tavily Search
    tavily_status = "✅ Configurada" if get_tavily_api_key() else "❌ No configurada (añade TAVILY_API_KEY en .env)"
    
    # Checkbox para activar/desactivar Tavily
    st.session_state.usar_tavily = st.checkbox(
        f"Habilitar búsqueda web con Tavily ({tavily_status})",
        value=st.session_state.usar_tavily,
        help="Permite que el asistente busque información actualizada en internet"
    )
    
    if not get_tavily_api_key() and st.session_state.usar_tavily:
        st.info("Para usar la búsqueda web, añade TAVILY_API_KEY en tu archivo .env")
    
    # Botón para restablecer valores predeterminados
    if st.button("🔄 Restablecer valores predeterminados", use_container_width=True):
        # Establecer valores predeterminados
        st.session_state.tipo_modelo = "Conversación"
        st.session_state.modelo_seleccionado = "llama-3.3-70b-versatile"
        st.session_state.temperatura = 0.9
        st.session_state.max_tokens = 1024
        st.session_state.system_prompt = "Eres un asistente de inteligencia artificial útil, claro y conciso. Tu objetivo es ayudar al usuario proporcionando respuestas precisas y fáciles de entender. Siempre responde en español, y si el usuario hace una pregunta ambigua, pide amablemente más detalles."
        st.session_state.usar_tavily = True
        st.rerun()
    
    # Botón para guardar la configuración e ir al chat
    if st.button("💾 Guardar configuración e iniciar chat", use_container_width=True, type="primary"):
        guardar_configuracion()
        
        # Si necesitamos forzar una recarga
        if "force_rerun" in st.session_state and st.session_state.force_rerun:
            st.session_state.force_rerun = False
            st.rerun()
        else:
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
        
        # Actualizar el sidebar con información
        st.sidebar.markdown("---")
        st.sidebar.subheader("Configuración Actual")
        st.sidebar.info(f"**Modelo:** {st.session_state.config_actual['tipo_modelo']} - {st.session_state.config_actual['modelo_seleccionado']}")
        st.sidebar.caption(f"Temperatura: {st.session_state.config_actual['temperatura']}")
        st.sidebar.caption(f"Tokens máximos: {st.session_state.config_actual['max_tokens']}")
        
        # Agregar el system prompt en un acordeón en el sidebar con mejor estilo
        with st.sidebar.expander("Ver System Prompt actual", expanded=False):
            # Mostrar el system prompt real que se está utilizando
            prompt_to_display = st.session_state.system_prompt_actual if 'system_prompt_actual' in st.session_state else st.session_state.config_actual['system_prompt']
            
            st.markdown(
                f"""<div style="background-color: var(--secondary-background-color); 
                           color: var(--text-color); 
                           font-family: monospace; 
                           padding: 10px; 
                           border-radius: 5px; 
                           font-size: 12px; 
                           word-wrap: break-word; 
                           white-space: pre-wrap;
                           overflow-wrap: break-word;
                           border: 1px solid rgba(128, 128, 128, 0.2);">{prompt_to_display}</div>""", 
                unsafe_allow_html=True
            )
        
        # Mostrar estado de herramientas en el sidebar
        st.sidebar.caption(f"Búsqueda web: {'Activada' if st.session_state.config_actual.get('usar_tavily', False) else 'Desactivada'}")
        
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
    
    # Asegurar que los valores en la sesión están sincronizados
    st.session_state.tipo_modelo = tipo_modelo
    st.session_state.modelo_seleccionado = modelo_seleccionado
    
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

# Función para limpiar y procesar etiquetas <think> en un mensaje
def procesar_mensaje_razonamiento(contenido):
    """
    Procesa un mensaje para detectar y formatear etiquetas <think>
    Retorna el contenido procesado
    """
    # Limpiar agresivamente cualquier etiqueta HTML incorrecta
    html_patterns = [
        "</div>", 
        '<div class="chat-text">', 
        '<div class=', 
        '</div>', 
        '<span', 
        '</span>'
    ]
    
    # Crear una copia para procesar
    clean_content = contenido
    
    # Verificar si el contenido ya tiene etiquetas HTML incorrectas
    has_html_tags = any(pattern in clean_content for pattern in html_patterns)
    
    # Limpiar todas las etiquetas HTML posibles
    if has_html_tags:
        for pattern in html_patterns:
            clean_content = clean_content.replace(pattern, '')
        clean_content = clean_content.strip()
    
    # Verificar si hay etiquetas <think>
    has_thinking_tags = False
    thinking_content = ""
    answer_content = ""
    
    # Probar formato sin escapar
    if "<think>" in clean_content and "</think>" in clean_content:
        has_thinking_tags = True
        thinking_start = clean_content.find("<think>")
        thinking_end = clean_content.find("</think>")
        
        thinking_content = clean_content[thinking_start + 7:thinking_end].strip()
        answer_content = clean_content[thinking_end + 8:].strip()
        
        # Preservar el formato para visualización posterior
        return clean_content
        
    return clean_content

# Función para enviar mensajes a Groq y obtener respuestas con streaming
def get_response_streaming(messages: List[Dict[str, str]], placeholder, razonamiento_formato=None, tipo_modelo_actual=None):
    try:
        if not client:
            return "Por favor, configura tu API key de Groq en un archivo .env"
        
        # Usar el tipo de modelo pasado como parámetro, o el global si no se proporciona
        tipo_modelo_actual = tipo_modelo_actual or tipo_modelo
        
        # Preparar para streaming
        response_text = ""  # Para almacenar el texto puro sin HTML
        
        # Actualizar el primer mensaje (system) con la fecha y hora actuales
        from datetime import datetime
        now = datetime.now()
        date_time_str = now.strftime("%d/%m/%Y %H:%M:%S")
        
        # Asegurarse de que hay un mensaje de sistema
        if messages and messages[0]['role'] == 'system':
            # Añadir información de fecha y hora al mensaje del sistema
            base_system_content = messages[0]['content']
            messages[0]['content'] = f"{base_system_content} La fecha y hora actuales son: {date_time_str}."
        
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
        if tipo_modelo_actual == "Razonamiento" and razonamiento_formato:
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
                if tipo_modelo_actual == "Razonamiento" and razonamiento_formato == "raw":
                    # Comprobar si hay etiquetas think incluso cuando no estamos en modelo de razonamiento
                    # Buscar el patrón <think> y </think> en cualquier tipo de modelo
                    thinking_start = -1
                    thinking_end = -1
                    has_thinking_tags = False
                    thinking_content = ""
                    answer_content = ""
                    
                    # Buscar las etiquetas sin escapar en el texto original
                    if "<think>" in response_text and "</think>" in response_text:
                        has_thinking_tags = True
                        thinking_start = response_text.find("<think>")
                        thinking_end = response_text.find("</think>")
                        
                        # Extraer pensamiento y respuesta del texto original sin escapar
                        thinking_content = response_text[thinking_start + 7:thinking_end].strip()
                        answer_content = response_text[thinking_end + 8:].strip()
                    # Buscar las etiquetas escapadas en la respuesta ya procesada
                    elif "&lt;think&gt;" in safe_response and "&lt;/think&gt;" in safe_response:
                        has_thinking_tags = True
                        thinking_start = safe_response.find("&lt;think&gt;")
                        thinking_end = safe_response.find("&lt;/think&gt;")
                        
                        # Extraer contenido
                        thinking_content = safe_response[thinking_start + 12:thinking_end].strip()
                        answer_content = safe_response[thinking_end + 13:].strip()
                    
                    # Si se encontraron etiquetas de pensamiento, mostrar razonamiento y respuesta
                    if has_thinking_tags:
                        # Escapar para visualización si no estaba ya escapado
                        if "<" in thinking_content or ">" in thinking_content:
                            safe_thinking = thinking_content.replace("<", "&lt;").replace(">", "&gt;")
                        else:
                            safe_thinking = thinking_content
                        
                        if "<" in answer_content or ">" in answer_content:
                            safe_answer = answer_content.replace("<", "&lt;").replace(">", "&gt;")
                        else:
                            safe_answer = answer_content
                        
                        # Si el answer_content está vacío, añadir un mensaje predeterminado
                        if not safe_answer:
                            safe_answer = "El modelo proporcionó sólo su razonamiento."
                        
                        placeholder.markdown(
                            f"""
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
                            """, 
                            unsafe_allow_html=True
                        )
                        # Salimos de esta rama, ya procesamos el mensaje
                        return response_text
                    else:
                        # No hay etiquetas de razonamiento, mostrar el mensaje normal
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
                    thinking_start = -1
                    thinking_end = -1
                    has_thinking_tags = False
                    thinking_content = ""
                    answer_content = ""
                    
                    # Buscar las etiquetas sin escapar en el texto original
                    if "<think>" in response_text and "</think>" in response_text:
                        has_thinking_tags = True
                        thinking_start = response_text.find("<think>")
                        thinking_end = response_text.find("</think>")
                        
                        # Extraer pensamiento y respuesta del texto original sin escapar
                        thinking_content = response_text[thinking_start + 7:thinking_end].strip()
                        answer_content = response_text[thinking_end + 8:].strip()
                    # Buscar las etiquetas escapadas en la respuesta ya procesada
                    elif "&lt;think&gt;" in safe_response and "&lt;/think&gt;" in safe_response:
                        has_thinking_tags = True
                        thinking_start = safe_response.find("&lt;think&gt;")
                        thinking_end = safe_response.find("&lt;/think&gt;")
                        
                        # Extraer contenido
                        thinking_content = safe_response[thinking_start + 12:thinking_end].strip()
                        answer_content = safe_response[thinking_end + 13:].strip()
                    
                    # Si se encontraron etiquetas de pensamiento, mostrar razonamiento y respuesta
                    if has_thinking_tags:
                        # Escapar para visualización si no estaba ya escapado
                        if "<" in thinking_content or ">" in thinking_content:
                            safe_thinking = thinking_content.replace("<", "&lt;").replace(">", "&gt;")
                        else:
                            safe_thinking = thinking_content
                        
                        if "<" in answer_content or ">" in answer_content:
                            safe_answer = answer_content.replace("<", "&lt;").replace(">", "&gt;")
                        else:
                            safe_answer = answer_content
                        
                        # Si el answer_content está vacío, añadir un mensaje predeterminado
                        if not safe_answer:
                            safe_answer = "El modelo proporcionó sólo su razonamiento."
                        
                        placeholder.markdown(
                            f"""
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
                            """, 
                            unsafe_allow_html=True
                        )
                        return response_text
                    else:
                        # No hay etiquetas de razonamiento, mostrar el mensaje normal
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
        
        # Actualizar la fecha y hora en el system prompt
        from datetime import datetime
        now = datetime.now()
        date_time_str = now.strftime("%d/%m/%Y %H:%M:%S")
        
        # Verificar si el system prompt ha cambiado desde el último uso
        system_prompt_changed = st.session_state.system_prompt != st.session_state.last_used_system_prompt
        
        # Verificar que el agente existe y asegurarse de que esté usando el system prompt actual
        if st.session_state.pydantic_agent is None or system_prompt_changed:
            st.session_state.pydantic_agent = setup_pydantic_agent(api_key, modelo_seleccionado)
            # Actualizar el último system prompt utilizado
            st.session_state.last_used_system_prompt = st.session_state.system_prompt
            
            if st.session_state.pydantic_agent is None:
                return "No se pudo inicializar el agente de memoria"
        else:
            # Si el agente ya existe, solo actualizamos la fecha y hora
            # Obtener el system prompt base (sin fecha/hora ni instrucciones de Tavily)
            base_system_prompt = st.session_state.system_prompt
            
            # Reconstruir el system prompt con la fecha y hora actualizadas
            system_prompt = f"{base_system_prompt} La fecha y hora actuales son: {date_time_str}."
            
            # Añadir información sobre la búsqueda web si está habilitada
            if st.session_state.usar_tavily and get_tavily_api_key() and tavily_available:
                if not "búsqueda web" in system_prompt.lower() and not "tavily" in system_prompt.lower():
                    system_prompt += " Cuando el usuario solicite información actualizada o sobre eventos recientes, utiliza la herramienta de búsqueda web de Tavily para obtener y proporcionar información en tiempo real de fuentes confiables."
            
            # Actualizar el system prompt del agente
            st.session_state.pydantic_agent._system_prompt = system_prompt
            
            # Guardar el system prompt realmente usado
            st.session_state.system_prompt_actual = system_prompt
        
        # Ejecutar el agente con la historia de mensajes
        try:
            # Placeholder para mostrar información sobre herramientas
            tools_placeholder = st.empty()
            tools_placeholder.markdown("⏳ Procesando tu consulta...")
            
            # Limpiar registro de herramientas utilizadas para esta consulta
            if "herramientas_usadas" in st.session_state:
                st.session_state.herramientas_usadas = []
            
            # Ejecutar el agente con la historia de mensajes y mostrar el proceso
            st.session_state.debug_info = []
            
            # Configurar el callback para visualizar el proceso
            def tool_callback(event_type, event_data):
                if event_type == "tool_start":
                    tool_info = f"Usando herramienta: {event_data.get('name', 'desconocida')}, Argumentos: {event_data.get('input')}"
                    st.session_state.debug_info.append(tool_info)
                    # Actualizar el placeholder para mostrar la herramienta en uso
                    tools_placeholder.markdown(f"⚙️ {tool_info}...")
                elif event_type == "tool_end":
                    if "result" in event_data:
                        result_summary = event_data["result"][:500] + "..." if len(event_data["result"]) > 500 else event_data["result"]
                        tool_result = f"Resultado: {result_summary}"
                        st.session_state.debug_info.append(tool_result)
            
            # Ejecutar el agente con callback
            try:
                result = st.session_state.pydantic_agent.run_sync(
                    user_prompt, 
                    message_history=st.session_state.pydantic_history,
                    callbacks=[tool_callback]
                )
            except TypeError:
                # Si el callback causa problemas, ejecutar sin él
                result = st.session_state.pydantic_agent.run_sync(
                    user_prompt, 
                    message_history=st.session_state.pydantic_history
                )
            
            # Actualizar la historia de mensajes
            st.session_state.pydantic_history = result.all_messages()
            
            # Verificar si se utilizaron herramientas
            response_data = result.data
            
            # Verificar el registro de herramientas utilizadas
            if "herramientas_usadas" in st.session_state and st.session_state.herramientas_usadas:
                # Construir un razonamiento con los resultados de Tavily
                thinking_content = "Consultando fuentes en tiempo real...\n\n"
                
                for tool_use in st.session_state.herramientas_usadas:
                    if tool_use["tool"] == "search_web":
                        thinking_content += f"Búsqueda web para: '{tool_use['query']}'\n\n"
                        
                        # Obtener los resultados completos de la última búsqueda
                        if "ultima_busqueda" in st.session_state:
                            thinking_content += st.session_state["ultima_busqueda"]["resultados"]
                
                # Formatear la respuesta con el formato de pensamiento para que se muestre en la UI
                # Verificar si la respuesta ya contiene etiquetas de función
                if "<function=" in response_data:
                    # Eliminar las etiquetas de función que están apareciendo en la UI
                    response_data = response_data.replace("<function=", "").replace("</function>", "")
                    # Si hay información JSON, intentamos limpiarla también
                    import re
                    response_data = re.sub(r'\{.*?\}', '', response_data)
                
                response_data = f"<think>{thinking_content}</think>{response_data}"
            
            # Limpiar el placeholder de herramientas
            tools_placeholder.empty()
            
            # Devolver los datos procesados
            return response_data
            
        except Exception as inner_e:
            # Si hay un error específico con la ejecución
            st.warning(f"Ajustando configuración: {str(inner_e)}")
            result = st.session_state.pydantic_agent.run_sync(user_prompt)
            
            # Actualizar la historia de mensajes
            st.session_state.pydantic_history = result.all_messages()
            return result.data
            
    except Exception as e:
        return f"Error al utilizar la memoria: {str(e)}"

# Mostrar historial de mensajes
if st.session_state.pagina_actual == 'chat' and st.session_state.config_guardada:
    # Utilizar tipo_modelo de la configuración actual
    current_tipo_modelo = st.session_state.config_actual['tipo_modelo']
    
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
            
            # Siempre buscar etiquetas <think> independientemente del tipo de modelo
            # Buscar con y sin escape en HTML
            thinking_start = -1
            thinking_end = -1
            has_thinking_tags = False
            thinking_content = ""
            answer_content = ""
            
            # Probar formato sin escapar en el contenido limpio pero sin escapar
            if "<think>" in clean_content and "</think>" in clean_content:
                has_thinking_tags = True
                thinking_start = clean_content.find("<think>")
                thinking_end = clean_content.find("</think>")
                
                # Extraer contenido
                thinking_content = clean_content[thinking_start + 7:thinking_end].strip()
                answer_content = clean_content[thinking_end + 8:].strip()
            # Probar formato escapado como respaldo
            elif "&lt;think&gt;" in safe_content and "&lt;/think&gt;" in safe_content:
                has_thinking_tags = True
                thinking_start = safe_content.find("&lt;think&gt;")
                thinking_end = safe_content.find("&lt;/think&gt;")
                
                # Extraer contenido
                thinking_content = safe_content[thinking_start + 12:thinking_end].strip()
                answer_content = safe_content[thinking_end + 13:].strip()
            
            # Si se encontraron etiquetas de pensamiento, mostrar razonamiento y respuesta
            if has_thinking_tags:
                # Escapar para visualización si no estaba ya escapado
                if "<" in thinking_content or ">" in thinking_content:
                    safe_thinking = thinking_content.replace("<", "&lt;").replace(">", "&gt;")
                else:
                    safe_thinking = thinking_content
                    
                if "<" in answer_content or ">" in answer_content:
                    safe_answer = answer_content.replace("<", "&lt;").replace(">", "&gt;")
                else:
                    safe_answer = answer_content
                
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
                # No hay etiquetas de razonamiento, mostrar el mensaje normal
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
    # Utilizar tipo_modelo de la configuración actual
    current_tipo_modelo = st.session_state.config_actual['tipo_modelo']
    
    if current_tipo_modelo == "Audio a Texto" and uploaded_file is not None:
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
            if pydantic_available and st.session_state.memoria_activa and current_tipo_modelo in ["Conversación", "Razonamiento"]:
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
                    
                    # Procesar el mensaje para asegurar un formato correcto de etiquetas <think>
                    processed_response = procesar_mensaje_razonamiento(response)
                    
                    # Guardar la respuesta procesada en el historial
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": processed_response
                    })
            else:
                # Mostrar mensaje si pydantic no está disponible pero se intenta usar memoria
                if current_tipo_modelo in ["Conversación", "Razonamiento"] and st.session_state.memoria_activa and not pydantic_available:
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
                
                # Establecer formato de razonamiento según el tipo de modelo actual
                current_razonamiento_formato = None
                if current_tipo_modelo == "Razonamiento":
                    current_razonamiento_formato = "raw"
                
                # Obtener respuesta del modelo con streaming (sin memoria)
                response = get_response_streaming(messages_for_api, response_placeholder, current_razonamiento_formato, current_tipo_modelo)
                
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
                
                # Procesar el mensaje para asegurar un formato correcto de etiquetas <think>
                processed_response = procesar_mensaje_razonamiento(clean_response)
                
                # Guardar la respuesta procesada en el historial
                st.session_state.messages.append({"role": "assistant", "content": processed_response})

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
    
    # Añadir información sobre Tavily Search API
    if tavily_available:
        st.sidebar.markdown("---")
        st.sidebar.markdown("""
        ### Habilitar búsqueda web (opcional)
        Para permitir que el asistente busque información en internet:
        1. Obtén tu API key gratuita en [Tavily Search API](https://tavily.com)
        2. Añade la línea `TAVILY_API_KEY=tu_api_key_aquí` en tu archivo `.env`
        3. La herramienta de búsqueda se activará automáticamente
        
        Con esta funcionalidad, el asistente podrá buscar información actualizada en tiempo real cuando sea necesario.
        """, unsafe_allow_html=True) 