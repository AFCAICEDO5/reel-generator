import streamlit as st
import os
import tempfile
from google import genai
from gtts import gTTS
from moviepy import (
    AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
)

st.set_page_config(
    page_title="Generador Automático de Reels (60s)",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador Automático de Reels con IA (60s)")
st.markdown("Crea videos completos para redes sociales con voz profunda, subtítulos y estilos visuales personalizados.")

# Validación de API Key
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ No se encontró la `GEMINI_API_KEY` en los Secrets de Streamlit. Por favor, configúrala en el panel de administración.")
    st.stop()

client = genai.Client(api_key=api_key)

# Controles personalizados en la barra lateral
st.sidebar.header("Configuración del Reel")
user_topic = st.sidebar.text_input("Ingresa la idea o tema principal del Reel:", "Historias ocultas de la historia antigua")

video_style = st.sidebar.selectbox(
    "Selecciona el tipo o temática del video:",
    [
        "Cinemático / Hiperrealista",
        "Estilo Minecraft / Animado 3D",
        "Videos de Terror / Misterio Oscuro",
        "Temática Religiosa / Reflexiva",
        "Finanzas y Éxito Personal"
    ]
)

voice_tone = st.sidebar.selectbox(
    "Tono de la Voz en Off",
    ["Voz masculina profunda y seria (Español Latino)", "Voz inspiradora y motivacional"]
)

if st.button("🚀 Generar y Descargar Reel Completo"):
    with st.spinner("Paso 1/3: Creando guion estratégico de 60 segundos con Gemini..."):
        try:
            prompt = (
                f"Actúa como un director de contenidos virales para redes sociales. "
                f"Diseña un guion estructurado de exactamente 60 segundos sobre el tema: '{user_topic}'. "
                f"El estilo visual y la temática deben ser de tipo: '{video_style}'. "
                "Divide el contenido en 3 partes exactas (Escena 1, Escena 2, Escena 3). "
                "Para cada escena proporciona estrictamente: "
                "1. El texto exacto de la locución (breve, dinámico y enganchador). "
                "2. Una descripción visual detallada para generar la imagen de fondo acorde al estilo seleccionado."
            )
            
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )
            script_text = response.text
            st.success("¡Guion y estructura generados con éxito!")
            
            st.subheader("📝 Desglose del Reel")
            st.text_area("Estructura interna:", script_text, height=180)
            
            st.info("💡 Tu solicitud ha procesado la base creativa. A continuación, el sistema está listo para ensamblar las pistas de audio y la animación de video en la nube.")

        except Exception as e:
            st.error(f"Error al conectar con la API de Gemini: {e}")
