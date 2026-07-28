import streamlit as st
import os
import tempfile
import asyncio
import edge_tts
from google import genai
from openai import OpenAI
from PIL import Image
import requests
import subprocess
import shutil
import gc


# CONFIG
st.set_page_config(
    page_title="Reels PRO IA",
    layout="centered"
)

st.title("🎬 Generador PRO de Reels IA")


# KEYS
gemini_api_key = os.environ.get("GEMINI_API_KEY")
openrouter_api_key = os.environ.get("OPENROUTER_API_KEY")


@st.cache_resource
def cargar_gemini():
    if gemini_api_key:
        return genai.Client(api_key=gemini_api_key)
    return None


@st.cache_resource
def cargar_openrouter():
    if openrouter_api_key:
        return OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key
        )
    return None


gemini_client = cargar_gemini()
openrouter_client = cargar_openrouter()



tema = st.text_input(
    "Tema del Reel:",
    "Dios tiene una palabra para ti hoy"
)



# ======================
# VOZ
# ======================

async def generar_voz(texto, salida):

    voz = edge_tts.Communicate(
        texto,
        "es-MX-DaliaNeural"
    )

    await voz.save(salida)



# ======================
# IMAGEN IA
# ======================

def generar_imagen(prompt, ruta):

    try:

        respuesta = openrouter_client.images.generate(
            model="stabilityai/stable-diffusion-3-medium",
            prompt=prompt,
            size="768x1344"
        )


        url = respuesta.data[0].url

        imagen = requests.get(
            url,
            timeout=60
        ).content


        with open(ruta,"wb") as f:
            f.write(imagen)


        return ruta


    except Exception as e:

        st.warning(
            f"No se pudo crear imagen: {e}"
        )

        img = Image.new(
            "RGB",
            (768,1344),
            (20,20,20)
        )

        img.save(ruta)

        return ruta




# ======================
# CREAR VIDEO
# ======================


if st.button("🚀 GENERAR REEL"):


    carpeta = tempfile.mkdtemp()


    try:


        # -------- GUION ---------

        prompt = f"""

        Crea un reel viral sobre:

        {tema}


        Crea 5 escenas.

        Formato:

        ESCENA | narración | descripción visual

        Cada narración debe durar
        aproximadamente 10 segundos.

        """


        raw = None


        if gemini_client:

            try:

                respuesta = gemini_client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt
                )

                raw = respuesta.text

            except Exception:
                pass



        if not raw:

            respuesta = openrouter_client.chat.completions.create(

                model="meta-llama/llama-3.3-70b-instruct:free",

                messages=[
                    {
                        "role":"user",
                        "content":prompt
                    }
                ]
            )


            raw = respuesta.choices[0].message.content



        escenas=[]


        for linea in raw.split("\n"):

            if "|" in linea:

                partes=linea.split("|")


                if len(partes)>=3:

                    escenas.append({

                        "texto":partes[1].strip(),

                        "imagen":partes[2].strip()

                    })



        if len(escenas)<3:

            st.error(
                "No se pudo crear el guion"
            )

            st.stop()



        # -------- AUDIO ---------

        texto_total=" ".join(
            x["texto"]
            for x in escenas
        )


        audio=os.path.join(
            carpeta,
            "voz.mp3"
        )


        asyncio.run(
            generar_voz(
                texto_total,
                audio
            )
        )



        # -------- IMAGENES ---------

        imagenes=[]


        for i, escena in enumerate(escenas):

            ruta=os.path.join(
                carpeta,
                f"imagen_{i}.jpg"
            )


            generar_imagen(
                escena["imagen"],
                ruta
            )


            imagenes.append(ruta)



        # -------- LISTA FFPEG ---------

        lista=os.path.join(
            carpeta,
            "lista.txt"
        )


        duracion=60/len(imagenes)



        with open(lista,"w") as archivo:


            for img in imagenes:

                archivo.write(
                    f"file '{img}'\n"
                )

                archivo.write(
                    f"duration {duracion}\n"
                )


            # repetir última imagen
            archivo.write(
                f"file '{imagenes[-1]}'\n"
            )



        video=os.path.join(
            carpeta,
            "reel.mp4"
        )



        # -------- VIDEO FINAL ---------

        comando=[

            "ffmpeg",
            "-y",

            "-f",
            "concat",

            "-safe",
            "0",

            "-i",
            lista,

            "-i",
            audio,


            "-vf",
            "scale=720:1280",


            "-t",
            "60",


            "-c:v",
            "libx264",

            "-preset",
            "veryfast",

            "-pix_fmt",
            "yuv420p",


            "-c:a",
            "aac",

            "-shortest",

            video

        ]



        resultado=subprocess.run(
            comando,
            capture_output=True
        )


        if resultado.returncode!=0:

            st.error(
                resultado.stderr.decode()
            )

            st.stop()



        st.success(
            "🔥 Reel creado correctamente"
        )


        st.video(video)



        # descarga

        with open(video,"rb") as f:

            st.download_button(

                "⬇ Descargar Reel",

                f,

                "reel.mp4",

                "video/mp4"

            )



    finally:


        gc.collect()
