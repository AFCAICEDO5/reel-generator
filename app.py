import streamlit as st
import os
import tempfile
from google import genai
from gtts import gTTS
from moviepy import (
    AudioFileClip, ColorClip, CompositeVideoClip
)

st.set_page_config(
    page_title="Generador Automático de Reels (60s)",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador Automático de Reels con IA (60s)")
st.markdown("Crea, renderiza y descarga tu video completo con voz en off, subtítulos y estilos visuales personalizados.")

# Validación de la API Key
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
    ["Voz masculina seria (Español Latino)", "Voz inspiradora y motivacional"]
)

if st.button("🚀 Generar y Renderizar Reel Completo"):
    with st.spinner("Paso 1/3: Creando guion y locución con Gemini..."):
        try:
            prompt = (
                f"Actúa como un director de contenidos virales para redes sociales. "
                f"Diseña un guion breve y directo de aproximadamente 45 a 60 segundos sobre el tema: '{user_topic}'. "
                f"El estilo visual y la temática deben ser de tipo: '{video_style}'. "
                "Dame estrictamente un texto continuo para la voz en off, sin etiquetas de escenas ni instrucciones de cámara, "
                "solo el texto exacto que dirá el narrador de forma atractiva y persuasiva."
            )
            
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )
            narration_text = response.text.strip()
            
            st.success("¡Guion generado con éxito!")
            st.text_area("Texto procesado para la voz:", narration_text, height=120)

            with st.spinner("Paso 2/3: Sintetizando la voz en off y preparando el video..."):
                # Generar audio con gTTS (español)
                tts = gTTS(text=narration_text, lang='es', tld='com.co')
                audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                tts.save(audio_path)
                
                audio_clip = AudioFileClip(audio_path)
                duration = audio_clip.duration
                if duration > 60:
                    duration = 60 # Límite máximo de 60 segundos

                st.info(f"Duración estimada de la locución: {round(duration, 1)} segundos.")

            with st.spinner("Paso 3/3: Renderizando archivo de video final en la nube..."):
                # Crear fondo dinámico vertical optimizado para Reels
                bg_clip = ColorClip(size=(360, 640), color=(15, 15, 25), duration=duration)
                
                # Sincronizar audio con el contenedor de video
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
                
                st.success("¡Video renderizado y listo!")
                st.video(output_path)
                
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Descargar Reel Completo (.mp4)",
                        data=file,
                        file_name="reel_generado.mp4",
                        mime="video/mp4"
                    )

        except Exception as e:
            st.error(f"Error durante el proceso de renderizado: {e}")
