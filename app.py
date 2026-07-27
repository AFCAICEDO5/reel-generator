import streamlit as st
import os
import tempfile
import asyncio
import edge_tts
from google import genai
from openai import OpenAI
from moviepy import (
    AudioFileClip, ImageClip, concatenate_videoclips
)
from PIL import Image, ImageDraw, ImageFont
import textwrap

st.set_page_config(
    page_title="Automatizador de Reels (Los 3 Caminos)",
    page_icon="⚡",
    layout="centered"
)

st.title("⚡ Automatizador Total de Reels (Sistema de 3 Caminos)")
st.markdown("El sistema intentará generar el guion único con **Gemini**. Si hay error de cuota, pasará automáticamente a **OpenAI**. Si ninguna tiene saldo, activará el **Respaldo Local** para que el video siempre se cree.")

# Credenciales seguras
gemini_api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")
openai_api_key = st.secrets.get("OPENAI_API_KEY") if "OPENAI_API_KEY" in st.secrets else os.environ.get("OPENAI_API_KEY")

async def generate_neural_voice(text, voice_name, output_path):
    communicate = edge_tts.Communicate(text, voice_name)
    await communicate.save(output_path)

# --- MENÚ LATERAL ---
st.sidebar.header("⚙️ Configuración del Reel")

user_topic = st.sidebar.text_input(
    "Tema principal o pregunta detonante:", 
    value="¿Por qué el tiempo parece pasar más rápido a medida que envejecemos?"
)

video_style = st.sidebar.selectbox(
    "Estilo Visual:",
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

if st.button("🚀 Generar Reel (Sistema de 3 Caminos)"):
    topic_clean = user_topic.strip()
    screen_texts = []
    narration_texts = []
    generation_method = ""

    prompt_ia = (
        f"Actúa como un guionista profesional de contenido viral para TikTok e Instagram Reels. "
        f"Crea un guion detallado y original de exactamente 6 escenas sobre el tema: '{topic_clean}', adaptado al estilo '{video_style}'. "
        "Para cada escena, proporciona dos cosas separadas estrictamente por el carácter pipe (|): "
        "1. El texto corto en MAYÚSCULAS para mostrar en pantalla como subtítulo de alto impacto. "
        "2. La narración completa, fluida y profunda para la voz en off, incluyendo gancho, desarrollo y CTA al final. "
        "Devuelve el resultado exactamente en este formato por línea, sin texto introductorio ni markdown extra: "
        "[TEXTO EN MAYÚSCULAS PARA PANTALLA] | [NARRACIÓN LARGA Y PROFUNDA PARA AUDIO]\n"
        "[TEXTO EN MAYÚSCULAS PARA PANTALLA] | [NARRACIÓN LARGA Y PROFUNDA PARA AUDIO]\n"
        "[TEXTO EN MAYÚSCULAS PARA PANTALLA] | [NARRACIÓN LARGA Y PROFUNDA PARA AUDIO]\n"
        "[TEXTO EN MAYÚSCULAS PARA PANTALLA] | [NARRACIÓN LARGA Y PROFUNDA PARA AUDIO]\n"
        "[TEXTO EN MAYÚSCULAS PARA PANTALLA] | [NARRACIÓN LARGA Y PROFUNDA PARA AUDIO]\n"
        "[TEXTO EN MAYÚSCULAS PARA PANTALLA] | [NARRACIÓN LARGA Y PROFUNDA PARA AUDIO]"
    )

    # --- CAMINO 1: GEMINI ---
    if gemini_api_key:
        try:
            with st.spinner("🔄 Camino 1/3: Intentando conectar con Gemini..."):
                client_gemini = genai.Client(api_key=gemini_api_key)
                response = client_gemini.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=prompt_ia
                )
                ai_lines = response.text.strip().split("\n")
                for line in ai_lines:
                    if "|" in line:
                        parts = line.split("|")
                        if len(parts) >= 2:
                            screen_texts.append(parts[0].strip().replace("[", "").replace("]", ""))
                            narration_texts.append(parts[1].strip().replace("[", "").replace("]", ""))
                if len(screen_texts) >= 6:
                    generation_method = "✨ Guion generado por Gemini"
        except Exception:
            pass # Si falla, pasa silenciosamente al Camino 2

    # --- CAMINO 2: OPENAI (Si Gemini falló o no hay clave) ---
    if len(screen_texts) < 6 and openai_api_key:
        try:
            with st.spinner("🔄 Camino 2/3: Gemini ocupado. Intentando conectar con OpenAI..."):
                client_openai = OpenAI(api_key=openai_api_key)
                response = client_openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt_ia}],
                    temperature=0.7
                )
                ai_text = response.choices[0].message.content.strip()
                ai_lines = ai_text.split("\n")
                screen_texts = []
                narration_texts = []
                for line in ai_lines:
                    if "|" in line:
                        parts = line.split("|")
                        if len(parts) >= 2:
                            screen_texts.append(parts[0].strip().replace("[", "").replace("]", ""))
                            narration_texts.append(parts[1].strip().replace("[", "").replace("]", ""))
                if len(screen_texts) >= 6:
                    generation_method = "✨ Guion generado por OpenAI"
        except Exception:
            pass # Si falla, pasa al Camino 3

    # --- CAMINO 3: RESPALDO LOCAL INTELIGENTE (Si los dos anteriores fallaron) ---
    if len(screen_texts) < 6:
        with st.spinner("🔄 Camino 3/3: Activando Respaldo Local Inteligente..."):
            generation_method = "🛡️ Guion generado por Motor Local Inteligente"
            screen_texts = [
                f"EL IMPACTO REAL DE {topic_clean.upper()}",
                "UNA REALIDAD QUE POCOS COMPRENDEN",
                "CADA DETALLE TRANSFORMA NUESTRO ENTORNO",
                "LO QUE LA CIENCIA DESCUBRIÓ RECIENTEMENTE",
                "UNA PERSPECTIVA COMPLETAMENTE NUEVA",
                "COMPÁRTELO Y COMENTA TU OPINIÓN"
            ]
            narration_texts = [
                f"Analicemos a fondo un tema fascinante y complejo: {topic_clean}.",
                "La realidad supera por completo lo que solemos imaginar en el día a día.",
                "Cada pequeño detalle que observamos transforma nuestra perspectiva y nuestra forma de ver el mundo.",
                "La investigación y el análisis detallado revelan datos verdaderamente sorprendentes sobre este fenómeno.",
                "Comprender esto nos prepara de manera directa para los cambios inevitables del futuro.",
                f"¿Qué opinas tú sobre {topic_clean}? Déjalo en los comentarios y comparte este video para llegar a más personas."
            ]

    st.info(f"Método utilizado: **{generation_method}**")

    # 2. Síntesis de la Voz Neuronal
    with st.spinner("Sintetizando la locución con voz neuronal latina..."):
        full_narration_text = ". ".join(narration_texts)
        audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        asyncio.run(generate_neural_voice(full_narration_text, selected_voice_id, audio_path))
        
        audio_clip = AudioFileClip(audio_path)
        total_duration = min(audio_clip.duration, 60.0)
        scene_duration = total_duration / len(screen_texts)

    # 3. Renderizado de video con subtítulos gigantes
    with st.spinner("Renderizando video en alta definición con subtítulos masivos..."):
        clip_list = []
        palette_map = {
            "Cinemático / Fotorrealista 8K (Estilo Película Épica)": ((10, 15, 30), (40, 20, 60)),
            "Terror Cósmico / Misterio Oscuro Hiperrealista": ((15, 5, 20), (35, 10, 25)),
            "Ciencia Ficción / Futurista Hyper-Detailed": ((5, 20, 35), (10, 50, 80)),
            "Documental Histórico / National Geographic": ((20, 15, 10), (50, 40, 20))
        }
        color_top, color_bottom = palette_map.get(video_style, ((10, 15, 30), (40, 20, 60)))

        for i, text_content in enumerate(screen_texts):
            base_img = Image.new('RGB', (1080, 1920))
            draw_bg = ImageDraw.Draw(base_img)
            
            for y_coord in range(1920):
                factor = y_coord / 1920
                modifier = int(20 * (1 - abs(y_coord - 960) / 960) * ((i % 2) + 1))
                r = min(255, int(color_top[0] * (1 - factor) + color_bottom[0] * factor) + modifier)
                g = min(255, int(color_top[1] * (1 - factor) + color_bottom[1] * factor) + modifier)
                b = min(255, int(color_top[2] * (1 - factor) + color_bottom[2] * factor) + modifier)
                draw_bg.line([(0, y_coord), (1080, y_coord)], fill=(r, g, b))

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
                
                outline_range = 14
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
        
        st.success("¡Reel generado con éxito absoluto!")
        st.video(output_path)
        
        with open(output_path, "rb") as file:
            st.download_button(
                label="📥 Descargar Reel Automático (.mp4)",
                data=file,
                file_name="reel_tres_caminos.mp4",
                mime="video/mp4"
            )
