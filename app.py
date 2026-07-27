import streamlit as st
import os
import tempfile
import asyncio
import edge_tts
from google import genai
from moviepy import (
    AudioFileClip, ImageClip, concatenate_videoclips
)
from PIL import Image, ImageDraw, ImageFont
import textwrap

st.set_page_config(
    page_title="Generador Pro Híbrido de Reels",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador Pro Híbrido de Reels (IA + Imágenes Manuales)")
st.markdown("Genera el guion y los prompts hiperrealistas con Gemini, sube tus imágenes y crea un Reel de 60s perfecto para redes.")

api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ No se encontró la `GEMINI_API_KEY` en los Secrets de Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

async def generate_neural_voice(text, voice_name, output_path):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_path)

st.sidebar.header("🛠️ Configuración del Reel")

user_topic = st.sidebar.text_input(
    "1. Tema o idea principal del Reel:", 
    value="¿Qué secretos ocultos guarda el universo que la ciencia no te cuenta?"
)

video_style = st.sidebar.selectbox(
    "2. Estilo Visual:",
    [
        "Cinemático / Fotorrealista 8K (Estilo Película Épica)",
        "Terror Cósmico / Misterio Oscuro Hiperrealista",
        "Ciencia Ficción / Futurista Hyper-Detailed",
        "Finanzas / Lujo y Éxito Fotográfico Real"
    ]
)

voice_option = st.sidebar.selectbox(
    "3. Selecciona la Voz Neuronal (100% Humana y Latina):",
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

# --- PASO 1: Generar Guion y Prompts con Gemini (Una sola llamada segura) ---
st.subheader("📌 Paso 1: Generar Guion y Prompts Hiperrealistas con IA")
if st.button("✨ Generar Guion y Prompts con Gemini"):
    with st.spinner("Creando estructura y prompts detallados para tus imágenes..."):
        try:
            prompt = (
                f"Actúa como un director de cine experto en videos cortos virales. Crea un guion de exactamente 6 escenas "
                f"sobre el tema: '{user_topic}', adaptado al estilo: '{video_style}'. "
                "Para cada escena, escribe un texto corto y contundente en MAYÚSCULAS para los subtítulos, y un prompt detallado en inglés para generar la imagen en 8K fotorrealista. "
                "Devuelve la respuesta estrictamente con este formato por línea: "
                "ESCENA 1 | [TEXTO EN MAYÚSCULAS] | [Detailed 8k hyperrealistic photographic prompt for scene 1]\n"
                "ESCENA 2 | [TEXTO EN MAYÚSCULAS] | [Detailed 8k hyperrealistic photographic prompt for scene 2]\n"
                "ESCENA 3 | [TEXTO EN MAYÚSCULAS] | [Detailed 8k hyperrealistic photographic prompt for scene 3]\n"
                "ESCENA 4 | [TEXTO EN MAYÚSCULAS] | [Detailed 8k hyperrealistic photographic prompt for scene 4]\n"
                "ESCENA 5 | [TEXTO EN MAYÚSCULAS] | [Detailed 8k hyperrealistic photographic prompt for scene 5]\n"
                "ESCENA 6 | [TEXTO EN MAYÚSCULAS] | [Detailed 8k hyperrealistic photographic prompt for scene 6]"
            )
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            st.session_state['ai_output'] = response.text.strip()
            st.success("¡Guion y prompts generados con éxito! Cópialos abajo para generar tus imágenes en Midjourney, ChatGPT o la herramienta que prefieras.")
        except Exception as e:
            st.error(f"Error al generar con Gemini: {e}")

if 'ai_output' in st.session_state:
    st.text_area("Copia estos prompts para tus imágenes:", st.session_state['ai_output'], height=200)

st.markdown("---")

# --- PASO 2: Carga Manual de Imágenes y Ensamblaje del Video ---
st.subheader("🖼️ Paso 2: Sube tus 6 Imágenes Hiperrealistas (Formato Vertical 9:16)")
uploaded_files = st.file_uploader(
    "Sube exactamente 6 imágenes (para las 6 escenas del guion):", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if st.button("🚀 Renderizar Reel Completo (60s)"):
    if not uploaded_files or len(uploaded_files) != 6:
        st.warning("⚠️ Por favor sube exactamente 6 imágenes para completar las escenas del video.")
    else:
        with st.spinner("Paso 1/3: Procesando guion y locución con voz neuronal..."):
            # Extraer textos base de la salida de IA si existe, o usar predeterminados robustos
            texts_data = [
                user_topic.upper(),
                "EL SECRETO QUE NADIE SE ATREVE A CONTAR",
                "CADA DETALLE CAMBIA NUESTRA REALIDAD",
                "DESCUBRE LO QUE SE OCULTA TRAS LA VISTA",
                "EL FUTURO PERTENECE A QUIENES INVESTIGAN",
                "COMPARTE ESTE MENSAJE AHORA MISMO"
            ]
            
            if 'ai_output' in st.session_state:
                parsed_texts = []
                for line in st.session_state['ai_output'].split("\n"):
                    if "|" in line:
                        parts = line.split("|")
                        if len(parts) >= 2:
                            parsed_texts.append(parts[1].strip().upper())
                if len(parsed_texts) >= 6:
                    texts_data = parsed_texts[:6]

            full_narration = ". ".join(texts_data)
            
            audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
            asyncio.run(generate_neural_voice(full_narration, selected_voice_id, audio_path))
            
            audio_clip = AudioFileClip(audio_path)
            total_duration = min(audio_clip.duration, 60.0)
            scene_duration = total_duration / len(uploaded_files)

        with st.spinner("Paso 2/3: Adaptando imágenes a 9:16 y aplicando subtítulos gigantes estilo Reel..."):
            clip_list = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                # Guardar imagen subida temporalmente
                img_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                img_temp.write(uploaded_file.read())
                img_temp.close()
                
                # Procesar imagen con Pillow para asegurar tamaño vertical exacto (1080x1920) y subtítulos
                try:
                    img_pil = Image.open(img_temp.name).convert("RGB")
                    # Redimensionar y recortar inteligentemente a proporción vertical 9:16
                    img_pil = img_pil.resize((1080, 1920), Image.Resampling.LANCZOS)
                    
                    txt_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(txt_layer)
                    
                    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                    try:
                        font = ImageFont.truetype(font_path, 130)
                    except:
                        font = ImageFont.load_default()

                    text_content = texts_data[i] if i < len(texts_data) else "VISIÓN HIPERREALISTA"
                    wrapped_text = textwrap.fill(text_content, width=9)
                    
                    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    x = (1080 - text_width) / 2
                    y = (1920 - text_height) / 2 - 120
                    
                    # Contorno negro grueso para máxima visibilidad en móviles
                    outline_range = 14
                    for adj_x in range(-outline_range, outline_range + 1):
                        for adj_y in range(-outline_range, outline_range + 1):
                            if adj_x != 0 or adj_y != 0:
                                draw.multiline_text((x + adj_x, y + adj_y), wrapped_text, font=font, fill=(0, 0, 0, 255), align="center")
                    
                    # Texto principal blanco brillante
                    draw.multiline_text((x, y), wrapped_text, font=font, fill=(255, 255, 255, 255), align="center")
                    
                    final_scene_img = Image.alpha_composite(img_pil.convert("RGBA"), txt_layer).convert("RGB")
                    final_img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                    final_scene_img.save(final_img_path)
                    
                    img_clip = ImageClip(final_img_path).with_duration(scene_duration)
                except Exception:
                    img_clip = ImageClip(img_temp.name).with_duration(scene_duration)

                clip_list.append(img_clip)

            final_visual = concatenate_videoclips(clip_list)
            final_video = final_visual.with_audio(audio_clip)

        with st.spinner("Paso 3/3: Renderizando video final en alta definición..."):
            output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            final_video.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                preset="ultrafast",
                logger=None
            )
            
            st.success("¡Reel Híbrido Pro generado con éxito!")
            st.video(output_path)
            
            with open(output_path, "rb") as file:
                st.download_button(
                    label="📥 Descargar Reel Pro (9:16 .mp4)",
                    data=file,
                    file_name="reel_hibrido_pro.mp4",
                    mime="video/mp4"
                )
