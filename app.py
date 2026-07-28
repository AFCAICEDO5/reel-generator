import streamlit as st
import os
import asyncio
import edge_tts
from PIL import Image, ImageDraw
import tempfile

st.set_page_config(page_title="Reels IA Ultra Ligero")
st.title("⚡ Generador de Reels (SIN BLOQUEOS)")


tema = st.text_input("Tema:", "Dios tiene una palabra para ti hoy")


async def generar_voz(texto, salida):
    voz = edge_tts.Communicate(texto, "es-MX-DaliaNeural")
    await voz.save(salida)


def crear_imagen_texto(texto, ruta):

    img = Image.new("RGB", (720, 1280), (15, 15, 15))
    draw = ImageDraw.Draw(img)

    import textwrap
    lineas = textwrap.wrap(texto, width=25)

    y = 400

    for linea in lineas:
        draw.text((60, y), linea, fill=(255, 255, 255))
        y += 60

    img.save(ruta)
    return ruta


if st.button("🚀 GENERAR"):

    # 👇 SIN IA (para evitar errores y throttling)
    escenas = [
        "Dios tiene algo grande para ti",
        "Confía, aunque no entiendas todo"
    ]

    texto_total = " ".join(escenas)

    temp_dir = tempfile.mkdtemp()
    audio_path = os.path.join(temp_dir, "voz.mp3")

    asyncio.run(generar_voz(texto_total, audio_path))

    st.subheader("🎞️ Vista")

    for i, texto in enumerate(escenas):
        ruta = os.path.join(temp_dir, f"img_{i}.jpg")
        crear_imagen_texto(texto, ruta)
        st.image(ruta)

    st.subheader("🔊 Audio")
    st.audio(audio_path)

    with open(audio_path, "rb") as f:
        st.download_button("⬇ Descargar", f, "reel.mp3")

    st.success("✅ Funciona sin errores ni bloqueos")
