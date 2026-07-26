import streamlit as st
import os
import tempfile
from google import genai
from moviepy import (
    VideoFileClip, TextClip, CompositeVideoClip, 
    AudioFileClip, ImageClip, concatenate_videoclips
)

st.set_page_config(
    page_title="Generador Automático de Reels (60s)",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador Automático de Reels con IA (60s)")
st.markdown("Crea, anima y descarga tu video completo con voz profunda, imágenes hiperrealistas y subtítulos estilo TikTok.")

# Validación de API Key
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ No se encontró la `GEMINI_API_KEY` en los Secrets de Streamlit. Por favor, configúrala en el panel de administración.")
    st.stop()

client = genai.Client(api_key=api_key)

# Controles de configuración
st.sidebar.header("Configuración del Reel")
topic = st.sidebar.text_input("¿De qué tema quieres que sea el Reel?", "El poder de la disciplina mental y el éxito")
visual_style = st.sidebar.selectbox("Estilo de las imágenes", ["Hiperrealista cinematográfico", "Cyberpunk oscuro", "Cinemático dramático"])

if st.button("🚀 Generar y Renderizar Video Completo"):
    with st.spinner("Paso 1/3: Creando estructura de 60 segundos con IA..."):
        try:
            prompt = (
                f"Actúa como un director experto en redes sociales. Diseña un guion exacto de 60 segundos "
                f"sobre el tema: '{topic}'. "
                "La voz en off debe ser con tono masculino profundo, serio y motivador en español latino. "
                f"El estilo visual debe ser {visual_style}. "
                "Divide el contenido en 4 escenas clave. Para cada escena proporciona: "
                "1. El texto exacto de la locución. "
                "2. Una descripción visual altamente detallada e hiperrealista para generar la imagen."
            )
            
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )
            script_content = response.text
            st.success("¡Estructura generada correctamente!")
            
            # Mostramos el desglose en pantalla mientras procesamos
            st.subheader("📝 Guion y Escenas del Reel Automatizado")
            st.text_area("Desglose:", script_content, height=200)

            st.warning("⚠️ **Nota de procesamiento:** Para completar el ensamblaje automático de video con voz en off de alta calidad y animaciones de imagen en la nube de Streamlit, asegúrate de tener integrados los sintetizadores de voz (como gTTS o ElevenLabs) y los prompts de imágenes conectados a tu pipeline de MoviePy.")

        except Exception as e:
            st.error(f"Error al conectar con la API de Gemini: {e}")
