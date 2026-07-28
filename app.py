import streamlit as st
import os
import tempfile
import asyncio
import edge_tts
import google.generativeai as genai
from openai import OpenAI
from PIL import Image
import requests
import subprocess
import gc


# =========================
# CONFIG
# =========================

st.set_page_config(page_title="Reels PRO IA", layout="centered")
st.title("🎬 Generador PRO de Reels IA")


# =========================
# KEYS
# =========================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")


# =========================
# CLIENTES
# =========================

@st.cache_resource
def cargar_gemini():
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        return genai
    return None


@st.cache_resource
def cargar_openrouter():
    if OPENROUTER_API_KEY:
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY
        )
    return None


gemini = cargar_gemini()
openrouter = cargar_openrouter()


# =========================
# INPUT
# =========================

tema = st.text_input(
    "Tema del Reel:",
    "Dios tiene una palabra para ti hoy"
)


# =========================
# VOZ
# =========================

async def generar_voz(texto, salida):
    voz = edge_tts.Communicate(texto, "es-MX-DaliaNeural")
    await voz.save(salida)


# =========================
# GENERAR GUION (ROBUSTO)
# =========================

def generar_guion_openrouter(prompt):

    modelos = [
        "mistralai/mistral-7b-instruct",
        "openchat/openchat-3.5",
        "nousresearch/nous-hermes-2-mixtral"
    ]

    for modelo in modelos:
        try:
            respuesta = openrouter.chat.completions.create(
                model=modelo,
                messages=[{"role": "user", "content": prompt}]
            )
            return respuesta.choices[0].message.content
        except Exception:
            continue

    return None


# =========================
# IMAGEN IA
# =========================

def generar_imagen(prompt, ruta):

    try:
        respuesta = openrouter.images.generate(
            model="stabilityai/stable-diffusion-3-medium",
            prompt=prompt,
            size="768x1344"
        )

        url = respuesta.data[0].url
        img = requests.get(url, timeout=60).content

        with open(ruta, "wb") as f:
            f.write(img)

        return ruta

    except Exception as e:
        st.warning(f"Error imagen IA: {e}")

        img = Image.new("RGB", (768, 1344), (30, 30, 30))
        img.save(ruta)

        return ruta


# =========================
# BOTÓN
# =========================

if st.button("🚀 GENERAR REEL"):

    carpeta = tempfile.mkdtemp()

    try:

        # =========================
        # GUION
        # =========================

        prompt = f"""
        Crea un reel viral sobre: {tema}

        5 escenas.

        Formato:
        ESCENA | narración | descripción visual
        """

        raw = None

        # GEMINI
        if gemini:
            try:
                modelo = genai.GenerativeModel("gemini-1.5-flash")
                response = modelo.generate_content(prompt)
                raw = response.text
            except Exception:
                pass

        # OPENROUTER fallback
        if not raw and openrouter:
            raw = generar_guion_openrouter(prompt)

        if not raw:
            st.error("No se pudo generar el guion")
            st.stop()


        escenas = []

        for linea in raw.split("\n"):
            if "|" in linea:
                partes = linea.split("|")
                if len(partes) >= 3:
                    escenas.append({
                        "texto": partes[1].strip(),
                        "imagen": partes[2].strip()
                    })

        if len(escenas) < 3:
            st.error("Error procesando el guion")
            st.stop()


        # =========================
        # AUDIO
        # =========================

        texto_total = " ".join(x["texto"] for x in escenas)

        audio_path = os.path.join(carpeta, "voz.mp3")
        asyncio.run(generar_voz(texto_total, audio_path))


        # =========================
        # IMÁGENES
        # =========================

        imagenes = []

        for i, escena in enumerate(escenas):
            ruta = os.path.join(carpeta, f"img_{i}.jpg")
            generar_imagen(escena["imagen"], ruta)
            imagenes.append(ruta)


        # =========================
        # LISTA FFMPEG
        # =========================

        lista = os.path.join(carpeta, "lista.txt")
        duracion = 60 / len(imagenes)

        with open(lista, "w") as f:
            for img in imagenes:
                f.write(f"file '{img}'\n")
                f.write(f"duration {duracion}\n")

            f.write(f"file '{imagenes[-1]}'\n")


        # =========================
        # VIDEO FINAL
        # =========================

        video_final = os.path.join(carpeta, "reel.mp4")

        comando = [
            "ffmpeg",
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", lista,
            "-i", audio_path,
            "-vf", "scale=720:1280",
            "-t", "60",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-shortest",
            video_final
        ]

        proceso = subprocess.run(comando, capture_output=True)

        if proceso.returncode != 0:
            st.error(proceso.stderr.decode())
            st.stop()


        st.success("🔥 Reel creado correctamente")
        st.video(video_final)

        with open(video_final, "rb") as f:
            st.download_button(
                "⬇ Descargar Reel",
                f,
                "reel.mp4",
                "video/mp4"
            )

    finally:
        gc.collect()
