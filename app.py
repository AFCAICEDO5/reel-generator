import time

# ... (todo tu código anterior se mantiene igual hasta el bloque del botón de generación)

if st.button("🚀 Generar Reel con Imágenes y Subtítulos Gigantes (60s)"):
    with st.spinner("Paso 1/4: Generando guion estructurado de 6 escenas con Gemini..."):
        try:
            prompt = (
                f"Actúa como un director de contenidos virales. Diseña un guion fluido de exactamente 6 escenas cortas "
                f"sobre el tema: '{user_topic}', adaptado al estilo visual: '{video_style}'. "
                "Cada texto debe estar en MAYÚSCULAS, ser corto y muy impactante. "
                "Cada descripción visual debe ser un prompt detallado para generar una imagen hiperrealista que acompañe la narración. "
                "Devuelve la respuesta estrictamente separada por líneas con este formato exacto: "
                "ESCENA 1 | [TEXTO EN MAYÚSCULAS] | [Prompt visual detallado 8K para la escena 1]\n"
                "ESCENA 2 | [TEXTO EN MAYÚSCULAS] | [Prompt visual detallado 8K para la escena 2]\n"
                "ESCENA 3 | [TEXTO EN MAYÚSCULAS] | [Prompt visual detallado 8K para la escena 3]\n"
                "ESCENA 4 | [TEXTO EN MAYÚSCULAS] | [Prompt visual detallado 8K para la escena 4]\n"
                "ESCENA 5 | [TEXTO EN MAYÚSCULAS] | [Prompt visual detallado 8K para la escena 5]\n"
                "ESCENA 6 | [TEXTO EN MAYÚSCULAS] | [Prompt visual detallado 8K para la escena 6]"
            )
            
            # --- SISTEMA DE REINTENTOS Y RESPALDO POR ALTA DEMANDA (503) ---
            response = None
            models_to_try = ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-1.5-flash"]
            
            for model_name in models_to_try:
                success = False
                for attempt in range(3): # Hasta 3 intentos por modelo
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt
                        )
                        success = True
                        break
                    except Exception as api_err:
                        if "503" in str(api_err) or "UNAVAILABLE" in str(api_err):
                            time.sleep(2 * (attempt + 1)) # Espera progresiva (2s, 4s, 6s)
                            continue
                        else:
                            raise api_err # Si es otro error distinto, lo lanza de una vez
                if success:
                    break
            
            if not response:
                raise Exception("Todos los modelos están experimentando alta demanda en este momento. Por favor, intenta de nuevo en unos minutos.")
            # -------------------------------------------------------------

            raw_output = response.text.strip()
            
            st.success("¡Guion y prompts visuales generados con éxito!")
            st.text_area("Desglose del Guion:", raw_output, height=140)

            # ... (el resto del código continúa exactamente igual a partir de aquí)
