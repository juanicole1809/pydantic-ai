"""
Módulo para la configuración y manejo del cliente Groq.
Incluye funciones para obtener la API key y procesar archivos de audio.
"""

import os
import groq
import streamlit as st
from typing import Optional

@st.cache_resource
def get_groq_client(api_key: str):
    """
    Obtiene un cliente Groq usando la API key proporcionada.
    
    Args:
        api_key: La API key de Groq
        
    Returns:
        Un cliente Groq configurado o None si no hay API key
    """
    if not api_key:
        return None
    return groq.Groq(api_key=api_key)

def get_groq_api_key() -> Optional[str]:
    """
    Obtiene la API key de Groq de manera segura.
    
    Returns:
        La API key de Groq o None si no se encuentra
    """
    # Primero intentar obtenerla del archivo .env
    api_key = os.getenv("GROQ_API_KEY")
    
    # Si no está en el archivo .env, intentar obtenerla del entorno
    if not api_key:
        # Como último recurso, pedirla al usuario (solo en desarrollo)
        api_key = st.sidebar.text_input("Introduce tu API key de Groq:", type="password")
        if not api_key:
            st.sidebar.warning("Por favor, introduce tu API key de Groq para continuar.")
    
    return api_key

def process_audio_file(file, model, client):
    """
    Procesa un archivo de audio usando la API de Groq.
    
    Args:
        file: El archivo de audio a procesar
        model: El modelo a utilizar para la transcripción
        client: El cliente Groq configurado
        
    Returns:
        El texto transcrito del archivo de audio
    """
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