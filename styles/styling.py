"""
Estilos CSS para la interfaz de usuario de la aplicación.
"""

# Estilo CSS personalizado para toda la aplicación
CUSTOM_CSS = """
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
"""

def apply_custom_styles():
    """
    Aplica los estilos CSS personalizados a la aplicación Streamlit.
    """
    import streamlit as st
    st.markdown(f"<style>{CUSTOM_CSS}</style>", unsafe_allow_html=True) 