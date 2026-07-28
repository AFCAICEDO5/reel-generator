import streamlit as st
import os
import tempfile
import asyncio
import edge_tts
from google import genai
from openai import OpenAI
from moviepy import AudioFileClip, ImageClip, concatenate_videoclips
from PIL import Image, ImageDraw, ImageFont
import textwrap
import random

st.set_page_config(
    page_title="Generador de Reels Profesional (60 Segundos Ampliados)",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador de Reels Viral & Ampliado (60s)")
st.markdown("Crea videos con guiones profundos, voz neuronal de alta retención, fondos temáticos y subtítulos estilo TikTok.")

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
        "Terror",
        "Fantasía",
        "Minecraft",
        "Pixel Art",
        "Biblia / Religioso",
        "Cómic",
        "Cartoon"
    ]
)

voice_option = st.sidebar.selectbox(
    "Selecciona la Voz Neuronal:",
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
    "México - Gonzalo (Masculina Dinámica)": "es-CO-GonzaloNeural",
    "México - Salome (Femenina Cálida)": "es-CO-SalomeNeural",
    "Argentina - Tomás (Masculina Cercana)": "es-AR-TomasNeural"
}

selected_voice_id = voice_mapping.get(voice_option, "es-MX-DaliaNeural")

def create_styled_background(style_name, scene_index):
    img = Image.new('RGB', (1080, 1920), color=(12, 12, 18))
    draw = ImageDraw.Draw(img)
    
    palettes = {
        "Cinematográfico": [(15, 22, 38), (45, 32, 65), (10, 10, 15)],
        "Fotorrealista": [(22, 28, 35), (55, 65, 75), (12, 14, 18)],
        "Anime": [(65, 22, 85), (22, 75, 110), (22, 12, 32)],
        "Ciencia Ficción": [(8, 32, 55), (12, 65, 88), (3, 12, 22)],
        "Terror Oscuro": [(12, 6, 6), (32, 12, 12), (6, 3, 3)],
        "Terror": [(22, 6, 12), (42, 16, 22), (12, 3, 6)],
        "Fantasía": [(42, 22, 65), (85, 42, 95), (22, 12, 32)],
        "Minecraft": [(55, 125, 55), (105, 85, 55), (32, 85, 32)],
        "Pixel Art": [(32, 32, 55), (75, 55, 95), (16, 16, 32)],
        "Biblia / Religioso": [(55, 42, 22), (95, 75, 32), (22, 16, 12)],
        "Cómic": [(85, 22, 22), (22, 42, 85), (12, 12, 12)],
        "Cartoon": [(95, 52, 105), (32, 85, 125), (42, 22, 55)]
    }
    
    colors = palettes.get(style_name, [(15, 22, 38), (45, 32, 65), (10, 10, 15)])
    c1 = colors[scene_index % len(colors)]
    c2 = colors[(scene_index + 1) % len(colors)]
    
    for y in range(0, 1920, 10):
        factor = y / 1920.0
        r = int(c1[0] * (1 - factor) + c2[0] * factor)
        g = int(c1[1] * (1 - factor) + c2[1] * factor)
        b = int(c1[2] * (1 - factor) + c2[2] * factor)
        draw.rectangle([0, y, 1080, y + 10], fill=(r, g, b))
        
    for _ in range(12):
        rx = random.randint(0, 1080)
        ry = random.randint(0, 1920)
        rw = random.randint(60, 350)
        rh = random.randint(60, 350)
        draw.ellipse([rx, ry, rx + rw, ry + rh], fill=(255, 255, 255, 18))

    return img

if st.button("🚀 Generar Reel Ampliado (60s)"):
    with st.spinner("Paso 1/4: Generando guion ampliado de alto impacto (Gancho + Desarrollo Profundo + CTA)..."):
        try:
            prompt = (
                f"Actúa como un experto productor de contenidos virales para Reels y TikTok. "
                f"Escribe un guion dinámico, persuasivo y muy completo de exactamente 7 escenas sobre el tema: '{user_topic}', adaptado al estilo visual: '{visual_style}'. "
                "ESTRUCTURA OBLIGATORIA PARA ALCANZAR 60 SEGUNDOS EXACTOS:\n"
                "- ESCENA 1 (Gancho): Pregunta o afirmación impactante para retener en los primeros 8 segundos (aprox. 30-35 palabras).\n"
                "- ESCENA 2 (Punto 1 - Explicación): Desarrollo detallado del primer concepto clave (aprox. 30-35 palabras).\n"
                "- ESCENA 3 (Punto 1 - Ejemplo): Aplicación práctica o beneficio directo del primer concepto (aprox. 30-35 palabras).\n"
                "- ESCENA 4 (Punto 2 - Explicación): Desarrollo detallado del segundo concepto clave (aprox. 30-35 palabras).\n"
                "- ESCENA 5 (Punto 2 - Ejemplo): Aplicación práctica o beneficio directo del segundo concepto (aprox. 30-35 palabras).\n"
                "- ESCENA 6 (Punto 3 o Reflexión): Conclusión analítica o cierre del desarrollo central (aprox. 30-35 palabras).\n"
                "- ESCENA 7 (Cierre / CTA): Llamado a la acción claro, cercano y profesional para invitar a comentar (aprox. 25-30 palabras).\n"
                "REQUISITOS:\n"
                "- Todo el texto de voz en off (VO) debe estar estrictamente en MAYÚSCULAS.\n"
                "- El tono debe ser conversacional, magnético y de alta retención.\n"
                "- Cada escena debe incluir un prompt visual detallado en inglés acorde al estilo '{visual_style}'.\n"
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
            
            if gemini_client and not raw_output:
                for model_name in ["gemini-2.0-flash", "gemini-1.5-flash"]:
                    try:
                        res = gemini_client.models.generate_content(model=model_name, contents=prompt)
                        raw_output = res.text.strip()
                        break
                    except Exception:
                        continue

            if not raw_output and groq_client:
                try:
                    comp = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "system", "content": "Eres un guionista profesional de TikTok."}, {"role": "user", "content": prompt}]
                    )
                    raw_output = comp.choices[0].message.content.strip()
                except Exception:
                    pass

            if not raw_output and openrouter_client:
                try:
                    comp = openrouter_client.chat.completions.create(
                        model="meta-llama/llama-3.3-70b-instruct:free",
                        messages=[{"role": "system", "content": "Eres un guionista profesional de TikTok."}, {"role": "user", "content": prompt}]
                    )
                    raw_output = comp.choices[0].message.content.strip()
                except Exception:
                    pass

            if not raw_output:
                raise Exception("No se pudo generar el guion ampliado con ningún proveedor.")

            st.success("¡Guion ampliado de 60s generado con éxito!")
            st.text_area("Desglose del Guion Ampliado (JSON / Formato API de Escenas):", raw_output, height=200)

            scenes_data = []
            for line in raw_output.split("\n"):
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        scenes_data.append({"text": parts[1].strip().upper(), "visual": parts[2].strip()})
            
            if not scenes_data:
                raise Exception("El formato del guion devuelto no pudo ser interpretado.")

            full_narration = " ".join([s["text"] for s in scenes_data])

            with st.spinner("Paso 2/4: Sintetizando locución extendida de 60 segundos..."):
                audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                asyncio.run(generate_neural_voice(full_narration, selected_voice_id, audio_path))
                
                audio_clip = AudioFileClip(audio_path)
                total_duration = audio_clip.duration
                scene_duration = total_duration / len(scenes_data)

            with st.spinner("Paso 3/4: Renderizando imágenes temáticas y subtítulos dinámicos estilo TikTok..."):
                clip_list = []
                
                for i, scene in enumerate(scenes_data):
                    img_pil = create_styled_background(visual_style, i)
                    
                    try:
                        txt_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
                        draw = ImageDraw.Draw(txt_layer)
                        
                        try:
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 75)
                        except:
                            font = ImageFont.load_default()

                        wrapped_text = textwrap.fill(scene['text'], width=18)
                        
                        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
                        tw = bbox[2] - bbox[0]
                        th = bbox[3] - bbox[1]
                        
                        x = (1080 - tw) / 2
                        y = 1250
                        
                        draw.rounded_rectangle(
                            [x - 40, y - 25, x + tw + 40, y + th + 25],
                            radius=25,
                            fill=(0, 0, 0, 210)
                        )
                        
                        for ox in range(-5, 6):
                            for oy in range(-5, 6):
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

            with st.spinner("Paso 4/4: Exportando video final en alta definición..."):
                output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
                final_video.write_videofile(
                    output_path,
                    fps=24,
                    codec="libx264",
                    audio_codec="aac",
                    preset="ultrafast",
                    logger=None
                )
                
                st.success(f"¡Reel ampliado generado con éxito! Duración total: {int(total_duration)} segundos.")
                st.video(output_path)
                
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Descargar Reel de 60s (.mp4)",
                        data=file,
                        file_name="reel_ampliado_60s.mp4",
                        mime="video/mp4"
                    )

        except Exception as e:
            st.error(f"Error durante el proceso de generación: {e}")
