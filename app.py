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
    page_title="Generador Pro Híbrido de Reels",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador Pro Híbrido de Reels (Sin Límites de API)")
st.markdown("Genera tu guion local, sube tus imágenes hiperrealistas y crea un Reel de 60s perfecto para redes.")

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

# --- PASO 1: Generador automático local de Prompts y Guion ---
st.subheader("📌 Paso 1: Prompts e Ideas de Escenas (Generados Localmente)")

# Creamos prompts profesionales listos para copiar a Midjourney o ChatGPT basados en el tema
base_prompts = [
    f"ESCENA 1 | {user_topic.upper()} | Cinematic 8k hyperrealistic shot of {user_topic}, dramatic lighting, photorealistic masterpiece",
    "ESCENA 2 | EL SECRETO QUE NADIE SE ATREVE A CONTAR | Dark mysterious cinematic atmosphere, hyperdetailed raw photo, 8k resolution",
    "ESCENA 3 | CADA DETALLE CAMBIA NUESTRA REALIDAD | Futuristic hyperdetailed 8k photography, cinematic masterpiece, dramatic shadows",
    "ESCENA 4 | DESCUBRE LO QUE SE OCULTA TRAS LA VISTA | Epic cosmic background, photorealistic 8k, cinematic lighting",
    "ESCENA 5 | EL FUTURO PERTENECE A QUIENES INVESTIGAN | High tech hyperrealistic concept art, dramatic 8k resolution, raw photo",
    "ESCENA 6 | COMPARTE ESTE MENSAJE AHORA MISMO | Stunning hyperrealistic 8k cinematic shot, masterpiece, photorealistic"
]

generated_prompts_text = "\n".join(base_prompts)
st.text_area("Copia estos prompts para generar tus 6 imágenes en Midjourney, ChatGPT o Leonardo AI:", generated_prompts_text, height=180)

st.markdown("---")

# --- PASO 2: Carga Manual de Imágenes y Ensamblaje del Video ---
st.subheader("🖼️ Paso 2: Sube tus 6 Imágenes Hiperrealistas (Formato Vertical 9:16)")
uploaded_files = st.file_uploader(
    "Sube exactamente 6 imágenes generadas:", 
    type=["jpg", "jpeg", "png"], 
    accept_multiple_files=True
)

if st.button("🚀 Renderizar Reel Completo (60s)"):
    if not uploaded_files or len(uploaded_files) != 6:
        st.warning("⚠️ Por favor sube exactamente 6 imágenes para completar las escenas del video.")
    else:
        with st.spinner("Paso 1/2: Procesando guion y locución con voz neuronal..."):
            texts_data = [
                user_topic.upper(),
                "EL SECRETO QUE NADIE SE ATREVE A CONTAR",
                "CADA DETALLE CAMBIA NUESTRA REALIDAD",
                "DESCUBRE LO QUE SE OCULTA TRAS LA VISTA",
                "EL FUTURO PERTENECE A QUIENES INVESTIGAN",
                "COMPARTE ESTE MENSAJE AHORA MISMO"
            ]

            full_narration = ". ".join(texts_data)
            
            audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
            asyncio.run(generate_neural_voice(full_narration, selected_voice_id, audio_path))
            
            audio_clip = AudioFileClip(audio_path)
            total_duration = min(audio_clip.duration, 60.0)
            scene_duration = total_duration / len(uploaded_files)

        with st.spinner("Paso 2/2: Adaptando imágenes a 9:16 y aplicando subtítulos gigantes estilo Reel..."):
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
                    
                    outline_range = 14
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

            output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
            final_video.write_videofile(
                output_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                preset="ultrafast",
                logger=None
            )
            
            st.success("¡Reel Híbrido Pro generado con éxito sin errores de API!")
            st.video(output_path)
            
            with open(output_path, "rb") as file:
                st.download_button(
                    label="📥 Descargar Reel Pro (9:16 .mp4)",
                    data=file,
                    file_name="reel_hibrido_pro.mp4",
                    mime="video/mp4"
                )
