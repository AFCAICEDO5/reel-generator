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
import random

st.set_page_config(
    page_title="Generador de Reels Profesional (Gancho + CTA + Estilos)",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador de Reels Profesional & Viral")
st.markdown("Guion estructurado (Gancho + Desarrollo + CTA), estilos visuales avanzados y subtítulos estilo TikTok.")

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
    value="El misterio oculto detrás de las decisiones que cambian tu vida para siempre."
)

visual_style = st.sidebar.selectbox(
    "2. Estilo Visual de las Imágenes:",
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

def create_styled_background(style_name, scene_index):
    """Crea un fondo visual profesional adaptado al estilo seleccionado con efectos artísticos."""
    img = Image.new('RGB', (1080, 1920), color=(10, 10, 15))
    draw = ImageDraw.Draw(img)
    
    # Definir paletas según el estilo
    palettes = {
        "Cinematográfico": [(15, 20, 35), (40, 30, 60), (10, 10, 15)],
        "Fotorrealista": [(20, 25, 30), (50, 60, 70), (10, 12, 15)],
        "Anime": [(60, 20, 80), (20, 70, 100), (20, 10, 30)],
        "Ciencia Ficción": [(5, 30, 50), (10, 60, 80), (2, 10, 20)],
        "Terror Oscuro": [(10, 5, 5), (30, 10, 10), (5, 2, 2)],
        "Terror": [(20, 5, 10), (40, 15, 20), (10, 2, 5)],
        "Fantasía": [(40, 20, 60), (80, 40, 90), (20, 10, 30)],
        "Minecraft": [(50, 120, 50), (100, 80, 50), (30, 80, 30)],
        "Pixel Art": [(30, 30, 50), (70, 50, 90), (15, 15, 30)],
        "Biblia / Religioso": [(50, 40, 20), (90, 70, 30), (20, 15, 10)],
        "Cómic": [(80, 20, 20), (20, 40, 80), (10, 10, 10)],
        "Cartoon": [(90, 50, 100), (30, 80, 120), (40, 20, 50)]
    }
    
    colors = palettes.get(style_name, [(15, 20, 35), (40, 30, 60), (10, 10, 15)])
    c1 = colors[scene_index % len(colors)]
    c2 = colors[(scene_index + 1) % len(colors)]
    
    # Degradado vertical simulado por bloques de color estilizados
    for y in range(0, 1920, 10):
        factor = y / 1920.0
        r = int(c1[0] * (1 - factor) + c2[0] * factor)
        g = int(c1[1] * (1 - factor) + c2[1] * factor)
        b = int(c1[2] * (1 - factor) + c2[2] * factor)
        draw.rectangle([0, y, 1080, y + 10], fill=(r, g, b))
        
    # Añadir elementos geométricos abstractos según el estilo para darle textura visual única
    for _ in range(15):
        rx = random.randint(0, 1080)
        ry = random.randint(0, 1920)
        rw = random.randint(50, 400)
        rh = random.randint(50, 400)
        draw.ellipse([rx, ry, rx + rw, ry + rh], fill=(255, 255, 255, 15))

    return img

if st.button("🚀 Generar Reel Profesional (60s)"):
    with st.spinner("Paso 1/4: Creando guion profesional estructurado (Gancho + Desarrollo + CTA)..."):
        try:
            prompt = (
                f"Actúa como un productor ejecutivo experto en retención de audiencia para Reels y TikTok. "
                f"Escribe un guion fluido y atrapante de exactamente 6 escenas sobre el tema: '{user_topic}', diseñado bajo el estilo visual: '{visual_style}'. "
                "ESTRUCTURA OBLIGATORIA DEL GUION:\n"
                "- Escena 1 y 2: GANCHO VIRAL (Atraer la atención inmediata del espectador sin rodeos).\n"
                "- Escena 3 y 4: DESARROLLO DEL TEMA (Explicación profunda, dinámica y de alto valor).\n"
                "- Escena 5 y 6: CTA LIMPIO (Llamado a la acción profesional e inspirador para comentar o seguir).\n"
                "REQUISITOS:\n"
                "1. Cada escena debe tener un texto narrativo potente y natural en MAYÚSCULAS (de 15 a 25 palabras cada uno para garantizar ~60 segundos de locución).\n"
                "2. Cero tono aburrido de lectura; debe sonar conversacional, persuasivo y magnético.\n"
                "3. Incluye un prompt visual descriptivo en inglés enfocado en el estilo '{visual_style}'.\n"
                "Devuelve la respuesta estrictamente separada por líneas con este formato exacto:\n"
                "ESCENA 1 | [TEXTO NARRATIVO] | [Prompt visual en inglés]\n"
                "ESCENA 2 | [TEXTO NARRATIVO] | [Prompt visual en inglés]\n"
                "ESCENA 3 | [TEXTO NARRATIVO] | [Prompt visual en inglés]\n"
                "ESCENA 4 | [TEXTO NARRATIVO] | [Prompt visual en inglés]\n"
                "ESCENA 5 | [TEXTO NARRATIVO] | [Prompt visual en inglés]\n"
                "ESCENA 6 | [TEXTO NARRATIVO] | [Prompt visual en inglés]"
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
                        messages=[{"role": "system", "content": "Eres un productor viral experto."}, {"role": "user", "content": prompt}]
                    )
                    raw_output = comp.choices[0].message.content.strip()
                except Exception:
                    pass

            # Camino 3: OpenRouter
            if not raw_output and openrouter_client:
                try:
                    comp = openrouter_client.chat.completions.create(
                        model="meta-llama/llama-3.3-70b-instruct:free",
                        messages=[{"role": "system", "content": "Eres un productor viral experto."}, {"role": "user", "content": prompt}]
                    )
                    raw_output = comp.choices[0].message.content.strip()
                except Exception:
                    pass

            if not raw_output:
                raise Exception("No se pudo generar el guion con ningún proveedor disponible.")

            st.success("¡Guion profesional generado (Gancho + Desarrollo + CTA)!")
            st.text_area("Desglose del Guion:", raw_output, height=140)

            scenes_data = []
            for line in raw_output.split("\n"):
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 3:
                        scenes_data.append({"text": parts[1].strip().upper(), "visual": parts[2].strip()})
            
            if not scenes_data:
                raise Exception("Error al parsear el formato del guion.")

            full_narration = " ".join([s["text"] for s in scenes_data])

            with st.spinner("Paso 2/4: Sintetizando locución neuronal fluida de 60s..."):
                audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
                asyncio.run(generate_neural_voice(full_narration, selected_voice_id, audio_path))
                
                audio_clip = AudioFileClip(audio_path)
                total_duration = audio_clip.duration
                scene_duration = total_duration / len(scenes_data)

            with st.spinner("Paso 3/4: Renderizando imágenes temáticas y subtítulos estilo TikTok..."):
                clip_list = []
                
                for i, scene in enumerate(scenes_data):
                    # Generar imagen de fondo profesional basada en el estilo elegido
                    img_pil = create_styled_background(visual_style, i)
                    
                    try:
                        txt_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
                        draw = ImageDraw.Draw(txt_layer)
                        
                        try:
                            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 85)
                        except:
                            font = ImageFont.load_default()

                        # Subtítulos en formato dinámico estilo TikTok (tercio inferior central)
                        wrapped_text = textwrap.fill(scene['text'], width=16)
                        
                        bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
                        tw = bbox[2] - bbox[0]
                        th = bbox[3] - bbox[1]
                        
                        x = (1080 - tw) / 2
                        y = 1300  # Ubicación perfecta en la zona segura de Reels/TikTok
                        
                        # Caja de fondo oscura translúcida para máxima visibilidad
                        draw.rounded_rectangle(
                            [x - 35, y - 25, x + tw + 35, y + th + 25],
                            radius=25,
                            fill=(0, 0, 0, 200)
                        )
                        
                        # Efecto de texto con contorno fuerte y color amarillo vibrante
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
                
                st.success(f"¡Reel profesional generado con éxito! Duración total: {int(total_duration)} segundos.")
                st.video(output_path)
                
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="📥 Descargar Reel Profesional (.mp4)",
                        data=file,
                        file_name="reel_profesional_viral.mp4",
                        mime="video/mp4"
                    )

        except Exception as e:
            st.error(f"Error durante el proceso de generación: {e}")
