import streamlit as st
import os
import tempfile
import asyncio
import edge_tts
from google import genai
from openai import OpenAI
from moviepy.editor import *
from PIL import Image, ImageDraw, ImageFont
import textwrap
import requests

# CONFIG
st.set_page_config(page_title="Reels PRO 60s", layout="centered")
st.title("🎬 Generador PRO de Reels Virales (60s)")

# --- API KEYS ---
gemini_api_key = os.environ.get("GEMINI_API_KEY")
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")

gemini_client = genai.Client(api_key=gemini_api_key) if gemini_api_key else None
openrouter_client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_api_key
) if openrouter_api_key else None

# --- INPUT ---
user_topic = st.text_input("Tema:", "3 hábitos que cambiarán tu vida")
visual_style = st.selectbox("Estilo:", ["Cinematográfico", "Realista", "Religioso"])

# --- VOZ ---
async def generar_voz(texto, voz, path):
    communicate = edge_tts.Communicate(texto, voz)
    await communicate.save(path)

# --- IMÁGENES ---
def generar_imagen(prompt):
    try:
        res = openrouter_client.images.generate(
            model="stabilityai/stable-diffusion-3-medium",
            prompt=prompt,
            size="1024x1024"
        )
        url = res.data[0].url
        img_data = requests.get(url).content
        path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name

        with open(path, "wb") as f:
            f.write(img_data)

        return Image.open(path).resize((1080, 1920))

    except Exception as e:
        st.warning(f"⚠️ Error generando imagen: {e}")
        return Image.new("RGB", (1080, 1920), (20, 20, 20))

# --- BOTÓN ---
if st.button("🚀 GENERAR REEL PRO"):

    # =========================
    # 1. GENERAR GUION (ROBUSTO)
    # =========================
    with st.spinner("Generando guion viral..."):

        prompt = f"""
        Crea un guion viral para TikTok sobre: {user_topic}

        7 escenas:
        1 Hook extremo
        2 Contexto
        3 Valor
        4 Valor
        5 Valor
        6 Giro
        7 CTA emocional

        Reglas:
        - Frases cortas
        - Lenguaje emocional
        - NO mayúsculas completas
        - Máximo 20 palabras

        Formato:
        ESCENA | texto | prompt visual en inglés
        """

        raw = None

        # 🔹 Intento 1: Gemini
        if gemini_client:
            try:
                res = gemini_client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt
                )
                raw = res.text
            except Exception as e:
                st.warning(f"⚠️ Gemini falló: {e}")

        # 🔹 Intento 2: OpenRouter
        if not raw and openrouter_client:
            try:
                comp = openrouter_client.chat.completions.create(
                    model="meta-llama/llama-3.3-70b-instruct:free",
                    messages=[{"role": "user", "content": prompt}]
                )
                raw = comp.choices[0].message.content
            except Exception as e:
                st.error(f"❌ OpenRouter falló: {e}")
                st.stop()

        if not raw:
            st.error("❌ No se pudo generar el guion")
            st.stop()

        # PARSEAR ESCENAS
        scenes = []
        for line in raw.split("\n"):
            if "|" in line:
                parts = line.split("|")
                if len(parts) >= 3:
                    scenes.append({
                        "text": parts[1].strip(),
                        "visual": parts[2].strip()
                    })

        if len(scenes) < 5:
            st.error("❌ Guion inválido")
            st.stop()

    # =========================
    # 2. VOZ NATURAL
    # =========================
    texto_total = ". ... ".join([s["text"] for s in scenes]) + "."
    audio_path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name

    asyncio.run(generar_voz(texto_total, "es-MX-DaliaNeural", audio_path))

    audio = AudioFileClip(audio_path)

    # =========================
    # 3. FORZAR 60s
    # =========================
    TARGET = 60

    if audio.duration < TARGET:
        silence = AudioClip(lambda t: 0, duration=TARGET - audio.duration)
        audio = concatenate_audioclips([audio, silence])
    else:
        audio = audio.subclip(0, TARGET)

    scene_duration = TARGET / len(scenes)

    # =========================
    # 4. CREAR VIDEO
    # =========================
    clips = []

    for s in scenes:
        img = generar_imagen(s["visual"])

        # TEXTO
        txt_layer = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        draw = ImageDraw.Draw(txt_layer)

        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 70)
        except:
            font = ImageFont.load_default()

        texto = textwrap.fill(s["text"], width=14)

        draw.multiline_text(
            (100, 1300),
            texto,
            font=font,
            fill=(255, 230, 0)
        )

        img = Image.alpha_composite(img.convert("RGBA"), txt_layer).convert("RGB")

        path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
        img.save(path)

        clip = (
            ImageClip(path)
            .set_duration(scene_duration)
            .resize(lambda t: 1 + 0.08 * t)
            .set_position("center")
        )

        clips.append(clip)

    video = concatenate_videoclips(clips).set_audio(audio)

    output = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4").name

    video.write_videofile(
        output,
        fps=24,
        codec="libx264",
        audio_codec="aac"
    )

    st.success("🔥 Reel generado correctamente")
    st.video(output)
