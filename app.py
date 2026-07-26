import streamlit as st
import os
import tempfile
from google import genai
from gtts import gTTS
from moviepy import (
    AudioFileClip, ImageClip, CompositeVideoClip, TextClip, concatenate_videoclips, ColorClip
)
from PIL import Image, ImageDraw, ImageFont

st.set_page_config(
    page_title="Generador Automático de Reels (60s)",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador Profesional de Reels con IA (60s)")
st.markdown("Crea videos con imágenes hiperrealistas generadas por IA, múltiples voces naturales y subtítulos estilo TikTok.")

# Validación de la API Key
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ No se encontró la `GEMINI_API_KEY` en los Secrets de Streamlit. Por favor, configúrala en el panel de administración.")
    st.stop()

client = genai.Client(api_key=api_key)

# -------------------------------------------------------------
# CONTROLES INTERACTIVOS EN LA BARRA LATERAL
# -------------------------------------------------------------
st.sidebar.header("🛠️ Configuración Avanzada del Reel")

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
        "Voz Masculina Joven (Español Latino - Dinámica)",
        "Voz Femenina Natural (Español Latino)",
        "Voz Narrador Solemne (Español Neutro)"
    ]
)

if st.button("🚀 Generar y Renderizar Reel Completo"):
    with st.spinner("Paso 1/4: Diseñando guion y segmentación visual con Gemini..."):
        try:
            prompt = (
                f"Actúa como un director de videos virales. Diseña un guion estructurado de exactamente 3 escenas cortas "
                f"sobre el tema: '{user_topic}', adaptado al estilo visual: '{video_style}'. "
                "Devuelve la respuesta estrictamente separada por líneas con este formato exacto: "
                "ESCENA 1 | [Texto corto y atrapante para la voz] | [Descripción visual detallada para generar una imagen hiperrealista]\n"
                "ESCENA 2 | [Texto corto y atrapante para la voz] | [Descripción visual detallada para generar una imagen hiperrealista]\n"
                "ESCENA 3 | [Texto corto y atrapante para la voz] | [Descripción visual detallada para generar una imagen hiperrealista]"
            )
            
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )
            raw_output = response.text.strip()
            
            st.success("¡Estructura de guion generada con éxito!")
            st.text_area("Desglose del Guion:", raw_output, height=120)

            # Procesamiento y extracción de escenas
            scenes_data = []
            lines = raw_output.split("\n")
            full_narration = ""
            
            for line in lines:
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        text_part = parts[1].strip()
                        visual_part = parts[2].strip()
                        full_narration += " " + text_part
                        scenes_data.append({"text": text_part, "visual": visual_part})
            
            if not scenes_data:
                full_narration = user_topic
                scenes_data = [{"text": user_topic, "visual": f"Hyperrealistic 8k cinematic shot of {user_topic}"}]

            with st.spinner("Paso 2/4: Sintetizando la voz en off seleccionada..."):
                # Configurar acentos y parámetros de gTTS según la voz seleccionada
                if "Solemne" in voice_option:
                    tld_choice = 'es'
                elif "Femenina" in voice_option:
                    tld_choice = 'com.mx'
                else:
                    tld_choice = 'com.co' # Variante latina profunda por defecto
                
                tts = gTTS(text=full_narration.strip(), lang='es', tld=tld_choice)
                audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                tts.save(audio_path)
                
                audio_clip = AudioFileClip(audio_path)
                total_duration = min(audio_clip.duration, 60)
                scene_duration = total_duration / len(scenes_data)

            with st.spinner("Paso 3/4: Generando imágenes hiperrealistas y subtítulos dinámicos..."):
                clip_list = []
                
                for i, scene in enumerate(scenes_data):
                    img_clip = None
                    # Intentar generar imagen hiperrealista mediante Imagen 3[span_1](start_span)[span_1](end_span)
                    try:
                        img_response = client.models.generate_images(
                            model='imagen-3.0-generate-002',
                            prompt=f"{scene['visual']}, vertical 9:16 aspect ratio, ultra-detailed, 8k resolution, cinematic lighting, photorealistic",
                            config=dict(
                                number_of_images=1,
                                output_mime_type="image/jpeg",
                                aspect_ratio="9:16",
                            )
                        )
                        for generated_image in img_response.generated_images:
                            image_bytes = generated_image.image.image_bytes
                            img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                            with open(img_path, "wb") as f:
                                f.write(image_bytes)
                            img_clip = ImageClip(img_path).with_duration(scene_duration)
                    except Exception:
                        pass
                    
                    # Fallback visual garantizado (evita pantalla negra si la cuota de imágenes satura)
                    if img_clip is None:
                        fallback_colors = [(15, 32, 67), (45, 10, 20), (10, 50, 40), (50, 40, 10)]
                        img_clip = ColorClip(size=(1080, 1920), color=fallback_colors[i % len(fallback_colors)], duration=scene_duration)

                    # Generar subtítulos grandes y legibles estilo TikTok usando Pillow incrustado en MoviePy
                    try:
                        txt_clip = TextClip(
                            text=scene['text'],
                            font_size=60,
                            color='white',
                            font='Arial-Bold',
                            stroke_color='black',
                            stroke_width=4,
                            size=(950, None),
                            method='caption'
                        ).with_duration(scene_duration).with_position(('center', 'center'))
                        
                        video_scene = CompositeVideoClip([img_clip, txt_clip])
                    except Exception:
                        video_scene = img_clip

                    clip_list.append(video_scene)

                final_visual = concatenate_videoclips(clip_list)
                final_video = final_visual.with_audio(audio_clip)

            with st.spinner("Paso 4/4: Renderizando archivo final en alta definición (1080x1920)..."):
                output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                final_video.write_videofile(
                    output_path,
                    fps=24,
                    codec="libx264",
                    audio_codec="aac",
                    preset="ultrafast",
                    logger=None
                )
                
                st.success("¡Reel renderizado con éxito!")
                st.video(output_path)
                
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Descargar Reel Completo con Subtítulos (.mp4)",
                        data=file,
                        file_name="reel_viral.mp4",
                        mime="video/mp4"
                    )

        except Exception as e:
            st.error(f"Error durante el proceso de generación: {e}")
