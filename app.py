import streamlit as st
import os
import tempfile
from google import genai
from gtts import gTTS
from moviepy import (
    AudioFileClip, ColorClip, CompositeVideoClip, TextClip
)

st.set_page_config(
    page_title="Generador Automático de Reels (60s)",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador Automático de Reels con IA (60s)")
st.markdown("Crea, personaliza y descarga tu video completo con voz en off, subtítulos y estilos visuales dinámicos.")

# Validación de la API Key
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ No se encontró la `GEMINI_API_KEY` en los Secrets de Streamlit. Por favor, configúrala en el panel de administración.")
    st.stop()

client = genai.Client(api_key=api_key)

# -------------------------------------------------------------
# CONTROLES INTERACTIVOS EN LA BARRA LATERAL (Entradas del Usuario)
# -------------------------------------------------------------
st.sidebar.header("🛠️ Configuración de tu Reel")

user_topic = st.sidebar.text_input(
    "1. Escribe la idea o tema principal:", 
    value="El misterio de las pirámides de Egipto y sus secretos ocultos"
)

video_style = st.sidebar.selectbox(
    "2. Selecciona la temática visual:",
    [
        "Cinemático / Hiperrealista",
        "Estilo Minecraft / Animado 3D",
        "Videos de Terror / Misterio Oscuro",
        "Temática Religiosa / Reflexiva",
        "Finanzas y Éxito Personal"
    ]
)

voice_option = st.sidebar.selectbox(
    "3. Selecciona la Voz en Off:",
    [
        "Voz Masculina Profunda (Español Latino - Épica/Seria)",
        "Voz Motivacional e Inspiradora (Español Latino)",
        "Voz Estándar Latino"
    ]
)

# Paleta de colores temáticos para dar dinamismo visual al fondo del video
style_colors = {
    "Cinemático / Hiperrealista": (20, 30, 50),       # Azul cian elegante
    "Estilo Minecraft / Animado 3D": (34, 139, 34),    # Verde vibrante
    "Videos de Terror / Misterio Oscuro": (40, 10, 10),# Rojo sangre / oscuro
    "Temática Religiosa / Reflexiva": (60, 40, 80),    # Morado solemne
    "Finanzas y Éxito Personal": (10, 50, 30)          # Verde esmeralda corporativo
}

if st.button("🚀 Generar y Renderizar Reel Completo"):
    with st.spinner("Paso 1/3: Creando guion persuasivo con Gemini adaptado a tu tema..."):
        try:
            prompt = (
                f"Actúa como un creador de contenido viral experto. "
                f"Redacta un guion dinámico, directo y atrapante de aproximadamente 45 a 60 segundos sobre este tema específico proporcionado por el usuario: '{user_topic}'. "
                f"El tono debe ajustarse estrictamente a la temática: '{video_style}'. "
                "Devuelve únicamente el texto de la locución que dirá el narrador, sin viñetas de escenas ni notas de director."
            )
            
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )
            narration_text = response.text.strip()
            
            st.success("¡Guion generado con éxito!")
            st.text_area("Texto exacto para la locución:", narration_text, height=130)

            with st.spinner("Paso 2/3: Sintetizando la voz en off seleccionada..."):
                # Configurar acento y parámetros de gTTS según la voz elegida
                tld_choice = 'com.co' if 'Latino' in voice_option or 'Profunda' in voice_option else 'es'
                
                tts = gTTS(text=narration_text, lang='es', tld=tld_choice)
                audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                tts.save(audio_path)
                
                audio_clip = AudioFileClip(audio_path)
                duration = min(audio_clip.duration, 60) # Tope máximo de 60 segundos

                st.info(f"Duración estimada del Reel: {round(duration, 1)} segundos.")

            with st.spinner("Paso 3/3: Renderizando video dinámico y subtítulos..."):
                # Seleccionar color dinámico según la temática elegida
                bg_color = style_colors.get(video_style, (20, 20, 30))
                
                # Crear fondo con dimensiones verticales optimizadas para Reels (360x640)
                bg_clip = ColorClip(size=(360, 640), color=bg_color, duration=duration)
                
                # Sincronizar audio con el video
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
                
                st.success("¡Video renderizado con éxito!")
                st.video(output_path)
                
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Descargar Reel Completo (.mp4)",
                        data=file,
                        file_name="reel_personalizado.mp4",
                        mime="video/mp4"
                    )

        except Exception as e:
            st.error(f"Error durante el proceso de renderizado: {e}")
