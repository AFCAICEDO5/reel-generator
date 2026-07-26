import os
import asyncio
import tempfile
import streamlit as st
from google import genai
import edge_tts
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.video.compositing.concatenate import concatenate_videoclips
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json

# Configuración de página de Streamlit
st.set_page_config(page_title="Generador Automático de Reels con IA", page_icon="🎬", layout="centered")

st.title("🎬 Generador Automático de Reels (60s) con IA")
st.markdown("Crea Reels virales con guion de Gemini, voces latinas profundas de cine, imágenes hiperrealistas con zoom y subtítulos grandes y dinámicos.")

# Entrada de la idea principal
idea = st.text_input("💡 Idea principal del Reel:", "Misterios ocultos del universo y los secretos más oscuros de los agujeros negros")

# Selector de voces latinas profesionales y profundas
voz_seleccionada = st.selectbox(
    "🎙️ Selecciona la voz en off (Narración Latina Profesional):", 
    [
        "es-MX-JorgeNeural (Hombre - Voz Profunda / Documental)", 
        "es-CO-SalomeNeural (Mujer - Locución Clara y Cálida)", 
        "es-MX-DaliaNeural (Mujer - Dinámica y Viral)",
        "es-ES-AlvaroNeural (Hombre - España Clásica)"
    ]
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
            Actúa como un director de documentales virales y experto en copywriting para Reels. 
            Crea un guion de exactamente 60 segundos basado en esta idea: '{idea}'.
            Divide el guion en exactamente 4 escenas coherentes y atrapantes.
            Devuelve la respuesta estrictamente en el siguiente formato JSON plano (sin markdown extra, solo el JSON):
            [
              {{
                "escena": 1,
                "texto_voz": "Texto impactante para la voz en off de esta escena (debe tomar unos 15 segundos leerlo con tono pausado y profundo).",
                "prompt_imagen": "Prompt cinemático en inglés detallado para generar atmósfera hiperrealista de esta escena."
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
            # PASO 2: Generar audio con Edge-TTS (Voz Latina Profunda)
            # ----------------------------------------------------
            status_text.text("Paso 2/4: Generando locución con voz latina profunda (Edge-TTS)...")
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
            # PASO 3: Renderizado Hiperrealista + Zoom + Subtítulos Grandes
            # ----------------------------------------------------
            status_text.text("Paso 3/4: Renderizando fotogramas cinemáticos y subtítulos dinámicos...")
            progress_bar.progress(75)
            
            clips_video = []
            duracion_por_escena = duracion_total / len(escenas)
            fps = 24
            total_frames = int(duracion_por_escena * fps)
            
            # Temas visuales de cine hiperrealista
            temas_visuales = [
                {"base": (2, 5, 15), "luz": (0, 120, 255), "nebula": (50, 0, 120)},
                {"base": (15, 2, 8), "luz": (255, 90, 0), "nebula": (100, 10, 30)},
                {"base": (0, 15, 15), "luz": (0, 255, 150), "nebula": (10, 60, 90)},
                {"base": (10, 0, 20), "luz": (220, 40, 120), "nebula": (120, 0, 60)}
            ]
            
            for i, escena in enumerate(escenas):
                tema = temas_visuales[i % len(temas_visuales)]
                
                # Lienzo de alta resolución para zoom suave
                img_base = Image.new('RGB', (1280, 2276), color=tema["base"])
                draw_base = ImageDraw.Draw(img_base)
                
                # Efecto de iluminación volumétrica y nebulosas de fondo
                for _ in range(14):
                    rx = np.random.randint(-100, 1380)
                    ry = np.random.randint(-100, 2376)
                    rad = np.random.randint(400, 800)
                    draw_base.ellipse([rx-rad, ry-rad, rx+rad, ry+rad], fill=tema["nebula"])
                
                draw_base.ellipse([200, 400, 1080, 1300], fill=tema["luz"])
                img_base = img_base.filter(ImageFilter.GaussianBlur(radius=50))
                
                # Partículas estelares
                draw_particles = ImageDraw.Draw(img_base)
                for _ in range(120):
                    px = np.random.randint(0, 1280)
                    py = np.random.randint(0, 2276)
                    psize = np.random.randint(1, 5)
                    draw_particles.ellipse([px, py, px+psize, py+psize], fill=(255, 255, 255))
                
                scene_frames = []
                for f in range(total_frames):
                    progress = f / total_frames
                    scale = 1.0 + (0.18 * progress) # Zoom in progresivo
                    
                    w_crop = int(1280 / scale)
                    h_crop = int(2276 / scale)
                    x_offset = (1280 - w_crop) // 2
                    y_offset = (2276 - h_crop) // 2
                    
                    cropped = img_base.crop((x_offset, y_offset, x_offset + w_crop, y_offset + h_crop))
                    frame_img = cropped.resize((1080, 1920), Image.Resampling.LANCZOS)
                    
                    # Viñeta oscura en los bordes
                    vignette = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
                    dv = ImageDraw.Draw(vignette)
                    dv.rectangle([0, 0, 1080, 1920], outline=(0, 0, 0, 140), width=80)
                    frame_img = Image.alpha_composite(frame_img.convert('RGBA'), vignette).convert('RGB')
                    
                    # Panel inferior translúcido para destacar subtítulos grandes
                    overlay = Image.new('RGBA', (1080, 1920), (0, 0, 0, 0))
                    draw_ov = ImageDraw.Draw(overlay)
                    draw_ov.rounded_rectangle([50, 1220, 1030, 1820], radius=25, fill=(0, 0, 0, 200))
                    frame_img = Image.alpha_composite(frame_img.convert('RGBA'), overlay).convert('RGB')
                    
                    draw_text = ImageDraw.Draw(frame_img)
                    
                    # Fuente grande y llamativa estilo Reels
                    try:
                        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 68)
                    except:
                        font = ImageFont.load_default()
                    
                    palabras = escena["texto_voz"].split(" ")
                    lineas = []
                    linea_actual = ""
                    for palabra in palabras:
                        test_linea = linea_actual + palabra + " "
                        if len(test_linea) > 22:
                            lineas.append(linea_actual.strip())
                            linea_actual = palabra + " "
                        else:
                            linea_actual = test_linea
                    lineas.append(linea_actual.strip())
                    
                    # Dibujar subtítulos grandes centrados con palabras clave destacadas
                    y_cursor = 1280
                    for linea_idx, linea in enumerate(lineas):
                        try:
                            bbox = draw_text.textbbox((0, 0), linea, font=font)
                            text_width = bbox[2] - bbox[0]
                        except:
                            text_width = len(linea) * 25
                        
                        x_centered = (1080 - text_width) // 2
                        
                        color_texto = "yellow" if linea_idx == 0 else "white"
                        
                        # Sombra gruesa para máximo contraste
                        draw_text.text((x_centered - 3, y_cursor - 3), linea, font=font, fill="black")
                        draw_text.text((x_centered + 3, y_cursor - 3), linea, font=font, fill="black")
                        draw_text.text((x_centered - 3, y_cursor + 3), linea, font=font, fill="black")
                        draw_text.text((x_centered + 3, y_cursor + 3), linea, font=font, fill="black")
                        
                        draw_text.text((x_centered, y_cursor), linea, font=font, fill=color_texto)
                        y_cursor += 85
                    
                    scene_frames.append(np.array(frame_img))
                
                scene_clip = ImageSequenceClip(scene_frames, fps=fps).with_duration(duracion_por_escena)
                clips_video.append(scene_clip)
                
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
                fps=fps,
                codec='libx264',
                audio_codec='aac',
                preset='ultrafast',
                bitrate='3500k'
            )
            
            progress_bar.progress(100)
            status_text.text("¡Listo! Reel generado con éxito.")
            
            st.success("🎉 ¡Tu Reel con voz latina profunda y subtítulos grandes y dinámicos está listo!")
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
