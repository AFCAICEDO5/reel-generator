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
    page_title="Generador de Reels Viral (60s + Subtítulos Estilo TikTok)",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador de Reels Viral (Definitivo)")
st.markdown("Crea videos completos de 60 segundos con imágenes por escena y subtítulos gigantes estilo TikTok.")

# --- CREDENCIALES ---
gemini_api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")
groq_api_key = st.secrets.get("GROQ_API_KEY") if "GROQ_API_KEY" in st.secrets else os.environ.get("GROQ_API_KEY")
openrouter_api_key = st.secrets.get("OPENROUTER_API_KEY") if "OPENROUTER_API_KEY" in st.secrets else os.environ.get("OPENROUTER_API_KEY")

if not gemini_api_key and not groq_api_key and not openrouter_api_key:
    st.error("⚠️ Configura al menos una clave de API (Gemini, Groq u OpenRouter) en los Secrets de Streamlit.")
    st.stop()

gemini_client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None
groq_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=groq_api_key) if groq_api_key else None
openrouter_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_api_key) if openrouter_api_key else None

async def generate_neural_voice(text, voice_name, output_path):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_path)

st.sidebar.header("🛠️ Configuración del Reel")

user_topic = st.sidebar.text_input(
    "1. Tema o idea principal del Reel:", 
    value="Secretos del universo que la ciencia oculta sobre el tiempo y la conciencia humana."
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

if st.button("🚀 Generar Reel Completo de 60s"):
    with st.spinner("Paso 1/4: Generando guion extendido de alto impacto..."):
        try:
            prompt = (
                f"Actúa como un experto guionista de TikTok y Reels virales. Crea un guion extenso y profundo de exactamente 6 escenas "
                f"sobre el tema: '{user_topic}', adaptado al estilo visual: '{video_style}'. "
                "IMPORTANTE: Cada escena debe contener un párrafo de narración sustancial (de 15 a 25 palabras cada uno) para asegurar que el audio dure aproximadamente 60 segundos en total. "
                "Cada texto debe estar en MAYÚSCULAS y ser muy atrapante. "
                "Cada descripción visual debe ser un prompt hiperdetallado en inglés para generar una imagen cinematográfica en 8K. "
                "Devuelve la respuesta estrictamente separada por líneas con este formato exacto: "
                "ESCENA 1 | [TEXTO NARRATIVO LARGO EN MAYÚSCULAS] | [Prompt visual 8K detallado en inglés]\n"
                "ESCENA 2 | [TEXTO NARRATIVO LARGO EN MAYÚSCULAS] | [Prompt visual 8K detallado en inglés]\n"
                "ESCENA 3 | [TEXTO NARRATIVO LARGO EN MAYÚSCULAS] | [Prompt visual 8K detallado en inglés]\n"
                "ESCENA 4 | [TEXTO NARRATIVO LARGO EN MAYÚSCULAS] | [Prompt visual 8K detallado en inglés]\n"
                "ESCENA 5 | [TEXTO NARRATIVO LARGO EN MAYÚSCULAS] | [Prompt visual 8K detallado en inglés]\n"
                "ESCENA 6 | [TEXTO NARRATIVO LARGO EN MAYÚSCULAS] | [Prompt visual 8K detallado en inglés]"
            )
            
            raw_output = None
            
            # Camino 1: Gemini
            if gemini_client and not raw_output:
                for model_name in ["gemini-2.0-flash", "gemini-1.5-flash"]:
                    try:
                        res = gemini_client.models.generate_content(model=model_name, contents=prompt)
                        raw_output = res.text.strip()
                        break
                    except Exception:
                        continue

            # Camino 2: Groq
            if not raw_output and groq_client:
                try:
                    comp = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "Eres un guionista viral."}, {"role": "user", "content": prompt}]
                    )
                    raw_output = comp.choices[0].message.content.strip()
                except Exception:
                    pass

            # Camino 3: OpenRouter
            if not raw_output and openrouter_client:
                try:
                    comp = openrouter_client.chat.completions.create(
                        model="meta-llama/llama-3.3-70b-instruct:free",
                        messages=[{"role": "system", "content": "Eres un guionista viral."}, {"role": "user", "content": prompt}]
                    )
                    raw_output = comp.choices[0].message.content.strip()
                except Exception:
                    pass

            if not raw_output:
                raise Exception("No se pudo generar el guion con ningún proveedor.")

            st.success("¡Guion extendido generado con éxito!")
            st.text_area("Desglose:", raw_output, height=140)

            scenes_data = []
            for line in raw_output.split("\n"):
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        scenes_data.append({"text": parts[1].strip().upper(), "visual": parts[2].strip()})
            
            if not scenes_data:
                raise Exception("El formato del guion no fue interpretado correctamente.")

            full_narration = " ".join([s["text"] for s in scenes_data])

            with st.spinner("Paso 2/4: Sintetizando locución de 60 segundos..."):
                audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                asyncio.run(generate_neural_voice(full_narration, selected_voice_id, audio_path))
                
                audio_clip = AudioFileClip(audio_path)
                total_duration = audio_clip.duration
                scene_duration = total_duration / len(scenes_data)

            with st.spinner("Paso 3/4: Generando imágenes de alta calidad y subtítulos gigantes estilo TikTok..."):
                clip_list = []
                
                for i, scene in enumerate(scenes_data):
                    img_path = None
                    
                    if gemini_client:
                        try:
                            img_res = gemini_client.models.generate_images(
                                model='imagen-3.0-generate-002',
                                prompt=f"{scene['visual']}, vertical 9:16 aspect ratio, ultra-detailed, 8k resolution, cinematic lighting, photorealistic masterpiece",
                                config=dict(number_of_images=1, output_mime_type="image/jpeg", aspect_ratio="9:16")
                            )
                            for gen_img in img_res.generated_images:
                                img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                                with open(img_path, "wb") as f:
                                    f.write(gen_img.image.image_bytes)
                        except Exception:
                            pass
                    
                    if not img_path:
                        # Fondo cinemático dinámico si la API de imagen no responde en capa gratuita
                        base_img = Image.new('RGB', (1080, 1920), color=(15, 15, 25))
                        draw_bg = ImageDraw.Draw(base_img)
                        draw_bg.rectangle([0, 0, 1080, 1920], fill=(20 + (i*10), 10, 40 + (i*15)))
                        img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                        base_img.save(img_path)

                    try:
                        img_pil = Image.open(img_path).convert("RGB")
                        txt_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
                        draw = ImageDraw.Draw(txt_layer)
                        
                        try:
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
                        except:
                            font = ImageFont.load_default()

                        # Envolver texto para que luzca como subtítulos estilo TikTok en la parte inferior central
                        wrapped_text = textwrap.fill(scene['text'], width=18)
                        
                        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
                        tw = bbox[2] - bbox[0]
                        th = bbox[3] - bbox[1]
                        
                        x = (1080 - tw) / 2
                        y = 1350  # Posicionados en el tercio inferior estilo TikTok
                        
                        # Marco de fondo translúcido para legibilidad perfecta
                        draw.rounded_rectangle(
                            [x - 30, y - 20, x + tw + 30, y + th + 20],
                            radius=20,
                            fill=(0, 0, 0, 180)
                        )
                        
                        # Efecto de contorno grueso y texto blanco vibrante
                        for ox in range(-6, 7):
                            for oy in range(-6, 7):
                                if ox != 0 or oy != 0:
                                    draw.multiline_text((x + ox, y + oy), wrapped_text, font=font, fill=(0, 0, 0, 255), align="center")
                        
                        draw.multiline_text((x, y), wrapped_text, font=font, fill=(255, 255, 0, 255), align="center") # Amarillo brillante estilo TikTok
                        
                        img_pil = Image.alpha_composite(img_pil.convert("RGBA"), txt_layer).convert("RGB")
                        subbed_img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                        img_pil.save(subbed_img_path)
                        
                        img_clip = ImageClip(subbed_img_path).with_duration(scene_duration)
                    except Exception:
                        img_clip = ImageClip(img_path).with_duration(scene_duration)

                    clip_list.append(img_clip)

                final_visual = concatenate_videoclips(clip_list)
                final_video = final_visual.with_audio(audio_clip)

            with st.spinner("Paso 4/4: Renderizando video final..."):
                output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                final_video.write_videofile(
                    output_path,
                    fps=24,
                    codec="libx264",
                    audio_codec="aac",
                    preset="ultrafast",
                    logger=None
                )
                
                st.success(f"¡Reel generado con éxito! Duración total: {int(total_duration)} segundos.")
                st.video(output_path)
                
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Descargar Reel (.mp4)",
                        data=file,
                        file_name="reel_viral_tiktok.mp4",
                        mime="video/mp4"
                    )

        except Exception as e:
            st.error(f"Error durante el proceso de generación: {e}")
