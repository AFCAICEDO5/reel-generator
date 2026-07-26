import os
import asyncio
import tempfile
import streamlit as st
from google import genai
import edge_tts
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json
import requests
from io import BytesIO

# Configuración de página de Streamlit
st.set_page_config(page_title="Generador Automático de Reels con IA", page_icon="🎬", layout="centered")

st.title("🎬 Generador Automático de Reels (60s) con IA")
st.markdown("Ingresa una idea principal y esta aplicación creará un Reel completo con guion de Gemini, voz en off natural (Edge-TTS) e imágenes fotográficas sincronizadas.")

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
            # PASO 3: Descargar Imágenes de Fondo y Procesar Subtítulos
            # ----------------------------------------------------
            status_text.text("Paso 3/4: Descargando imágenes cinematográficas y aplicando subtítulos...")
            progress_bar.progress(75)
            
            clips_video = []
            duracion_por_escena = duracion_total / len(escenas)
            
            for i, escena in enumerate(escenas):
                # Descargar una fotografía de fondo aleatoria de alta calidad adaptada a formato vertical
                img_url = f"https://picsum.photos/seed/reelscene{i+10}/1080/1920"
                try:
                    res = requests.get(img_url, timeout=10)
                    img = Image.open(BytesIO(res.content)).convert('RGB')
                except:
                    # Imagen de respaldo en caso de fallo de red
                    img = Image.new('RGB', (1080, 1920), color=(20, 20, 30))
                
                # Aplicar un ligero oscurecimiento general para que el texto resalte perfectamente
                img = img.filter(ImageFilter.SMOOTH)
                
                draw = ImageDraw.Draw(img)
                
                # Capa semitransparente oscura en la parte inferior para mejorar la lectura de los subtítulos
                overlay = Image.new('RGBA', img.size, (0, 0, 0, 0))
                draw_overlay = ImageDraw.Draw(overlay)
                draw_overlay.rectangle([50, 1150, 1030, 1850], fill=(0, 0, 0, 160)) # Rectángulo oscuro translúcido
                img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
                draw = ImageDraw.Draw(img)
                
                # Intentar cargar fuente o usar la predeterminada
                try:
                    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 52)
                except:
                    font = ImageFont.load_default()
                
                # Dividir el texto en líneas limpias
                palabras = escena["texto_voz"].split(" ")
                lineas = []
                linea_actual = ""
                for palabra in palabras:
                    test_linea = linea_actual + palabra + " "
                    if len(test_linea) > 30:
                        lineas.append(linea_actual)
                        linea_actual = palabra + " "
                    else:
                        linea_actual = test_linea
                lineas.append(linea_actual)
                
                # Dibujar texto centrado en la zona inferior
                y_text = 1250
                for linea in lineas:
                    # Sombra de alto contraste
                    draw.text((90-2, y_text-2), linea, font=font, fill="black")
                    draw.text((90+2, y_text-2), linea, font=font, fill="black")
                    draw.text((90-2, y_text+2), linea, font=font, fill="black")
                    draw.text((90+2, y_text+2), linea, font=font, fill="black")
                    # Texto principal blanco
                    draw.text((90, y_text), linea, font=font, fill="white")
                    y_text += 75
                
                # Convertir a arreglo numpy para MoviePy
                frame_np = np.array(img)
                img_clip = ImageClip(frame_np).with_duration(duracion_por_escena)
                clips_video.append(img_clip)
                
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
                preset='ultrafast',
                bitrate='3000k'
            )
            
            progress_bar.progress(100)
            status_text.text("¡Listo! Reel generado con éxito.")
            
            st.success("🎉 ¡Tu Reel de 60 segundos está listo con fotografías reales de fondo y subtítulos!")
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
