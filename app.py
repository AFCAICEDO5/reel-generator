import streamlit as st
import os
import tempfile
import asyncio
import edge_tts
from google import genai
from google.genai import types
from openai import OpenAI
from moviepy import AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import textwrap
import base64
import requests

st.set_page_config(
    page_title="Generador de Reels Pro con Múltiples IAs",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador de Reels Pro (Guion Inteligente & DALL-E 3 / Meta / FLUX)")
st.markdown("Crea videos virales de 60s eligiendo entre múltiples motores de texto e imagen de última generación.")

# --- CREDENCIALES ---
gemini_api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")
openai_api_key = st.secrets.get("OPENAI_API_KEY") if "OPENAI_API_KEY" in st.secrets else os.environ.get("OPENAI_API_KEY")
groq_api_key = st.secrets.get("GROQ_API_KEY") if "GROQ_API_KEY" in st.secrets else os.environ.get("GROQ_API_KEY")
openrouter_api_key = st.secrets.get("OPENROUTER_API_KEY") if "OPENROUTER_API_KEY" in st.secrets else os.environ.get("OPENROUTER_API_KEY")
cloudflare_api_token = st.secrets.get("CLOUDFLARE_API_TOKEN") if "CLOUDFLARE_API_TOKEN" in st.secrets else os.environ.get("CLOUDFLARE_API_TOKEN", "")
cloudflare_account_id = st.secrets.get("CLOUDFLARE_ACCOUNT_ID") if "CLOUDFLARE_ACCOUNT_ID" in st.secrets else os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")

if not gemini_api_key and not openai_api_key and not groq_api_key:
    st.error("⚠️ Configura al menos una clave de API principal (Gemini o OpenAI) en los Secrets de Streamlit.")
    st.stop()

gemini_client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None
openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None
groq_client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=groq_api_key) if groq_api_key else None
openrouter_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_api_key) if openrouter_api_key else None

async def generate_neural_voice_robust(text, voice_name, output_path):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            communicate = edge_tts.Communicate(text, voice_name)
            await communicate.save(output_path)
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                return True
        except Exception:
            if attempt == max_retries - 1:
                raise
            await asyncio.sleep(2)
    return False

st.sidebar.header("🛠️ Configuración del Reel")

user_topic = st.sidebar.text_input(
    "Tema o idea principal del Reel:", 
    value="3 hábitos sencillos para duplicar tu productividad sin agotarte."
)

visual_style = st.sidebar.selectbox(
    "Estilo Visual de las Escenas:",
    [
        "Cinematográfico",
        "Fotorrealista",
        "Anime",
        "Ciencia Ficción",
        "Terror Oscuro",
        "Fantasía",
        "Minecraft",
        "Pixel Art"
    ]
)

image_provider = st.sidebar.selectbox(
    "Proveedor de Generación de Imágenes:",
    [
        "OpenAI DALL-E 3 (Alta Calidad)",
        "Google Gemini (flash-image nativo)",
        "Modelos Open Source (FLUX / Llama Ecosystem via OpenRouter)",
        "Cloudflare Workers AI (Serverless)"
    ]
)

voice_option = st.sidebar.selectbox(
    "Selecciona la Voz Neuronal (Voces Profundas y Estándar):",
    [
        "México - Emiliano (Masculina Muy Profunda / Épica y Documental)",
        "México - Jorge (Masculina Profunda y Clara)",
        "Colombia - Carlos (Masculina Corporativa y Autoritaria / Graves)",
        "México - Lucia (Femenina con Graves / Misterio y Narrativa)",
        "México - Dalia (Femenina Natural y Fluida)",
        "Colombia - Gonzalo (Masculina Dinámica)"
    ]
)

voice_mapping = {
    "México - Emiliano (Masculina Muy Profunda / Épica y Documental)": "es-MX-EmilianoNeural",
    "México - Jorge (Masculina Profunda y Clara)": "es-MX-JorgeNeural",
    "Colombia - Carlos (Masculina Corporativa y Autoritaria / Graves)": "es-CO-CarlosNeural",
    "México - Lucia (Femenina con Graves / Misterio y Narrativa)": "es-MX-LuciaNeural",
    "México - Dalia (Femenina Natural y Fluida)": "es-MX-DaliaNeural",
    "Colombia - Gonzalo (Masculina Dinámica)": "es-CO-GonzaloNeural"
}

selected_voice_id = voice_mapping.get(voice_option, "es-MX-EmilianoNeural")

def generate_scene_image_multi(visual_prompt, style_name, provider):
    final_prompt = f"{visual_prompt}, in {style_name} style, vertical 9:16 format, highly detailed, dramatic lighting, cinematic composition"
    
    # 1. DALL-E 3 de OpenAI
    if provider == "OpenAI DALL-E 3 (Alta Calidad)" and openai_client:
        try:
            response = openai_client.images.generate(
                model="dall-e-3",
                prompt=final_prompt,
                size="1024x1792",
                quality="standard",
                n=1,
            )
            image_url = response.data[0].url
            img_data = requests.get(image_url).content
            temp_img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
            with open(temp_img_path, "wb") as f:
                f.write(img_data)
            img = Image.open(temp_img_path).convert("RGB")
            return img.resize((1080, 1920), Image.Resampling.LANCZOS)
        except Exception:
            pass

    # 2. Google Gemini Flash Image
    elif provider == "Google Gemini (flash-image nativo)" and gemini_client:
        try:
            response = gemini_client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=final_prompt,
                config=types.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"]),
            )
            for part in response.candidates[0].content.parts:
                if part.inline_data:
                    image_bytes = base64.b64decode(part.inline_data.data)
                    temp_img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                    with open(temp_img_path, "wb") as f:
                        f.write(image_bytes)
                    img = Image.open(temp_img_path).convert("RGB")
                    return img.resize((1080, 1920), Image.Resampling.LANCZOS)
        except Exception:
            pass

    # 3. Modelos Open Source / Ecosistema Meta vía OpenRouter
    elif provider == "Modelos Open Source (FLUX / Llama Ecosystem via OpenRouter)" and openrouter_client:
        try:
            response = openrouter_client.images.generate(
                model="stabilityai/stable-diffusion-3-medium",
                prompt=final_prompt,
                size="1024x1024"
            )
            image_url = response.data[0].url
            img_data = requests.get(image_url).content
            temp_img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
            with open(temp_img_path, "wb") as f:
                f.write(img_data)
            img = Image.open(temp_img_path).convert("RGB")
            return img.resize((1080, 1920), Image.Resampling.LANCZOS)
        except Exception:
            pass

    # 4. Cloudflare
    elif provider == "Cloudflare Workers AI (Serverless)" and cloudflare_api_token and cloudflare_account_id:
        try:
            url = f"https://api.cloudflare.com/client/v4/accounts/{cloudflare_account_id}/ai/run/@cf/bytedance/stable-diffusion-xl-lightning"
            headers = {"Authorization": f"Bearer {cloudflare_api_token}"}
            payload = {"prompt": final_prompt, "width": 768, "height": 1344}
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                temp_img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
                with open(temp_img_path, "wb") as f:
                    f.write(response.content)
                img = Image.open(temp_img_path).convert("RGB")
                return img.resize((1080, 1920), Image.Resampling.LANCZOS)
        except Exception:
            pass

    # Respaldo por defecto si falla
    img = Image.new('RGB', (1080, 1920), color=(15, 22, 38))
    draw = ImageDraw.Draw(img)
    for y in range(0, 1920, 10):
        r = int(15 + (y / 1920) * 30)
        g = int(22 + (y / 1920) * 20)
        b = int(38 + (y / 1920) * 50)
        draw.rectangle([0, y, 1080, y + 10], fill=(r, g, b))
    return img

if st.button("🚀 Generar Reel Pro (60s)"):
    with st.spinner("Paso 1/5: Creando guion optimizado (Gemini -> OpenAI -> Groq)..."):
        try:
            prompt = (
                f"Actúa como un experto productor de contenidos virales para Reels y TikTok. "
                f"Escribe un guion dinámico y completo de exactamente 7 escenas sobre el tema: '{user_topic}', adaptado al estilo visual: '{visual_style}'. "
                "ESTRUCTURA OBLIGATORIA PARA 60 SEGUNDOS:\n"
                "- ESCENA 1 (Gancho): Pregunta o afirmación impactante (aprox. 30 palabras).\n"
                "- ESCENA 2 (Punto 1 - Explicación): Desarrollo del primer concepto (aprox. 30 palabras).\n"
                "- ESCENA 3 (Punto 1 - Ejemplo): Aplicación práctica del primer concepto (aprox. 30 palabras).\n"
                "- ESCENA 4 (Punto 2 - Explicación): Desarrollo del segundo concepto (aprox. 30 palabras).\n"
                "- ESCENA 5 (Punto 2 - Ejemplo): Aplicación práctica del segundo concepto (aprox. 30 palabras).\n"
                "- ESCENA 6 (Punto 3 o Reflexión): Conclusión o cierre del desarrollo central (aprox. 30 palabras).\n"
                "- ESCENA 7 (Cierre / CTA): Llamado a la acción claro para interactuar (aprox. 25 palabras).\n"
                "REQUISITOS:\n"
                "- Todo el texto de voz en off (VO) debe estar estrictamente en MAYÚSCULAS.\n"
                "- Cada escena debe incluir un prompt visual detallado en INGLÉS para generar la imagen.\n"
                "Devuelve la respuesta estrictamente separada por líneas con este formato exacto:\n"
                "ESCENA 1 | [TEXTO DE VOZ EN OFF] | [Prompt visual detallado en inglés]\n"
                "ESCENA 2 | [TEXTO DE VOZ EN OFF] | [Prompt visual detallado en inglés]\n"
                "ESCENA 3 | [TEXTO DE VOZ EN OFF] | [Prompt visual detallado en inglés]\n"
                "ESCENA 4 | [TEXTO DE VOZ EN OFF] | [Prompt visual detallado en inglés]\n"
                "ESCENA 5 | [TEXTO DE VOZ EN OFF] | [Prompt visual detallado en inglés]\n"
                "ESCENA 6 | [TEXTO DE VOZ EN OFF] | [Prompt visual detallado en inglés]\n"
                "ESCENA 7 | [TEXTO DE VOZ EN OFF] | [Prompt visual detallado en inglés]"
            )
            
            raw_output = None
            
            # 1. Gemini
            if gemini_client and not raw_output:
                for model_name in ["gemini-2.0-flash", "gemini-1.5-flash"]:
                    try:
                        res = gemini_client.models.generate_content(model=model_name, contents=prompt)
                        raw_output = res.text.strip()
                        break
                    except Exception:
                        continue

            # 2. OpenAI
            if not raw_output and openai_client:
                try:
                    comp = openai_client.chat.completions.create(
                        model="gpt-4o",
                        messages=[
                            {"role": "system", "content": "Eres un guionista profesional de contenidos virales."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    raw_output = comp.choices[0].message.content.strip()
                except Exception:
                    pass

            # 3. Groq
            if not raw_output and groq_client:
                try:
                    comp = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "Eres un guionista profesional."}, {"role": "user", "content": prompt}]
                    )
                    raw_output = comp.choices[0].message.content.strip()
                except Exception:
                    pass

            if not raw_output:
                raise Exception("No se pudo generar el guion con ninguna de las APIs configuradas.")

            scenes_data = []
            for line in raw_output.split("\n"):
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        scenes_data.append({"text": parts[1].strip().upper(), "visual": parts[2].strip()})
            
            if not scenes_data:
                raise Exception("El formato del guion devuelto no pudo ser interpretado.")

            full_narration = " ".join([s["text"] for s in scenes_data])

            with st.spinner("Paso 2/5: Sintetizando locución neuronal..."):
                audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                try:
                    asyncio.run(generate_neural_voice_robust(full_narration, selected_voice_id, audio_path))
                except Exception:
                    asyncio.run(generate_neural_voice_robust(full_narration, "es-MX-DaliaNeural", audio_path))
                
                audio_clip = AudioFileClip(audio_path)
                total_duration = audio_clip.duration
                scene_duration = total_duration / len(scenes_data)

            with st.spinner(f"Paso 3/5: Generando imágenes con '{image_provider}'..."):
                clip_list = []
                
                for i, scene in enumerate(scenes_data):
                    img_pil = generate_scene_image_multi(scene['visual'], visual_style, image_provider)
                    
                    try:
                        txt_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
                        draw = ImageDraw.Draw(txt_layer)
                        
                        try:
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 65)
                        except:
                            font = ImageFont.load_default()

                        wrapped_text = textwrap.fill(scene['text'], width=16)
                        
                        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
                        tw = bbox[2] - bbox[0]
                        th = bbox[3] - bbox[1]
                        
                        x = (1080 - tw) / 2
                        y = 1200
                        
                        draw.rounded_rectangle(
                            [x - 50, y - 30, x + tw + 50, y + th + 30],
                            radius=30,
                            fill=(10, 10, 10, 230)
                        )
                        
                        for ox in range(-4, 5):
                            for oy in range(-4, 5):
                                if ox != 0 or oy != 0:
                                    draw.multiline_text((x + ox, y + oy), wrapped_text, font=font, fill=(0, 0, 0, 255), align="center")
                        
                        draw.multiline_text((x, y), wrapped_text, font=font, fill=(255, 230, 0, 255), align="center")
                        
                        img_pil = Image.alpha_composite(img_pil.convert("RGBA"), txt_layer).convert("RGB")
                    except Exception:
                        pass

                    img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                    img_pil.save(img_path)
                    
                    img_clip = ImageClip(img_path).with_duration(scene_duration)
                    clip_list.append(img_clip)

                final_visual = concatenate_videoclips(clip_list)
                final_video = final_visual.with_audio(audio_clip)

            with st.spinner("Paso 5/5: Renderizando video final y empaquetando documento..."):
                output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                final_video.write_videofile(
                    output_path,
                    fps=24,
                    codec="libx264",
                    audio_codec="aac",
                    preset="ultrafast",
                    logger=None
                )
                
                doc_content = f"# PROYECTO DE REEL / TIKTOK (60 SEGUNDOS)\n\n"
                doc_content += f"**Tema principal:** {user_topic}\n"
                doc_content += f"**Estilo Visual:** {visual_style}\n"
                doc_content += f"**Proveedor de Imágenes:** {image_provider}\n"
                doc_content += f"**Voz Neuronal Seleccionada:** {voice_option} (`{selected_voice_id}`)\n"
                doc_content += f"**Duración Total:** {int(total_duration)} segundos\n\n"
                doc_content += "=" * 50 + "\n\n## GUION Y DESGLOSE POR ESCENAS\n\n"
                
                current_time = 0.0
                for i, scene in enumerate(scenes_data):
                    start_t = current_time
                    end_t = current_time + scene_duration
                    doc_content += f"### Escena {i+1} ({start_t:.1f}s - {end_t:.1f}s)\n"
                    doc_content += f"- **Voz en Off (VO):** {scene['text']}\n"
                    doc_content += f"- **Prompt Visual (IA):** {scene['visual']}\n\n"
                    current_time = end_t

                doc_file_path = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="w", encoding="utf-8")
                doc_file_path.write(doc_content)
                doc_file_path.close()

                st.success(f"¡Reel generado con éxito! Duración total: {int(total_duration)} segundos.")
                st.video(output_path)
                
                col1, col2 = st.columns(2)
                with col1:
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label="📥 Descargar Reel (.mp4)",
                            data=file,
                            file_name="reel_pro_60s.mp4",
                            mime="video/mp4"
                        )
                with col2:
                    with open(doc_file_path.name, "rb") as file_doc:
                        st.download_button(
                            label="📄 Descargar Guion y Prompts (.txt)",
                            data=file_doc,
                            file_name="guion_y_prompts_proyecto.txt",
                            mime="text/plain"
                        )

        except Exception as e:
            st.error(f"Error durante el proceso de generación: {e}")
