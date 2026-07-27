import streamlit as st
import tempfile
import asyncio
import edge_tts
from moviepy import (
    AudioFileClip, ImageClip, concatenate_videoclips
)
from PIL import Image, ImageDraw, ImageFont
import textwrap

st.set_page_config(
    page_title="Generador Pro Dinámico de Reels",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador Pro Dinámico de Reels (Tema Libre)")
st.markdown("Escribe cualquier tema en el menú lateral. El sistema generará automáticamente los prompts hiperrealistas, el guion de 60s, y ensamblará tu video con voz neuronal y subtítulos gigantes.")

async def generate_neural_voice(text, voice_name, output_path):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_path)

# --- MENÚ LATERAL CONFIGURABLE ---
st.sidebar.header("🛠️ Configuración Dinámica")

user_topic = st.sidebar.text_input(
    "Escribe el Tema de tu Reel:", 
    value="La Inteligencia Artificial y el futuro de la humanidad"
)

video_style = st.sidebar.selectbox(
    "Estilo Visual e Hiperrealista:",
    [
        "Cinemático / Fotorrealista 8K (Estilo Película Épica)",
        "Terror Cósmico / Misterio Oscuro Hiperrealista",
        "Ciencia Ficción / Futurista Hyper-Detailed",
        "Documental Histórico / National Geographic"
    ]
)

voice_option = st.sidebar.selectbox(
    "Voz Neuronal (100% Humana y Latina):",
    [
        "México - Jorge (Masculina Profunda y Clara)",
        "México - Dalia (Femenina Natural y Fluida)",
        "Colombia - Gonzalo (Masculina Dinámica)",
        "Colombia - Salome (Femenina Cálida)",
        "Argentina - Tomás (Masculina Cercana)"
    ]
)

voice_mapping = {
    "México - Jorge (Masculina Profunda y Clara)": "es-MX-JorgeNeural",
    "México - Dalia (Femenina Natural y Fluida)": "es-MX-DaliaNeural",
    "Colombia - Gonzalo (Masculina Dinámica)": "es-CO-GonzaloNeural",
    "Colombia - Salome (Femenina Cálida)": "es-CO-SalomeNeural",
    "Argentina - Tomás (Masculina Cercana)": "es-AR-TomasNeural"
}

selected_voice_id = voice_mapping.get(voice_option, "es-MX-JorgeNeural")

# --- MOTOR DE GENERACIÓN AUTOMÁTICA DE GUIÓN Y PROMPTS BASADO EN EL TEMA ---
topic_clean = user_topic.strip()

# Generamos dinámicamente las 8 escenas adaptadas al tema ingresado por el usuario
scenes_config = [
    {
        "narration": f"Lo que está pasando con {topic_clean} va a cambiar por completo nuestra realidad para siempre.",
        "text": f"El impacto real de {topic_clean}",
        "prompt": f"Cinematic 8k hyperrealistic shot of {topic_clean}, dramatic lighting, photorealistic masterpiece, 9:16"
    },
    {
        "narration": "Nadie imaginó que la evolución de este proceso llegaría a este punto tan rápido y sorprendente.",
        "text": "Un avance sin precedentes",
        "prompt": f"Dramatic hyperdetailed 8k photography showing the evolution of {topic_clean}, cinematic lighting, raw photo, 9:16"
    },
    {
        "narration": "Expertos de todo el mundo advierten que los próximos años definirán un antes y un después absoluto.",
        "text": "Advertencia mundial",
        "prompt": f"High tech hyperrealistic concept art about {topic_clean}, dramatic shadows, 8k resolution, cinematic, 9:16"
    },
    {
        "narration": "Mientras algunos ven oportunidades infinitas, otros temen las consecuencias ocultas que esto conlleva.",
        "text": "Oportunidades y riesgos",
        "prompt": f"Epic mysterious atmosphere representing {topic_clean}, hyperdetailed textures, volumetric lighting, masterpiece, 9:16"
    },
    {
        "narration": "La historia demuestra que cada gran revolución tecnológica transforma por completo la estructura social.",
        "text": "Revolución tecnológica",
        "prompt": f"Documentary style professional shot related to {topic_clean}, National Geographic HDR quality, 9:16"
    },
    {
        "narration": "La pregunta clave que debemos hacernos hoy no es si sucederá, sino cómo nos adaptaremos a ello.",
        "text": "¿Estamos preparados?",
        "prompt": f"Futuristic cinematic view of {topic_clean}, hyperrealistic details, deep contrast, 8k quality, 9:16"
    },
    {
        "narration": "Aquellos que comprendan las reglas del juego a tiempo tendrán una ventaja incalculable en el futuro.",
        "text": "La ventaja del conocimiento",
        "prompt": f"Inspiring cinematic visual about {topic_clean}, golden hour lighting, ultra realistic textures, 9:16"
    },
    {
        "narration": f"¿Qué opinas tú sobre {topic_clean}? Déjalo en los comentarios y comparte este video.",
        "text": "¡Comenta y comparte tu opinión!",
        "prompt": f"Stunning hyperrealistic cinematic shot closing {topic_clean}, masterpiece, photorealistic, 9:16"
    }
]

st.markdown("---")
st.subheader("📌 Prompts Generados Automáticamente para tus 8 Imágenes")
st.info("Copia estos prompts y genera tus imágenes en Midjourney, ChatGPT, Leonardo AI o la herramienta de tu preferencia:")

# Mostrar en pantalla los prompts listos para copiar
prompts_text_display = "\n\n".join([f"ESCENA {i+1}:\nPrompt: {s['prompt']}\nTexto en pantalla: {s['text']}" for i, s in enumerate(scenes_config)])
st.text_area("Prompts optimizados (8 escenas):", prompts_text_display, height=200)

st.markdown("---")
st.subheader("🖼️ Sube tus 8 Imágenes Hiperrealistas (Formato Vertical 9:16)")

uploaded_files = st.file_uploader(
    "Sube exactamente las 8 imágenes correspondientes a las escenas:", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if st.button("🚀 Renderizar Reel Completo de 60s"):
    if not uploaded_files or len(uploaded_files) != 8:
        st.warning("⚠️ Debes subir exactamente 8 imágenes generadas para completar las 8 escenas.")
    else:
        with st.spinner("Paso 1/3: Sintetizando locución completa con voz neuronal (60s)..."):
            full_narration = ". ".join([s["narration"] for s in scenes_config])
            
            audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
            asyncio.run(generate_neural_voice(full_narration, selected_voice_id, audio_path))
            
            audio_clip = AudioFileClip(audio_path)
            total_duration = min(audio_clip.duration, 60.0)
            scene_duration = total_duration / 8.0

        with st.spinner("Paso 2/3: Ajustando a formato 9:16 e incrustando subtítulos gigantes..."):
            clip_list = []
            
            for i, uploaded_file in enumerate(uploaded_files):
                img_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
                img_temp.write(uploaded_file.read())
                img_temp.close()
                
                try:
                    img_pil = Image.open(img_temp.name).convert("RGB")
                    img_pil = img_pil.resize((1080, 1920), Image.Resampling.LANCZOS)
                    
                    txt_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
                    draw = ImageDraw.Draw(txt_layer)
                    
                    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                    try:
                        font = ImageFont.truetype(font_path, 120)
                    except:
                        font = ImageFont.load_default()

                    text_content = scenes_config[i]["text"].upper()
                    wrapped_text = textwrap.fill(text_content, width=10)
                    
                    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
                    text_width = bbox[2] - bbox[0]
                    text_height = bbox[3] - bbox[1]
                    
                    x = (1080 - text_width) / 2
                    y = (1920 - text_height) / 2 + 300
                    
                    # Contorno negro grueso (estilo profesional viral)
                    outline_range = 12
                    for adj_x in range(-outline_range, outline_range + 1):
                        for adj_y in range(-outline_range, outline_range + 1):
                            if adj_x != 0 or adj_y != 0:
                                draw.multiline_text((x + adj_x, y + adj_y), wrapped_text, font=font, fill=(0, 0, 0, 255), align="center")
                    
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
            
            st.success("¡Reel Dinámico generado con éxito!")
            st.video(output_path)
            
            with open(output_path, "rb") as file:
                st.download_button(
                    label="📥 Descargar Reel Dinámico (.mp4)",
                    data=file,
                    file_name="reel_dinamico_ia.mp4",
                    mime="video/mp4"
                )
