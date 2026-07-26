import streamlit as st
import os
import tempfile
from google import genai
from gtts import gTTS
from moviepy import (
    AudioFileClip, ImageClip, CompositeVideoClip, TextClip, concatenate_videoclips
)
from PIL import Image

st.set_page_config(
    page_title="Generador Automático de Reels (60s)",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador Profesional de Reels con IA (60s)")
st.markdown("Crea videos completos con imágenes hiperrealistas, voz profunda latina y subtítulos estilo TikTok.")

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
        "Voz Femenina Suave (Español Latino)",
        "Voz de Narrador Misterioso (Español de España)"
    ]
)

if st.button("🚀 Generar y Renderizar Reel Completo"):
    with st.spinner("Paso 1/4: Diseñando guion y segmentación visual con Gemini..."):
        try:
            prompt = (
                f"Actúa como un director de videos virales. Diseña un guion estructurado de 3 escenas cortas "
                f"sobre el tema: '{user_topic}', adaptado al estilo: '{video_style}'. "
                "Devuelve la respuesta estrictamente separada por escenas en este formato exacto: "
                "ESCENA 1 | [Texto para la voz] | [Descripción visual detallada para generar la imagen hiperrealista]\n"
                "ESCENA 2 | [Texto para la voz] | [Descripción visual detallada para generar la imagen hiperrealista]\n"
                "ESCENA 3 | [Texto para la voz] | [Descripción visual detallada para generar la imagen hiperrealista]"
            )
            
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )
            raw_output = response.text.strip()
            
            st.success("¡Estructura y guion generados con éxito!")
            st.text_area("Desglose del Guion:", raw_output, height=120)

            # Procesamiento de escenas
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
                # Fallback por si la IA varía el formato
                full_narration = user_topic
                scenes_data = [{"text": user_topic, "visual": f"Hyperrealistic 8k image of {user_topic}, cinematic lighting"}]

            with st.spinner("Paso 2/4: Sintetizando la voz en off seleccionada..."):
                # Configurar acentos según la opción de voz elegida para evitar que suene genérica
                if "Español de España" in voice_option:
                    tld_choice = 'es'
                else:
                    tld_choice = 'com.co' # Variante latina con gTTS
                
                tts = gTTS(text=full_narration.strip(), lang='es', tld=tld_choice)
                audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                tts.save(audio_path)
                
                audio_clip = AudioFileClip(audio_path)
                total_duration = min(audio_clip.duration, 60)
                scene_duration = total_duration / len(scenes_data)

            with st.spinner("Paso 3/4: Generando imágenes hiperrealistas y aplicando subtítulos TikTok..."):
                clip_list = []
                
                for i, scene in enumerate(scenes_data):
                    # Generar imagen mediante Imagen 3 / Generative AI SDK para asegurar contenido visual real
                    try:
                        img_response = client.models.generate_images(
                            model='imagen-3.0-generate-002',
                            prompt=f"{scene['visual']}, vertical 9:16 aspect ratio, ultra-detailed, 8k resolution, cinematic composition",
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
                        # Fallback visual si la cuota de imágenes de la API experimenta restricciones temporales
                        from moviepy import ColorClip
                        bg_colors = [(20, 30, 50), (40, 10, 10), (10, 40, 30)]
                        img_clip = ColorClip(size=(1080, 1920), color=bg_colors[i % len(bg_colors)], duration=scene_duration)

                    # Crear subtítulos grandes estilo TikTok centrados en pantalla
                    try:
                        txt_clip = TextClip(
                            text=scene['text'],
                            font_size=55,
                            color='white',
                            font='Arial-Bold',
                            stroke_color='black',
                            stroke_width=3,
                            size=(950, None),
                            method='caption'
                        ).with_duration(scene_duration).with_position(('center', 'center'))
                        
                        video_scene = CompositeVideoClip([img_clip, txt_clip])
                    except Exception:
                        video_scene = img_clip

                    clip_list.append(video_scene)

                # Concatenar todas las escenas
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
