import streamlit as st
import os
from google import genai

st.set_page_config(
    page_title="Generador de Reels con IA",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Generador Automático de Reels")
st.markdown("Crea contenido optimizado para redes sociales utilizando Inteligencia Artificial.")

# Obtener la clave de API desde los secrets de Streamlit o variables de entorno
api_key = st.secrets.get("GEMINI_API_KEY") if "GEMINI_API_KEY" in st.secrets else os.environ.get("GEMINI_API_KEY")

if not api_key:
    st.error("⚠️ No se encontró la `GEMINI_API_KEY` en los Secrets de Streamlit. Por favor, configúrala en el panel de administración.")
    st.stop()

# Inicializar el cliente moderno de GenAI
client = genai.Client(api_key=api_key)

st.sidebar.header("Configuración del Reel")
topic = st.sidebar.text_input("Tema o Idea Principal", "Consejos de productividad")
tone = st.sidebar.selectbox("Tono del guion", ["Divertido", "Inspirador", "Educativo", "Polémico"])

if st.button("Generar Guion con IA"):
    with st.spinner("Generando contenido con Gemini..."):
        try:
            prompt = f"Escribe un guion corto y dinámico para un Reel de Instagram sobre: {topic}. El tono debe ser {tone}."
            response = client.models.generate_content(
    model="gemini-3.5-flash",
    contents=prompt
)
            st.session_state["script"] = response.text
            st.success("¡Guion generado con éxito!")
        except Exception as e:
            st.error(f"Error al conectar con la API de Gemini: {e}")

if "script" in st.session_state:
    st.subheader("📝 Guion Generado")
    script_text = st.text_area("Puedes editar el guion antes de procesar:", st.session_state["script"], height=200)
