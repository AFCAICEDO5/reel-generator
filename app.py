import streamlit as st
import os
import asyncio
import edge_tts
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import tempfile

# =========================
# CONFIG
# =========================

st.set_page_config(page_title="Reels IA Ligero", layout="centered")
st.title("🎬 Generador de Reels IA (LIGERO ⚡)")


# =========================
# API KEYS
# =========================

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.warning("⚠️ Falta GEMINI_API_KEY")


# =========================
# INPUT
# =========================

tema = st.text_input("Tema:", "Dios tiene una palabra para ti hoy")


# =========================
# VOZ
# =========================

async def generar_voz(texto, salida):
    voz = edge_tts.Communicate(texto, "es-MX-DaliaNeural")
    await voz.save(salida)


# =========================
# CREAR IMAGEN SIMPLE (SIN IA)
# =========================

def crear_imagen_texto(texto, ruta):

    img = Image.new("RGB", (720, 1280), (10, 10, 10))
    draw = ImageDraw.Draw(img)

    # texto dividido
    import textwrap
    lineas = textwrap.wrap(texto, width=25)

    y = 300

    for linea in lineas:
        draw.text((50, y), linea, fill=(255, 255, 255))
        y += 60

    img.save(ruta)
    return ruta


# =========================
# BOTÓN
# =========================

if st.button("🚀 GENERAR REEL LIGERO"):

    with st.spinner("Generando..."):

        # =========================
        # GUION (SOLO GEMINI)
        # =========================

        prompt = f"""
        Crea un reel viral corto sobre: {tema}

        3 escenas.

        Formato:
        ESCENA | texto corto emocional
        """

        try:
            modelo = genai.GenerativeModel("gemini-1.5-flash")
            respuesta = modelo.generate_content(prompt)
            raw = respuesta.text
        except Exception as e:
            st.error(f"Error IA: {e}")
            st.stop()


        escenas = []

        for linea in raw.split("\n"):
            if "|" in linea:
                partes = linea.split("|")
                if len(partes) >= 2:
                    escenas.append(partes[1].strip())


        if len(escenas) == 0:
            st.error("No se pudo generar contenido")
            st.stop()


        # =========================
        # AUDIO
        # =========================

        texto_total = " ".join(escenas)

        temp_dir = tempfile.mkdtemp()
        audio_path = os.path.join(temp_dir, "voz.mp3")

        asyncio.run(generar_voz(texto_total, audio_path))


        # =========================
        # IMÁGENES (SIN IA)
        # =========================

        st.subheader("🎞️ Vista previa del Reel")

        for i, texto in enumerate(escenas):

            ruta = os.path.join(temp_dir, f"img_{i}.jpg")

            crear_imagen_texto(texto, ruta)

            st.image(ruta, caption=f"Escena {i+1}")


        # =========================
        # AUDIO PLAYER
        # =========================

        st.subheader("🔊 Voz del Reel")
        st.audio(audio_path)


        # =========================
        # DESCARGA
        # =========================

        with open(audio_path, "rb") as f:
            st.download_button(
                "⬇ Descargar audio",
                f,
                "reel_audio.mp3",
                "audio/mp3"
            )


        st.success("✅ Reel ligero listo (sin bloqueos)")
