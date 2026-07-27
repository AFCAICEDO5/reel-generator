import streamlit as st
import os
import tempfile
import asyncio
import edge_tts
from moviepy import (
    AudioFileClip, ImageClip, concatenate_videoclips
)
from PIL import Image, ImageDraw, ImageFont
import textwrap

st.set_page_config(
    page_title="Generador de Reels Local",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador de Reels (Sin Límites de API)")
st.markdown("Genera tus videos con voz neuronal y fondos profesionales generados localmente.")

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
        "Cinemático / Oscuro Elegante",
        "Estilo Misterio / Neón",
        "Temática Espiritual / Galaxia",
        "Finanzas / Minimalista Oscuro"
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

if st.button("🚀 Generar Reel Local (60s)"):
    with st.spinner("Paso 1/3: Creando estructura de escenas dinámicas..."):
        # Dividimos el texto ingresado en 4 partes lógicas para armar el video localmente sin consumir IA
        words = user_topic.split()
        chunk_size = max(1, len(words) // 4)
        scenes_text = []
        
        for i in range(0, len(words), chunk_size):
            part = " ".join(words[i:i+chunk_size])
            if part:
                scenes_text.append(part.upper())
        
        if len(scenes_text) == 0:
            scenes_text = [user_topic.upper()]
        
        # Aseguramos al menos 4 escenas para una buena duración
        while len(scenes_text) < 4:
            scenes_text.append(user_topic.upper())

        full_narration = " ".join(scenes_text)

    with st.spinner("Paso 2/3: Sintetizando locución con Voz Neuronal..."):
        audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        asyncio.run(generate_neural_voice(full_narration, selected_voice_id, audio_path))
        
        audio_clip = AudioFileClip(audio_path)
        total_duration = min(audio_clip.duration, 60)
        scene_duration = total_duration / len(scenes_text)

    with st.spinner("Paso 3/3: Renderizando fondos y subtítulos dinámicos..."):
        clip_list = []
        
        # Paletas de colores según el estilo seleccionado
        palette_map = {
            "Cinemático / Oscuro Elegante": ((15, 15, 20), (40, 40, 55)),
            "Estilo Misterio / Neón": ((10, 5, 20), (50, 10, 40)),
            "Temática Espiritual / Galaxia": ((5, 10, 25), (20, 40, 70)),
            "Finanzas / Minimalista Oscuro": ((10, 15, 10), (25, 50, 30))
        }
        color_top, color_bottom = palette_map.get(video_style, ((15, 15, 20), (40, 40, 55)))

        for i, text_content in enumerate(scenes_text):
            # Generación de fondo degradado profesional local
            base_img = Image.new('RGB', (1080, 1920))
            draw_bg = ImageDraw.Draw(base_img)
            
            for y_coord in range(1920):
                factor = y_coord / 1920
                r = int(color_top[0] * (1 - factor) + color_bottom[0] * factor)
                g = int(color_top[1] * (1 - factor) + color_bottom[1] * factor)
                b = int(color_top[2] * (1 - factor) + color_bottom[2] * factor)
                draw_bg.line([(0, y_coord), (1080, y_coord)], fill=(r, g, b))

            # Aplicar subtítulos gigantescos y centrados
            try:
                txt_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
                draw = ImageDraw.Draw(txt_layer)
                
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                try:
                    font = ImageFont.truetype(font_path, 120)
                except:
                    font = ImageFont.load_default()

                wrapped_text = textwrap.fill(text_content, width=12)
                
                bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (1080 - text_width) / 2
                y = (1920 - text_height) / 2 - 100
                
                # Sombra gruesa para legibilidad total
                outline_range = 10
                for adj_x in range(-outline_range, outline_range + 1):
                    for adj_y in range(-outline_range, outline_range + 1):
                        if adj_x != 0 or adj_y != 0:
                            draw.multiline_text((x + adj_x, y + adj_y), wrapped_text, font=font, fill=(0, 0, 0, 255), align="center")
                
                draw.multiline_text((x, y), wrapped_text, font=font, fill=(255, 255, 255, 255), align="center")
                
                final_scene_img = Image.alpha_composite(base_img.convert("RGBA"), txt_layer).convert("RGB")
                img_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                final_scene_img.save(img_path)
                
                img_clip = ImageClip(img_path).with_duration(scene_duration)
            except Exception:
                img_clip = ImageClip(base_img).with_duration(scene_duration)

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
        
        st.success("¡Reel generado con éxito sin restricciones de cuota!")
        st.video(output_path)
        
        with open(output_path, "rb") as file:
            st.download_button(
                label="📥 Descargar Reel (.mp4)",
                data=file,
                file_name="reel_local.mp4",
                mime="video/mp4"
            )
