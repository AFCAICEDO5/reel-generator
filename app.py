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
    page_title="Generador de Reels de 60s",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador de Reels Completos (60 Segundos)")
st.markdown("Genera tu locución fluida de 60s, transiciones por escena y subtítulos gigantes estilo TikTok sin límites de API.")

async def generate_neural_voice(text, voice_name, output_path):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_path)

st.sidebar.header("🛠️ Configuración del Reel")

user_topic = st.sidebar.text_input(
    "1. Tema o idea principal del Reel:", 
    value="¿Qué pasa en tu mente cuando estás a punto de lograr tus sueños?"
)

video_style = st.sidebar.selectbox(
    "2. Estilo Visual de Fondos:",
    [
        "Cinemático / Oscuro Elegante",
        "Estilo Misterio / Neón",
        "Temática Espiritual / Galaxia",
        "Finanzas / Lujo Oscuro"
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

if st.button("🚀 Generar Reel Completo (60s)"):
    # 1. Estructurar guion de forma local dividiendo el texto ingresado o complementándolo para alcanzar los 60s
    with st.spinner("Paso 1/4: Preparando estructura de escenas para 60 segundos..."):
        base_phrases = [
            user_topic.upper(),
            "EL SECRETO ESTÁ EN NO RENDIRSE NUNCA",
            "CADA DÍA ES UNA NUEVA OPORTUNIDAD",
            "DESCUBRE LO QUE ERES CAPAZ DE LOGRAR",
            "EL FUTURO PERTENECE A QUIENES CREEN",
            "HAZ QUE CADA SEGUNDO CUENTE"
        ]
        
        # Si el usuario escribió un texto largo, lo fragmentamos dinámicamente en 6 escenas
        words = user_topic.split()
        if len(words) > 5:
            chunk_size = max(1, len(words) // 6)
            scenes_data = []
            for i in range(0, len(words), chunk_size):
                part = " ".join(words[i:i+chunk_size])
                if part:
                    scenes_data.append(part.upper())
            while len(scenes_data) < 6:
                scenes_data.append(base_phrases[len(scenes_data) % len(base_phrases)])
            scenes_data = scenes_data[:6]
        else:
            scenes_data = base_phrases

        full_narration = ". ".join(scenes_data)
        st.success(f"¡Guion estructurado con {len(scenes_data)} escenas clave de forma local!")

    # 2. Síntesis de Voz de Larga Duración
    with st.spinner("Paso 2/4: Sintetizando locución completa (aprox. 60s)..."):
        audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        asyncio.run(generate_neural_voice(full_narration, selected_voice_id, audio_path))
        
        audio_clip = AudioFileClip(audio_path)
        total_duration = min(audio_clip.duration, 60.0)
        scene_duration = total_duration / len(scenes_data)

    # 3. Renderizado de Escenas con Fondos y Subtítulos Gigantes
    with st.spinner("Paso 3/4: Generando escenas dinámicas y subtítulos gigantes estilo Reel..."):
        clip_list = []
        
        palette_map = {
            "Cinemático / Oscuro Elegante": ((10, 10, 15), (35, 35, 50)),
            "Estilo Misterio / Neón": ((15, 5, 25), (45, 10, 35)),
            "Temática Espiritual / Galaxia": ((5, 10, 30), (15, 30, 60)),
            "Finanzas / Lujo Oscuro": ((10, 15, 10), (20, 45, 25))
        }
        color_top, color_bottom = palette_map.get(video_style, ((10, 10, 15), (35, 35, 50)))

        for text_content in scenes_data:
            base_img = Image.new('RGB', (1080, 1920))
            draw_bg = ImageDraw.Draw(base_img)
            
            # Dibujar degradado vertical profesional
            for y_coord in range(1920):
                factor = y_coord / 1920
                r = int(color_top[0] * (1 - factor) + color_bottom[0] * factor)
                g = int(color_top[1] * (1 - factor) + color_bottom[1] * factor)
                b = int(color_top[2] * (1 - factor) + color_bottom[2] * factor)
                draw_bg.line([(0, y_coord), (1080, y_coord)], fill=(r, g, b))

            # Añadir subtítulos gigantes centrados con borde negro fuerte
            try:
                txt_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
                draw = ImageDraw.Draw(txt_layer)
                
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                try:
                    font = ImageFont.truetype(font_path, 130)
                except:
                    font = ImageFont.load_default()

                wrapped_text = textwrap.fill(text_content, width=10)
                
                bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (1080 - text_width) / 2
                y = (1920 - text_height) / 2 - 120
                
                # Contorno grueso alrededor del texto para máxima visibilidad
                outline_range = 12
                for adj_x in range(-outline_range, outline_range + 1):
                    for adj_y in range(-outline_range, outline_range + 1):
                        if adj_x != 0 or adj_y != 0:
                            draw.multiline_text((x + adj_x, y + adj_y), wrapped_text, font=font, fill=(0, 0, 0, 255), align="center")
                
                # Texto principal en blanco brillante
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

    # 4. Renderizado Final del Video
    with st.spinner("Paso 4/4: Renderizando archivo de video final en alta definición..."):
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        final_video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            logger=None
        )
        
        st.success("¡Reel completo generado con éxito sin restricciones de API!")
        st.video(output_path)
        
        with open(output_path, "rb") as file:
            st.download_button(
                label="📥 Descargar Reel Completo (.mp4)",
                data=file,
                file_name="reel_60s_completo.mp4",
                mime="video/mp4"
            )
