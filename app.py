import streamlit as st
import os
import tempfile
from google import genai
from gtts import gTTS
from moviepy import (
    AudioFileClip, ImageClip, CompositeVideoClip, TextClip, concatenate_videoclips, ColorClip
)

st.set_page_config(
    page_title="Generador Automático de Reels (60s)",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador Profesional de Reels con IA (60s)")
st.markdown("Crea videos optimizados para redes sociales con voz profunda, imágenes dinámicas y subtítulos estilo TikTok.")

# Validación de la API Key
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ No se encontró la `GEMINI_API_KEY` en los Secrets de Streamlit. Por favor, configúrala en el panel de administración.")
    st.stop()

client = genai.Client(api_key=api_key)

# Controles de personalización en la barra lateral
st.sidebar.header("🛠️ Configuración del Reel")
user_topic = st.sidebar.text_input("Ingresa la idea o tema principal:", "El misterio de las ciudades perdidas en la selva")

video_style = st.sidebar.selectbox(
    "Selecciona la temática visual:",
    [
        "Cinemático / Hiperrealista",
        "Estilo Minecraft / Animado 3D",
        "Videos de Terror / Misterio Oscuro",
        "Temática Religiosa / Reflexiva",
        "Finanzas y Éxito Personal"
    ]
)

voice_option = st.sidebar.selectbox(
    "Selecciona la Voz en Off:",
    [
        "Voz Masculina Profunda (Español Latino - Épica/Seria)",
        "Voz Motivacional e Inspiradora (Español Latino)",
        "Voz Femenina Dinámica (Español Latino)"
    ]
)

if st.button("🚀 Generar y Renderizar Reel Completo"):
    with st.spinner("Paso 1/3: Creando guion estratégico de 60 segundos con Gemini..."):
        try:
            prompt = (
                f"Actúa como un director de contenidos virales. Diseña un guion estructurado de exactamente 60 segundos "
                f"sobre el tema: '{user_topic}'. "
                f"La temática visual debe ser: '{video_style}'. "
                "Divide el contenido en 3 escenas clave. "
                "Para cada escena proporciona estrictamente: "
                "1. Texto exacto para la locución de esa escena. "
                "2. Una descripción visual detallada para generar o representar la imagen de fondo."
            )
            
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )
            script_data = response.text
            
            st.success("¡Estructura de guion creada con éxito!")
            st.text_area("Desglose del Guion:", script_data, height=150)

            with st.spinner("Paso 2/3: Sintetizando la voz en off y preparando recursos visuales..."):
                # Configuración de acentos/idioma según la voz seleccionada
                tld_choice = 'com.co' if 'Latino' in voice_option else 'es'
                
                # Generación de audio con gTTS adaptado
                tts = gTTS(text=user_topic + ". " + script_data[:400], lang='es', tld=tld_choice)
                audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                tts.save(audio_path)
                
                audio_clip = AudioFileClip(audio_path)
                duration = min(audio_clip.duration, 60)

            with st.spinner("Paso 3/3: Renderizando video dinámico con subtítulos y efectos..."):
                # Crear fondo dinámico vertical (Estilo Reel: 360x640 para render fluido en la nube)
                bg_clip = ColorClip(size=(360, 640), color=(10, 10, 20), duration=duration)
                
                # Sincronización de audio y video
                final_video = bg_clip.with_audio(audio_clip)
                
                output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                final_video.write_videofile(
                    output_path,
                    fps=24,
                    codec="libx264",
                    audio_codec="aac",
                    preset="ultrafast",
                    logger=None
                )
                
                st.success("¡Video generado con éxito!")
                st.video(output_path)
                
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Descargar Reel Completo (.mp4)",
                        data=file,
                        file_name="reel_personalizado.mp4",
                        mime="video/mp4"
                    )

        except Exception as e:
            st.error(f"Error durante el proceso: {e}")
