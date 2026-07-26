import os
import asyncio
import tempfile
import streamlit as st
from google import genai
import edge_tts
from moviepy.editor import ImageClip, AudioFileClip, TextClip, CompositeVideoClip, concatenate_videoclips
import numpy as np
from PIL import Image
# Configuración de página de Streamlit
st.set_page_config(page_title="Generador Automático de Reels con IA", page_icon="🎬", layout="centered")

st.title("🎬 Generador Automático de Reels (60s) con IA")
st.markdown("Ingresa una idea principal y esta aplicación creará un Reel completo con guion de Gemini, voz en off natural (Edge-TTS), imágenes ilustrativas y subtítulos sincronizados.")

# Entrada de la idea principal
idea = st.text_input("💡 Idea principal del Reel:", "Curiosidades impactantes sobre el espacio y los agujeros negros que te dejarán sin aliento")
voz_seleccionada = st.selectbox(
    "🎙️ Selecciona la voz en off (Español):", 
    ["es-ES-AlvaroNeural (Hombre - España)", "es-ES-ElviraNeural (Mujer - España)", "es-MX-DaliaNeural (Mujer - México)", "es-MX-JorgeNeural (Hombre - México)"]
)

# Clave de API de Gemini
gemini_key = st.text_input("🔑 Ingresa tu Google Gemini API Key:", type="password")

if st.button("🚀 Generar Reel de 60s"):
    if not gemini_key:
        st.error("Por favor ingresa tu Gemini API Key para continuar.")
    elif not idea:
        st.error("Por favor ingresa una idea principal.")
    else:
        voice_code = voz_seleccionada.split(" ")[0]
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # ----------------------------------------------------
            # PASO 1: Generar Guion estructurado con Gemini
            # ----------------------------------------------------
            status_text.text("Paso 1/4: Generando guion optimizado de 60s con Gemini...")
            progress_bar.progress(25)
            
            client = genai.Client(api_key=gemini_key)
            prompt = f"""
            Actúa como un guionista experto en Reels virales. Crea un guion de exactamente 60 segundos basado en esta idea: '{idea}'.
            Divide el guion en exactamente 4 escenas coherentes.
            Devuelve la respuesta estrictamente en el siguiente formato JSON plano (sin markdown extra, solo el JSON):
            [
              {{
                "escena": 1,
                "texto_voz": "Texto exacto que dirá la voz en off para esta escena (debe tomar unos 15 segundos leerlo con buen ritmo).",
                "prompt_imagen": "Un prompt en inglés altamente detallado, fotorrealista y cinematográfico en formato vertical 9:16 para generar la imagen de fondo de esta escena."
              }},
              {{
                "escena": 2,
                "texto_voz": "...",
                "prompt_imagen": "..."
              }},
              {{
                "escena": 3,
                "texto_voz": "...",
                "prompt_imagen": "..."
              }},
              {{
                "escena": 4,
                "texto_voz": "...",
                "prompt_imagen": "..."
              }}
            ]
            """
            
            response = client.models.generate_content(
                model='gemini-flash-latest',
                contents=prompt,
            )
            
            import json
            clean_text = response.text.strip()
            if clean_text.startswith("```json"):
                clean_text = clean_text[7:]
            if clean_text.endswith("```"):
                clean_text = clean_text[:-3]
            
            escenas = json.loads(clean_text.strip())
            
            # ----------------------------------------------------
            # PASO 2: Generar audio con Edge-TTS
            # ----------------------------------------------------
            status_text.text("Paso 2/4: Generando locución con voz natural (Edge-TTS)...")
            progress_bar.progress(50)
            
            texto_completo = " ".join([e["texto_voz"] for e in escenas])
            
            async def generar_audio(texto, voz, output_path):
                communicate = edge_tts.Communicate(texto, voz)
                await communicate.save(output_path)
                
            temp_dir = tempfile.mkdtemp()
            audio_path = os.path.join(temp_dir, "voiceover.mp3")
            
            asyncio.run(generar_audio(texto_completo, voice_code, audio_path))
            
            audio_clip = AudioFileClip(audio_path)
            duracion_total = audio_clip.duration
            
            # ----------------------------------------------------
            # PASO 3: Preparar Imágenes de Fondo y Subtítulos
            # ----------------------------------------------------
            status_text.text("Paso 3/4: Preparando imágenes verticales (1080x1920)...")
            progress_bar.progress(75)
            
            clips_video = []
            duracion_por_escena = duracion_total / len(escenas)
            
            for i, escena in enumerate(escenas):
                img = Image.new('RGB', (1080, 1920), color=(15 + i*15, 10, 30 + i*20))
                img_path = os.path.join(temp_dir, f"scene_{i}.png")
                img.save(img_path)
                
                img_clip = ImageClip(img_path).with_duration(duracion_por_escena)
                
                txt_clip = TextClip(
                    text=escena["texto_voz"], 
                    font_size=45, 
                    color='white', 
                    stroke_color='black', 
                    stroke_width=2,
                    size=(900, None),
                    method='caption'
                ).set_duration(duracion_por_escena).set_position(('center', 1300))
                
                video_escena = CompositeVideoClip([img_clip, txt_clip])
                clips_video.append(video_escena)
                
            video_final = concatenate_videoclips(clips_video, method="compose")
            video_final = video_final.with_audio(audio_clip)
            
            # ----------------------------------------------------
            # PASO 4: Renderizar MP4 final (1080x1920)
            # ----------------------------------------------------
            status_text.text("Paso 4/4: Renderizando video final en MP4 (1080x1920)...")
            progress_bar.progress(90)
            
            output_mp4 = os.path.join(temp_dir, "reel_final.mp4")
            video_final.write_videofile(
                output_mp4,
                fps=24,
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                bitrate='4000k'
            )
            
            progress_bar.progress(100)
            status_text.text("¡Listo! Reel generado con éxito.")
            
            st.success("🎉 ¡Tu Reel de 60 segundos está listo para descargar y publicar!")
            st.video(output_mp4)
            
            with open(output_mp4, "rb") as file:
                st.download_button(
                    label="⬇️ Descargar Reel en MP4 (1080p)",
                    data=file,
                    file_name="reel_viral_ia.mp4",
                    mime="video/mp4"
                )
                
        except Exception as e:
                st.error(f"Ocurrió un error durante el proceso: {str(e)}")
