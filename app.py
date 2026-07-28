import streamlit as st
import os
import tempfile
import asyncio
import edge_tts
from google import genai
from google.genai import types
from openai import OpenAI
from moviepy import *
from PIL import Image, ImageDraw, ImageFont
import textwrap
import base64
import requests

st.set_page_config(page_title="Reels PRO 60s", layout="centered")

st.title("🎬 Generador PRO de Reels Virales (60s)")

# --- APIs ---
gemini_api_key = os.environ.get("GEMINI_API_KEY")
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")

gemini_client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None
openrouter_client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=openrouter_api_key) if openrouter_api_key else None

# --- INPUTS ---
user_topic = st.text_input("Tema del Reel:", "3 hábitos para cambiar tu vida")
visual_style = st.selectbox("Estilo:", ["Cinematográfico", "Realista", "Religioso"])

# --- VOZ ---
async def generar_voz(texto, voz, path):
    communicate = edge_tts.Communicate(texto, voz)
    await communicate.save(path)

# --- IMAGEN ---
def generar_imagen(prompt):
    try:
        res = openrouter_client.images.generate(
            model="stabilityai/stable-diffusion-3-medium",
            prompt=prompt,
            size="1024x1024"
        )
        url = res.data[0].url
        img = requests.get(url).content
        path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
        with open(path, "wb") as f:
            f.write(img)
        return Image.open(path).resize((1080,1920))
    except Exception as e:
        st.warning(f"Error imagen: {e}")
        return Image.new("RGB",(1080,1920),(20,20,20))

# --- BOTÓN ---
if st.button("🚀 GENERAR REEL PRO"):

    with st.spinner("Generando guion viral..."):

        prompt = f"""
        Crea guion viral sobre {user_topic}

        7 escenas:
        1 hook extremo
        2 contexto
        3 valor
        4 valor
        5 valor
        6 giro
        7 CTA

        formato:
        ESCENA | texto | prompt visual
        """

        res = gemini_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )

        raw = res.text

        scenes = []
        for l in raw.split("\n"):
            if "|" in l:
                p = l.split("|")
                if len(p)>=3:
                    scenes.append({"text":p[1].strip(),"visual":p[2].strip()})

    # --- VOZ ---
    texto_total = ". ... ".join([s["text"] for s in scenes]) + "."
    audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
    asyncio.run(generar_voz(texto_total, "es-MX-DaliaNeural", audio_path))

    audio = AudioFileClip(audio_path)

    # --- FORZAR 60s ---
    TARGET = 60
    if audio.duration < TARGET:
        silence = AudioClip(lambda t: 0, duration=TARGET-audio.duration)
        audio = concatenate_audioclips([audio, silence])
    else:
        audio = audio.subclip(0, TARGET)

    scene_duration = TARGET / len(scenes)

    # --- VIDEO ---
    clips = []

    for s in scenes:
        img = generar_imagen(s["visual"])

        # TEXTO
        txt_layer = Image.new("RGBA",(1080,1920),(0,0,0,0))
        draw = ImageDraw.Draw(txt_layer)

        try:
            font = ImageFont.truetype("arial.ttf",70)
        except:
            font = ImageFont.load_default()

        texto = textwrap.fill(s["text"], width=14)

        draw.multiline_text((100,1300), texto, font=font, fill=(255,255,0))

        img = Image.alpha_composite(img.convert("RGBA"), txt_layer).convert("RGB")

        path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
        img.save(path)

        clip = (
            ImageClip(path)
            .set_duration(scene_duration)
            .resize(lambda t: 1 + 0.08*t)
            .set_position("center")
        )

        clips.append(clip)

    video = concatenate_videoclips(clips).set_audio(audio)

    out = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

    video.write_videofile(out, fps=24, codec="libx264", audio_codec="aac")

    st.success("🔥 Reel listo")
    st.video(out)
