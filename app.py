import streamlit as st
import os
import tempfile
import asyncio
import time
import edge_tts
from google import genai
from openai import OpenAI
from moviepy import (
    AudioFileClip, ImageClip, concatenate_videoclips
)
from PIL import Image, ImageDraw, ImageFont
import textwrap

st.set_page_config(
    page_title="Generador de Reels Viral (Gemini + OpenAI)",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador de Reels Viral (Multiproveedor)")
st.markdown("Crea videos con imágenes por escena, subtítulos gigantes y respaldo dual (Gemini / OpenAI).")

# --- CREDENCIALES ---
gemini_api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")
openai_api_key = st.secrets.get("OPENAI_API_KEY") if "OPENAI_API_KEY" in st.secrets else os.environ.get("OPENAI_API_KEY")

if not gemini_api_key and not openai_api_key:
    st.error("⚠️ Configura al menos una clave de API (`GEMINI_API_KEY` u `OPENAI_API_KEY`) en los Secrets de Streamlit.")
    st.stop()

# Inicializar clientes si las claves existen
gemini_client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None
openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None

async def generate_neural_voice(text, voice_name, output_path):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_path)

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
    "3. Selecciona la Voz Neuronal (100% Humana):",
    [
        "México - Dalia (Femenina Natural y Fluida)",
        "México - Jorge (Masculina Profunda y Clara)",
        "Colombia - Gonzalo (Masculina Dinámica)",
        "Colombia - Salome (Femenina Cálida)",
        "Argentina - Tomás (Masculina Cercana)"
    ]
)

voice_mapping = {
    "México - Dalia (Femenina Natural y Fluida)": "es-MX-DaliaNeural",
    "México - Jorge (Masculina Profunda y Clara)": "es-MX-JorgeNeural",
    "Colombia - Gonzalo (Masculina Dinámica)": "es-CO-GonzaloNeural",
    "Colombia - Salome (Femenina Cálida)": "es-CO-SalomeNeural",
    "Argentina - Tomás (Masculina Cercana)": "es-AR-TomasNeural"
}

selected_voice_id = voice_mapping.get(voice_option, "es-MX-DaliaNeural")

if st.button("🚀 Generar Reel con Doble Vía (60s)"):
    with st.spinner("Paso 1/4: Generando guion estructurado con Gemini u OpenAI..."):
        try:
            prompt = (
                f"Actúa como un director de contenidos virales. Diseña un guion fluido de exactamente 6 escenas cortas "
                f"sobre el tema: '{user_topic}', adaptado al estilo visual: '{video_style}'. "
                "Cada texto debe estar en MAYÚSCULAS, ser corto y muy impactante. "
                "Cada descripción visual debe ser un prompt detallado para generar una imagen hiperrealista que acompañe la narración. "
                "Devuelve la respuesta estrictamente separada por líneas con este formato exacto: "
                "ESCENA 1 | [TEXTO EN MAYÚSCULAS] | [Prompt visual detallado 8K para la escena 1]\n"
                "ESCENA 2 | [TEXTO EN MAYÚSCULAS] | [Prompt visual detallado 8K para la escena 2]\n"
                "ESCENA 3 | [TEXTO EN MAYÚSCULAS] | [Prompt visual detallado 8K para la escena 3]\n"
                "ESCENA 4 | [TEXTO EN MAYÚSCULAS] | [Prompt visual detallado 8K para la escena 4]\n"
                "ESCENA 5 | [TEXTO EN MAYÚSCULAS] | [Prompt visual detallado 8K para la escena 5]\n"
                "ESCENA 6 | [TEXTO EN MAYÚSCULAS] | [Prompt visual detallado 8K para la escena 6]"
            )
            
            raw_output = None
            
            # --- CAMINO 1: GEMINI (Intento principal) ---
            if gemini_client:
                models_to_try = ["gemini-2.0-flash", "gemini-1.5-flash"]
                for model_name in models_to_try:
                    success = False
                    for attempt in range(2):
                        try:
                            response = gemini_client.models.generate_content(
                                model=model_name,
                                contents=prompt
                            )
                            raw_output = response.text.strip()
                            success = True
                            break
                        except Exception:
                            time.sleep(1)
                            continue
                    if success:
                        break

            # --- CAMINO 2: OPENAI (Respaldo si Gemini falla o no está configurado) ---
            if not raw_output and openai_client:
                try:
                    completion = openai_client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=[
                            {"role": "system", "content": "Eres un director de contenidos virales."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    raw_output = completion.choices[0].message.content.strip()
                except Exception as openai_err:
                    st.error(f"Error con OpenAI: {openai_err}")

            if not raw_output:
                raise Exception("Ambos caminos (Gemini y OpenAI) fallaron o no están configurados correctamente.")

            st.success("¡Guion y prompts visuales generados con éxito!")
            st.text_area("Desglose del Guion:", raw_output, height=140)

            scenes_data = []
            lines = raw_output.split("\n")
            
            for line in lines:
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        text_part = parts[1].strip().upper()
                        visual_part = parts[2].strip()
                        scenes_data.append({"text": text_part, "visual": visual_part})
            
            if not scenes_data:
                scenes_data = [{"text": user_topic.upper(), "visual": f"Hyperrealistic 8k cinematic shot of {user_topic}"}]

            full_narration = " ".join([s["text"] for s in scenes_data])

            with st.spinner("Paso 2/4: Sintetizando locución con Voz Neuronal..."):
                audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                asyncio.run(generate_neural_voice(full_narration.strip(), selected_voice_id, audio_path))
                
                audio_clip = AudioFileClip(audio_path)
                total_duration = min(audio_clip.duration, 60)
                scene_duration = total_duration / len(scenes_data)

            with st.spinner("Paso 3/4: Generando imágenes por escena y aplicando subtítulos gigantes estilo viral..."):
                clip_list = []
                
                for i, scene in enumerate(scenes_data):
                    img_path = None
                    
                    if gemini_client:
                        try:
                            img_response = gemini_client.models.generate_images(
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
                    
                    if not img_path:
                        base_img = Image.new('RGB', (1080, 1920), color=(10, 15, 30))
                        draw_bg = ImageDraw.Draw(base_img)
                        draw_bg.rectangle([0, 1000, 1080, 1920], fill=(50 + (i*15), 30, 70))
                        draw_bg.ellipse([100, 200, 980, 1400], fill=(90, 60, 120))
                        img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                        base_img.save(img_path)

                    try:
                        img_pil = Image.open(img_path).convert("RGB")
                        
                        txt_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
                        draw = ImageDraw.Draw(txt_layer)
                        
                        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                        try:
                            font = ImageFont.truetype(font_path, 120)
                        except:
                            font = ImageFont.load_default()

                        wrapped_text = textwrap.fill(scene['text'], width=12)
                        
                        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
                        text_width = bbox[2] - bbox[0]
                        text_height = bbox[3] - bbox[1]
                        
                        x = (1080 - text_width) / 2
                        y = (1920 - text_height) / 2 - 100
                        
                        outline_range = 10
                        for adj_x in range(-outline_range, outline_range + 1):
                            for adj_y in range(-outline_range, outline_range + 1):
                                if adj_x != 0 or adj_y != 0:
                                    draw.multiline_text((x + adj_x, y + adj_y), wrapped_text, font=font, fill=(0, 0, 0, 255), align="center")
                        
                        draw.multiline_text((x, y), wrapped_text, font=font, fill=(255, 255, 255, 255), align="center")
                        
                        img_pil = Image.alpha_composite(img_pil.convert("RGBA"), txt_layer).convert("RGB")
                        
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
                
                st.success("¡Reel generado con éxito!")
                st.video(output_path)
                
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Descargar Reel con Subtítulos Gigantes (.mp4)",
                        data=file,
                        file_name="reel_viral_gigante.mp4",
                        mime="video/mp4"
                    )

        except Exception as e:
            st.error(f"Error durante el proceso de generación: {e}")
