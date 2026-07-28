import streamlit as st
import os
import tempfile
import asyncio
import edge_tts
from google import genai
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
import textwrap
import requests
import subprocess

# CONFIG
st.set_page_config(page_title="Reels PRO FFmpeg", layout="centered")
st.title("🎬 Generador PRO de Reels (SIN MoviePy)")

# --- KEYS ---
gemini_api_key = os.environ.get("GEMINI_API_KEY")
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")

gemini_client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key
) if openrouter_api_key else None

# --- INPUT ---
tema = st.text_input("Tema:", "3 hábitos que cambiarán tu vida")

# --- VOZ ---
async def generar_voz(texto, path):
    communicate = edge_tts.Communicate(texto, "es-MX-DaliaNeural")
    await communicate.save(path)

# --- IMAGEN ---
def generar_imagen(prompt, idx):
    try:
        res = openrouter_client.images.generate(
            model="stabilityai/stable-diffusion-3-medium",
            prompt=prompt,
            size="1024x1024"
        )
        url = res.data[0].url
        img_data = requests.get(url).content
    except Exception as e:
        st.warning(f"Error imagen: {e}")
        img = Image.new("RGB", (1080,1920),(20,20,20))
        path = f"img_{idx}.jpg"
        img.save(path)
        return path

    path = f"img_{idx}.jpg"
    with open(path, "wb") as f:
        f.write(img_data)

    return path

# --- BOTÓN ---
if st.button("🚀 GENERAR VIDEO"):

    # 1. GUION
    prompt = f"""
    Crea guion viral sobre {tema}

    7 escenas cortas.
    formato:
    ESCENA | texto | prompt visual
    """

    raw = None

    if gemini_client:
        try:
            res = gemini_client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )
            raw = res.text
        except:
            pass

    if not raw and openrouter_client:
        comp = openrouter_client.chat.completions.create(
            model="meta-llama/llama-3.3-70b-instruct:free",
            messages=[{"role": "user", "content": prompt}]
        )
        raw = comp.choices[0].message.content

    escenas = []
    for l in raw.split("\n"):
        if "|" in l:
            p = l.split("|")
            if len(p)>=3:
                escenas.append({"text":p[1].strip(),"visual":p[2].strip()})

    if len(escenas) < 3:
        st.error("Error generando guion")
        st.stop()

    # 2. VOZ
    texto_total = ". ... ".join([s["text"] for s in escenas]) + "."
    audio_path = "audio.mp3"
    asyncio.run(generar_voz(texto_total, audio_path))

    # 3. IMÁGENES
    image_paths = []
    for i, s in enumerate(escenas):
        path = generar_imagen(s["visual"], i)
        image_paths.append(path)

    # 4. CREAR VIDEO CON FFMPEG
    duration = 60 / len(image_paths)

    txt_file = "inputs.txt"
    with open(txt_file, "w") as f:
        for img in image_paths:
            f.write(f"file '{img}'\n")
            f.write(f"duration {duration}\n")

    video_sin_audio = "video.mp4"

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", txt_file,
        "-vsync", "vfr",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1080:1920",
        video_sin_audio
    ])

    final = "final.mp4"

    subprocess.run([
        "ffmpeg", "-y",
        "-i", video_sin_audio,
        "-i", audio_path,
        "-t", "60",
        "-c:v", "copy",
        "-c:a", "aac",
        final
    ])

    st.success("🔥 Video listo (SIN MoviePy)")
    st.video(final)
