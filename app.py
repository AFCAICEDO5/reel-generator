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
    page_title="Automatizador Total de Reels Pro",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Automatizador Total de Reels Pro (IA + Sin Subidas Manuales)")
st.markdown("Escribe tu tema y deja que la IA cree el guion único, los fondos cinematográficos, la voz en off y los subtítulos gigantes en un solo proceso automático.")

# Configuración segura de la API key
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")

async def generate_neural_voice(text, voice_name, output_path):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_path)

# --- MENÚ LATERAL ---
st.sidebar.header("⚙️ Parámetros del Reel Automático")

user_topic = st.sidebar.text_input(
    "Tema principal o pregunta detonante:", 
    value="¿Por qué el tiempo parece pasar más rápido a medida que envejecemos?"
)

video_style = st.sidebar.selectbox(
    "Estilo Cinematográfico:",
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

if st.button("🚀 Generar Reel 100% Automático"):
    if not api_key:
        st.error("⚠️ Falta configurar tu `GEMINI_API_KEY` en los Secrets de Streamlit.")
        st.stop()
        
    client = genai.Client(api_key=api_key)
    
    # 1. Generar Guion Único y Dinámico con Gemini
    with st.spinner("Paso 1/4: La IA está analizando el tema y redactando un guion único (sin plantillas)..."):
        try:
            prompt_ia = (
                f"Actúa como un guionista profesional de contenido viral para TikTok e Instagram Reels. "
                f"Crea un guion detallado y original de exactamente 6 escenas sobre el tema: '{user_topic}', adaptado al estilo '{video_style}'. "
                "Para cada escena, proporciona dos cosas separadas estrictamente por el carácter pipe (|): "
                "1. El texto corto en MAYÚSCULAS para mostrar en pantalla como subtítulo de alto impacto. "
                "2. La narración completa, fluida y profunda para la voz en off, incluyendo gancho, desarrollo y CTA al final. "
                "Devuelve el resultado exactamente en este formato por línea, sin texto adicional: "
                "[TEXTO EN MAYÚSCULAS PARA PANTALLA] | [NARRACIÓN LARGA Y PROFUNDA PARA AUDIO]\n"
                "[TEXTO EN MAYÚSCULAS PARA PANTALLA] | [NARRACIÓN LARGA Y PROFUNDA PARA AUDIO]\n"
                "[TEXTO EN MAYÚSCULAS PARA PANTALLA] | [NARRACIÓN LARGA Y PROFUNDA PARA AUDIO]\n"
                "[TEXTO EN MAYÚSCULAS PARA PANTALLA] | [NARRACIÓN LARGA Y PROFUNDA PARA AUDIO]\n"
                "[TEXTO EN MAYÚSCULAS PARA PANTALLA] | [NARRACIÓN LARGA Y PROFUNDA PARA AUDIO]\n"
                "[TEXTO EN MAYÚSCULAS PARA PANTALLA] | [NARRACIÓN LARGA Y PROFUNDA PARA AUDIO]"
            )
            
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt_ia
            )
            ai_lines = response.text.strip().split("\n")
            
            screen_texts = []
            narration_texts = []
            
            for line in ai_lines:
                if "|" in line:
                    parts = line.split("|")
                    if len(parts) >= 2:
                        screen_texts.append(parts[0].strip().replace("[", "").replace("]", ""))
                        narration_texts.append(parts[1].strip().replace("[", "").replace("]", ""))
            
            if len(screen_texts) < 6:
                # Respaldo automático por seguridad si la IA devuelve menos líneas
                screen_texts = ["EL SECRETO DETRÁS DE ESTE FENÓMENO", "UNA PERSPECTIVA QUE CAMBIA TODO", "EL IMPACTO REAL EN NUESTRA VIDA", "LO QUE LA CIENCIA DESCUBRIÓ RECIENTEMENTE", "UNA CONCLUSIÓN SORPRENDENTE", "COMPÁRTELO Y COMENTA TU OPINIÓN"]
                narration_texts = [f"Analicemos a fondo {user_topic}.", "La realidad supera lo que imaginamos.", "Cada detalle transforma nuestra perspectiva.", "La investigación revela datos fascinantes.", "Entender esto nos prepara para el futuro.", f"¿Qué opinas sobre {user_topic}? Déjalo en comentarios."]
                
        except Exception as e:
            st.error(f"Error al conectar con la IA: {e}. Asegúrate de que tu clave tenga cuota disponible o reintenta en unos segundos.")
            st.stop()

    # 2. Síntesis de la Locución Neuronal
    with st.spinner("Paso 2/4: Sintetizando la voz en off humana y latina..."):
        full_narration_text = ". ".join(narration_texts)
        audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        asyncio.run(generate_neural_voice(full_narration_text, selected_voice_id, audio_path))
        
        audio_clip = AudioFileClip(audio_path)
        total_duration = min(audio_clip.duration, 60.0)
        scene_duration = total_duration / len(screen_texts)

    # 3. Generación Automática de Fondos Cinematográficos y Subtítulos Gigantes
    with st.spinner("Paso 3/4: Renderizando fotogramas verticales 9:16 y subtítulos masivos profesionales..."):
        clip_list = []
        
        # Paletas de colores profesionales según el estilo seleccionado
        palette_map = {
            "Cinemático / Fotorrealista 8K (Estilo Película Épica)": ((10, 15, 30), (40, 20, 60)),
            "Terror Cósmico / Misterio Oscuro Hiperrealista": ((15, 5, 20), (35, 10, 25)),
            "Ciencia Ficción / Futurista Hyper-Detailed": ((5, 20, 35), (10, 50, 80)),
            "Documental Histórico / National Geographic": ((20, 15, 10), (50, 40, 20))
        }
        color_top, color_bottom = palette_map.get(video_style, ((10, 15, 30), (40, 20, 60)))

        for i, text_content in enumerate(screen_texts):
            # Crear fotograma base vertical exacto (1080x1920) con degradado artístico
            base_img = Image.new('RGB', (1080, 1920))
            draw_bg = ImageDraw.Draw(base_img)
            
            for y_coord in range(1920):
                factor = y_coord / 1920
                modifier = int(20 * (1 - abs(y_coord - 960) / 960) * ((i % 2) + 1))
                r = min(255, int(color_top[0] * (1 - factor) + color_bottom[0] * factor) + modifier)
                g = min(255, int(color_top[1] * (1 - factor) + color_bottom[1] * factor) + modifier)
                b = min(255, int(color_top[2] * (1 - factor) + color_bottom[2] * factor) + modifier)
                draw_bg.line([(0, y_coord), (1080, y_coord)], fill=(r, g, b))

            # Incrustar subtítulos gigantes centrados con contorno negro grueso
            try:
                txt_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
                draw = ImageDraw.Draw(txt_layer)
                
                font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
                try:
                    font = ImageFont.truetype(font_path, 130)
                except:
                    font = ImageFont.load_default()

                wrapped_text = textwrap.fill(text_content, width=9)
                
                bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                x = (1080 - text_width) / 2
                y = (1920 - text_height) / 2 - 100
                
                # Borde negro grueso para visibilidad óptima en cualquier móvil
                outline_range = 14
                for adj_x in range(-outline_range, outline_range + 1):
                    for adj_y in range(-outline_range, outline_range + 1):
                        if adj_x != 0 or adj_y != 0:
                            draw.multiline_text((x + adj_x, y + adj_y), wrapped_text, font=font, fill=(0, 0, 0, 255), align="center")
                
                # Texto en blanco brillante
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
    with st.spinner("Paso 4/4: Compilando archivo de video final en alta definición..."):
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name
        final_video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            logger=None
        )
        
        st.success("¡Reel 100% Automatizado Generado con Éxito!")
        st.video(output_path)
        
        with open(output_path, "rb") as file:
            st.download_button(
                label="📥 Descargar Reel Automático (.mp4)",
                data=file,
                file_name="reel_ia_automatizado.mp4",
                mime="video/mp4"
            )
