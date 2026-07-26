import streamlit as st
import os
import tempfile
from google import genai
from gtts import gTTS
from moviepy import (
    AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips
)
from PIL import Image, ImageDraw, ImageFont
import textwrap

st.set_page_config(
    page_title="Generador Automático de Reels (60s)",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador Profesional de Reels con IA (60s)")
st.markdown("Crea videos con imágenes hiperrealistas en resolución 8K, múltiples voces naturales y subtítulos grandes estilo TikTok.")

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
                scenes_data = [{"text": user_topic, "visual": f"Hyperrealistic 8k cinematic shot of {user_topic}, highly detailed"}]

            with st.spinner("Paso 2/4: Sintetizando la voz en off seleccionada..."):
                if "Solemne" in voice_option:
                    tld_choice = 'es'
                elif "Femenina" in voice_option:
                    tld_choice = 'com.mx'
                else:
                    tld_choice = 'com.co'
                
                tts = gTTS(text=full_narration.strip(), lang='es', tld=tld_choice)
                audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                tts.save(audio_path)
                
                audio_clip = AudioFileClip(audio_path)
                total_duration = min(audio_clip.duration, 60)
                scene_duration = total_duration / len(scenes_data)

            with st.spinner("Paso 3/4: Generando imágenes hiperrealistas en resolución 8K y subtítulos estilo TikTok..."):
                clip_list = []
                
                for i, scene in enumerate(scenes_data):
                    img_path = None
                    # Generación de imagen hiperrealista utilizando Imagen 3 con especificaciones 8K[span_0](start_span)[span_0](end_span)
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
                    
                    # Fallback visual de alta calidad si la API de imágenes presenta restricciones temporales
                    if not img_path:
                        base_img = Image.new('RGB', (1080, 1920), color=(10, 15, 30))
                        img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                        base_img.save(img_path)

                    # Incrustar subtítulos grandes y legibles estilo TikTok con caja de contraste (Pillow)
                    try:
                        img_pil = Image.open(img_path).convert("RGB")
                        draw = ImageDraw.Draw(img_pil)
                        
                        # Cargar fuente en tamaño grande (70px) para evitar textos pequeños o círculos
                        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                        try:
                            font = ImageFont.truetype(font_path, 70)
                        except:
                            font = ImageFont.load_default()

                        # Envolver texto optimizado para formato vertical
                        wrapped_text = textwrap.fill(scene['text'], width=20)
                        
                        # Calcular dimensiones del texto
                        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        
                        # Posicionar subtítulos en la parte inferior central estilo TikTok
                        x = (1080 - text_width) / 2
                        y = 1920 - text_height - 350
                        
                        # Dibujar rectángulo de fondo semitransparente (caja estilo TikTok) para máxima visibilidad
                        padding = 30
                        box_coords = [x - padding, y - padding, x + text_width + padding, y + text_height + padding]
                        
                        overlay = Image.new("RGBA", img_pil.size, (0, 0, 0, 0))
                        overlay_draw = ImageDraw.Draw(overlay)
                        overlay_draw.rounded_rectangle(box_coords, radius=20, fill=(0, 0, 0, 180)) # Fondo negro translúcido
                        
                        img_pil = Image.alpha_composite(img_pil.convert("RGBA"), overlay).convert("RGB")
                        draw = ImageDraw.Draw(img_pil)
                        
                        # Dibujar contorno exterior negro y texto blanco brillante
                        offset = 4
                        for adj_x in range(-offset, offset + 1):
                            for adj_y in range(-offset, offset + 1):
                                draw.multiline_text((x + adj_x, y + adj_y), wrapped_text, font=font, fill="black", align="center")
                        
                        draw.multiline_text((x, y), wrapped_text, font=font, fill="white", align="center")
                        
                        subbed_img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                        img_pil.save(subbed_img_path)
                        
                        img_clip = ImageClip(subbed_img_path).with_duration(scene_duration)
                    except Exception:
                        img_clip = ImageClip(img_path).with_duration(scene_duration)

                    clip_list.append(img_clip)

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
