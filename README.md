# Asistente IA con Groq y Streamlit

Esta es una aplicación simple que te permite chatear con modelos de IA de Groq utilizando una interfaz web creada con Streamlit.

## Requisitos

- Python 3.9+
- Una API key de Groq (puedes obtenerla en https://console.groq.com/keys)

## Instalación

1. Clona este repositorio o descarga los archivos
2. Crea un entorno virtual de Python:
   ```
   python3 -m venv venv
   ```
3. Activa el entorno virtual:
   - En macOS/Linux:
     ```
     source venv/bin/activate
     ```
   - En Windows:
     ```
     venv\Scripts\activate
     ```
4. Instala las dependencias:
   ```
   pip install streamlit groq requests python-dotenv
   ```

## Configuración Segura de la API Key

Para usar la aplicación de forma segura:

1. Crea un archivo llamado `.env` en la raíz del proyecto
2. Añade tu API key de Groq en el siguiente formato:
   ```
   GROQ_API_KEY=tu_api_key_aquí
   ```
3. Este archivo está incluido en `.gitignore` y no se subirá a GitHub

## Uso

1. Activa el entorno virtual (si aún no está activado)
2. Ejecuta la aplicación con Streamlit:
   ```
   streamlit run app.py
   ```
3. Se abrirá automáticamente una página web en tu navegador
4. Si no has configurado el archivo `.env`, se te pedirá ingresar tu API key de Groq
5. ¡Comienza a chatear con el asistente!

## Características

- Interfaz de chat amigable
- Uso del modelo llama-3.3-70b-versatile
- Respuestas en streaming para una experiencia más natural
- Ajustes de temperatura y tokens máximos
- Historial de chat persistente durante la sesión
- Opción para limpiar la conversación
- Almacenamiento seguro de API keys a través de variables de entorno

## Obtener una API Key de Groq

1. Ve a [console.groq.com/keys](https://console.groq.com/keys)
2. Regístrate o inicia sesión
3. Genera una nueva API key

## Seguridad

- La API key nunca se almacena en el código
- El archivo `.env` está incluido en `.gitignore` para evitar subirlo accidentalmente
- Si no encuentras una API key en el archivo `.env`, la aplicación te pedirá ingresarla manualmente
