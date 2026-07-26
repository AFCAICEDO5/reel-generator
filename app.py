import streamlit as st
import os
import tempfile
from google import genai
from gtts import gTTS
from moviepy import (
    AudioFileClip, ImageClip, concatenate_videoclips
)
from PIL import Image, ImageDraw, ImageFont
import textwrap

st.set_page_config(
    page_title="Generador de Reels Estilo Viral",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador de Reels Estilo Viral")
st.markdown("Crea videos con subtítulos grandes en mayúsculas, borde negro marcado y estilo idéntico a los mejores Reels y TikToks.")

api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ No se encontró la `GEMINI_API_KEY` en los Secrets de Streamlit. Configúrala en el panel de administración.")
    st.stop()

client = genai.Client(api_key=api_key)

# -------------------------------------------------------------
# CONTROLES INTERACTIVOS EN LA BARRA LATERAL
# -------------------------------------------------------------
st.sidebar.header("🛠️ Configuración del Reel")

user_topic = st.sidebar.text_input(
    "1. Tema o idea principal del Reel:", 
    value="Espíritu, ¿sabes qué hay más allá de la vida?"
)

video_style = st.sidebar.selectbox(
    "2. Estilo Visual:",
    [
        "Cinemático / Animado 3D (Estilo Referencia)",
        "Estilo Minecraft / Animado 3D",
        "Videos de Terror / Misterio Oscuro",
        "Temática Religiosa / Reflexiva",
        "Finanzas y Éxito Personal"
    ]
)

voice_option = st.sidebar.selectbox(
    "3. Selecciona la Voz Natural:",
    [
        "Voz Natural Latinoamericana (México - Alta Fluidez)",
        "Voz Profunda Épica (Argentina - Tono Serio)",
        "Voz Dinámica (Colombia - Acento Claro)",
        "Voz Narrador Solemne (España - Neutro)"
    ]
)

if st.button("🚀 Generar Reel con Subtítulos Estilo Viral (60s)"):
    with st.spinner("Paso 1/4: Generando guion estructurado de 6 escenas..."):
        try:
            prompt = (
                f"Actúa como un creador de contenido viral. Diseña un guion fluido de exactamente 6 escenas cortas "
                f"sobre el tema: '{user_topic}', adaptado al estilo visual: '{video_style}'. "
                "Cada texto debe estar redactado en MAYÚSCULAS y ser muy impactante. "
                "Devuelve la respuesta estrictamente separada por líneas con este formato exacto: "
                "ESCENA 1 | [TEXTO EN MAYÚSCULAS PARA LA VOZ Y PANTALLA] | [Prompt visual hiperrealista detallado 8K para escena 1]\n"
                "ESCENA 2 | [TEXTO EN MAYÚSCULAS PARA LA VOZ Y PANTALLA] | [Prompt visual hiperrealista detallado 8K para escena 2]\n"
                "ESCENA 3 | [TEXTO EN MAYÚSCULAS PARA LA VOZ Y PANTALLA] | [Prompt visual hiperrealista detallado 8K para escena 3]\n"
                "ESCENA 4 | [TEXTO EN MAYÚSCULAS PARA LA VOZ Y PANTALLA] | [Prompt visual hiperrealista detallado 8K para escena 4]\n"
                "ESCENA 5 | [TEXTO EN MAYÚSCULAS PARA LA VOZ Y PANTALLA] | [Prompt visual hiperrealista detallado 8K para escena 5]\n"
                "ESCENA 6 | [TEXTO EN MAYÚSCULAS PARA LA VOZ Y PANTALLA] | [Prompt visual hiperrealista detallado 8K para escena 6]"
            )
            
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt
            )
            raw_output = response.text.strip()
            
            st.success("¡Estructura de guion generada con éxito!")
            st.text_area("Desglose del Guion:", raw_output, height=140)

            scenes_data = []
            lines = raw_output.split("\n")
            full_narration = ""
            
            for line in lines:
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        text_part = parts[1].strip().upper()
                        visual_part = parts[2].strip()
                        full_narration += " " + text_part
                        scenes_data.append({"text": text_part, "visual": visual_part})
            
            if not scenes_data:
                full_narration = user_topic.upper()
                scenes_data = [{"text": user_topic.upper(), "visual": f"Hyperrealistic 8k cinematic shot of {user_topic}, highly detailed"}]

            with st.spinner("Paso 2/4: Sintetizando voz natural..."):
                if "México" in voice_option:
                    tld_choice = 'com.mx'
                elif "Argentina" in voice_option:
                    tld_choice = 'com.ar'
                elif "España" in voice_option:
                    tld_choice = 'es'
                else:
                    tld_choice = 'com.co'
                
                tts = gTTS(text=full_narration.strip(), lang='es', tld=tld_choice, slow=False)
                audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                tts.save(audio_path)
                
                audio_clip = AudioFileClip(audio_path)
                total_duration = min(audio_clip.duration, 60)
                scene_duration = total_duration / len(scenes_data)

            with st.spinner("Paso 3/4: Generando imágenes y aplicando el estilo de subtítulos de la imagen de referencia..."):
                clip_list = []
                
                for i, scene in enumerate(scenes_data):
                    img_path = None
                    
                    # Generación mediante Imagen 3 API
                    try:
                        img_response = client.models.generate_images(
                            model='imagen-3.0-generate-002',
                            prompt=f"{scene['visual']}, vertical 9:16 aspect ratio, ultra-detailed, 8k resolution, cinematic lighting, photorealistic masterpiece",
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
                    except Exception:
                        pass
                    
                    # Respaldo visual inteligente si la API de imágenes experimenta alta demanda
                    if not img_path:
                        base_img = Image.new('RGB', (1080, 1920), color=(20 + (i*10), 15, 50 + (i*15)))
                        draw_bg = ImageDraw.Draw(base_img)
                        draw_bg.ellipse([-150, 600, 1200, 1600], fill=(50, 30, 90))
                        img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                        base_img.save(img_path)

                    # Procesar imagen y quemar subtítulos idénticos a la referencia (Letras blancas gruesas con borde negro centrado)
                    try:
                        img_pil = Image.open(img_path).convert("RGB")
                        
                        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                        try:
                            font = ImageFont.truetype(font_path, 85) # Tamaño grande idéntico a la referencia
                        except:
                            font = ImageFont.load_default()

                        scene_text = scene['text']
                        wrapped_text = textwrap.fill(scene_text, width=16)
                        
                        draw_temp = ImageDraw.Draw(img_pil)
                        bbox = draw_temp.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        
                        # Ubicación central exacta como en la imagen de referencia
                        x = (1080 - text_width) / 2
                        y = 1920 / 2 - text_height / 2 + 100
                        
                        draw = ImageDraw.Draw(img_pil)
                        
                        # Dibujar contorno negro grueso alrededor del texto blanco (Estilo meme/viral exacto)
                        outline_range = 7
                        for adj_x in range(-outline_range, outline_range + 1):
                            for adj_y in range(-outline_range, outline_range + 1):
                                if adj_x != 0 or adj_y != 0:
                                    draw.multiline_text((x + adj_x, y + adj_y), wrapped_text, font=font, fill="black", align="center")
                        
                        # Texto principal en blanco puro
                        draw.multiline_text((x, y), wrapped_text, font=font, fill="white", align="center")
                        
                        subbed_img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                        img_pil.save(subbed_img_path)
                        
                        img_clip = ImageClip(subbed_img_path).with_duration(scene_duration)
                    except Exception:
                        img_clip = ImageClip(img_path).with_duration(scene_duration)

                    clip_list.append(img_clip)

                final_visual = concatenate_videoclips(clip_list)
                final_video = final_visual.with_audio(audio_clip)

            with st.spinner("Paso 4/4: Renderizando video final en alta definición..."):
                output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                final_video.write_videofile(
                    output_path,
                    fps=24,
                    codec="libx264",
                    audio_codec="aac",
                    preset="ultrafast",
                    logger=None
                )
                
                st.success("¡Reel generado con el estilo visual exacto!")
                st.video(output_path)
                
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Descargar Reel Estilo Viral (.mp4)",
                        data=file,
                        file_name="reel_estilo_referencia.mp4",
                        mime="video/mp4"
                    )

        except Exception as e:
            st.error(f"Error durante el proceso de generación: {e}")
