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
    page_title="Generador Pro Cinemático de Reels",
    page_icon="📜",
    layout="centered"
)

st.title("📜 Generador Pro Cinemático de Reels (8 Escenas / 60s)")
st.markdown("Sube tus 8 imágenes hiperrealistas y genera un Reel profesional con voz neuronal, subtítulos gigantes y duración extendida.")

async def generate_neural_voice(text, voice_name, output_path):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_path)

# --- MENÚ LATERAL RESTAURADO ---
st.sidebar.header("🛠️ Configuración del Reel")

user_topic = st.sidebar.text_input(
    "Título o Tema Principal:", 
    value="EL ORIGEN DE LA BIBLIA: LA HISTORIA DEL LIBRO QUE CAMBIó AL MUNDO"
)

voice_option = st.sidebar.selectbox(
    "Selecciona la Voz Neuronal (100% Humana y Latina):",
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

# Configuración exacta de las 8 escenas cinemáticas
scenes_config = [
    {
        "narration": "Hace más de tres mil quinientos años comenzó la historia del libro más leído de toda la humanidad... la Biblia.",
        "text": "¿Sabías que la Biblia tardó más de 1.500 años en escribirse?"
    },
    {
        "narration": "No fue escrita por una sola persona, sino por alrededor de cuarenta autores diferentes.",
        "text": "40 autores diferentes"
    },
    {
        "narration": "Reyes, pastores, pescadores, médicos y profetas dejaron por escrito el mensaje que transformaría generaciones.",
        "text": "Reyes • Pastores • Profetas • Apóstoles"
    },
    {
        "narration": "Los primeros libros fueron escritos principalmente en hebreo. Más tarde aparecieron textos en arameo y griego.",
        "text": "Hebreo • Arameo • Griego"
    },
    {
        "narration": "El Antiguo Testamento relata la creación, el pueblo de Israel y la promesa del glorioso Mesías.",
        "text": "La promesa del Salvador"
    },
    {
        "narration": "El Nuevo Testamento cuenta la vida, muerte y resurrección de Jesucristo, el acontecimiento que cambió la historia.",
        "text": "Jesucristo cambió la historia"
    },
    {
        "narration": "Miles de manuscritos antiguos han permitido conservar su contenido con una fidelidad extraordinaria hasta hoy.",
        "text": "Miles de manuscritos preservados"
    },
    {
        "narration": "Más que un libro, es un mensaje de esperanza que continúa transformando millones de vidas. Comenta y comparte.",
        "text": "La Biblia sigue cambiando vidas. ¿Ya descubriste su mensaje?"
    }
]

st.markdown("---")
st.subheader("🖼️ Carga Manual de las 8 Imágenes (Formato Vertical 9:16)")
st.info("Sube exactamente **8 imágenes** correspondientes a cada escena del guion.")

uploaded_files = st.file_uploader(
    "Sube tus 8 imágenes en orden (Escena 1 a la 8):", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if st.button("🚀 Renderizar Reel Cinemático Completo (60s)"):
    if not uploaded_files or len(uploaded_files) != 8:
        st.warning("⚠️ Debes subir exactamente 8 imágenes para las 8 escenas configuradas.")
    else:
        with st.spinner("Paso 1/3: Sintetizando locución completa con voz neuronal (50-60s)..."):
            full_narration = ". ".join([s["narration"] for s in scenes_config])
            
            audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
            asyncio.run(generate_neural_voice(full_narration, selected_voice_id, audio_path))
            
            audio_clip = AudioFileClip(audio_path)
            total_duration = min(audio_clip.duration, 60.0)
            scene_duration = total_duration / 8.0

        with st.spinner("Paso 2/3: Procesando formato 9:16 e incrustando subtítulos gigantes con contorno..."):
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
            
            st.success("¡Reel Cinemático de 60s generado con éxito!")
            st.video(output_path)
            
            with open(output_path, "rb") as file:
                st.download_button(
                    label="📥 Descargar Reel Cinemático (.mp4)",
                    data=file,
                    file_name="reel_cinematico_biblia.mp4",
                    mime="video/mp4"
                )
