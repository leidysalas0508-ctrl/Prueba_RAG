
import requests
import streamlit as st
from io import BytesIO
import os


# Dirección del backend
DIRECCION_API = os.getenv(
    "DIRECCION_API",
    "http://127.0.0.1:8000"
)

# Configurar la página
st.set_page_config(
    page_title="Asistente RAG",
    page_icon="📚"
)

st.title("📚 Asistente de documentos")
st.write(
    "Consulta información de tus documentos PDF "
    "utilizando inteligencia artificial."
)


# Crear las variables de sesión
if "documento_id" not in st.session_state:
    st.session_state.documento_id = ""

if "mensajes" not in st.session_state:
    st.session_state.mensajes = []


# Recuperar un documento existente
identificador_guardado = st.text_input(
    "Identificador de un documento existente",
    value=st.session_state.documento_id
)

if identificador_guardado != st.session_state.documento_id:
    st.session_state.documento_id = identificador_guardado.strip()
    st.session_state.mensajes = []


# Subir un documento PDF
archivo_pdf = st.file_uploader(
    "Selecciona un documento PDF",
    type=["pdf"]
)

if archivo_pdf is not None:
    if st.button("Procesar documento"):
        try:
            with st.spinner("Enviando documento..."):
                respuesta_api = requests.post(
                    f"{DIRECCION_API}/documentos",
                    files={
                        "archivo": (
                            archivo_pdf.name,
                            archivo_pdf.getvalue(),
                            "application/pdf"
                        )
                    },
                    timeout=60
                )

                respuesta_api.raise_for_status()
                datos = respuesta_api.json()

                st.session_state.documento_id = datos["job_id"]
                st.session_state.mensajes = []

                st.success("Documento recibido correctamente.")

        except requests.exceptions.RequestException:
            st.error("No fue posible subir el documento.")


# Consultar el estado del documento
documento_id = st.session_state.documento_id
documento_listo = False

if documento_id:
    st.write("**Estado del documento:**")

    if st.button("Actualizar estado"):
        st.rerun()

    try:
        respuesta_estado = requests.get(
            f"{DIRECCION_API}/trabajos/{documento_id}",
            timeout=10
        )

        respuesta_estado.raise_for_status()
        trabajo = respuesta_estado.json()

        st.info(
            f"{trabajo['estado']}: {trabajo['mensaje']}"
        )

        if trabajo["estado"] == "Completed":
            documento_listo = True
            st.success("Ya puedes hacer preguntas sobre el PDF.")

        elif trabajo["estado"] == "Failed":
            st.error("No se pudo procesar el documento.")

    except requests.exceptions.RequestException:
        st.error("No fue posible consultar el estado del documento.")


# Mostrar las imágenes extraídas del documento
if documento_id and documento_listo:

    with st.expander("🖼️ Ver imágenes del documento"):

        try:
            # Consultar las imágenes disponibles
            respuesta_imagenes = requests.get(
                f"{DIRECCION_API}/documentos/{documento_id}/imagenes",
                timeout=15
            )

            respuesta_imagenes.raise_for_status()

            imagenes = respuesta_imagenes.json().get(
                "imagenes", []
            )

            if not imagenes:
                st.info("Este documento no contiene imágenes extraídas.")

            else:
                st.write(
                    f"Se encontraron {len(imagenes)} imágenes."
                )

                # Seleccionar la página que queremos consultar
                paginas = sorted({
                    imagen["pagina"]
                    for imagen in imagenes
                })

                pagina_seleccionada = st.selectbox(
                    "Selecciona una página",
                    options=paginas
                )

                # Mostrar las imágenes de la página elegida
                for imagen in imagenes:
                    if imagen["pagina"] == pagina_seleccionada:

                        direccion_imagen = (
                            f"{DIRECCION_API}/documentos/"
                            f"{documento_id}/imagenes/"
                            f"{imagen['nombre_archivo']}"
                        )

                        # Descargar la imagen desde FastAPI
                        respuesta_archivo = requests.get(
                            direccion_imagen,
                            timeout=15
                        )

                        respuesta_archivo.raise_for_status()

                        st.image(
                            BytesIO(respuesta_archivo.content),
                            caption=(
                                f"{imagen['documento']} - "
                                f"Página {imagen['pagina']}"
                            ),
                            use_container_width=True
                        )

        except requests.exceptions.RequestException:
            st.error("No fue posible consultar las imágenes.")


# Mostrar el historial de mensajes
for mensaje in st.session_state.mensajes:
    with st.chat_message(mensaje["rol"]):
        st.markdown(mensaje["contenido"])

        # Recuperar imágenes de respuestas anteriores
        for imagen in mensaje.get("imagenes", []):
            try:
                respuesta_imagen = requests.get(
                    imagen["url"],
                    timeout=15
                )
                respuesta_imagen.raise_for_status()

                st.image(
                    BytesIO(respuesta_imagen.content),
                    caption=imagen["descripcion"],
                    use_container_width=True
                )

            except requests.exceptions.RequestException:
                st.warning("No fue posible mostrar una imagen.")


# Escribir preguntas
pregunta = st.chat_input(
    "Escribe tu pregunta sobre el documento...",
    disabled=not documento_listo
)

if pregunta:
    st.session_state.mensajes.append({
        "rol": "user",
        "contenido": pregunta
    })

    with st.chat_message("user"):
        st.markdown(pregunta)

    with st.spinner("Buscando información en el documento..."):
        try:
            # Consultar el sistema RAG
            respuesta_api = requests.post(
                f"{DIRECCION_API}/preguntar",
                json={
                    "pregunta": pregunta,
                    "documento_id": documento_id
                },
                timeout=120
            )

            respuesta_api.raise_for_status()
            datos = respuesta_api.json()

            respuesta = datos["respuesta"]
            fuentes = datos.get("fuentes", [])

            # Mostrar referencias sin duplicarlas
            if fuentes:
                referencias = {
                    (fuente["documento"], fuente["pagina"])
                    for fuente in fuentes
                }

                respuesta += "\n\n**Fuentes consultadas:**\n"

                for documento, pagina in sorted(referencias):
                    respuesta += f"\n- {documento}, página {pagina}"

            # Consultar imágenes de las páginas recuperadas
            imagenes_relacionadas = []

            try:
                respuesta_imagenes = requests.get(
                    f"{DIRECCION_API}/documentos/{documento_id}/imagenes",
                    timeout=15
                )

                respuesta_imagenes.raise_for_status()
                todas_imagenes = respuesta_imagenes.json().get(
                    "imagenes", []
                )

                paginas_consultadas = {
                    fuente["pagina"]
                    for fuente in fuentes
                }

                for imagen in todas_imagenes:
                    if imagen["pagina"] in paginas_consultadas:
                        nombre_imagen = imagen["nombre_archivo"]

                        direccion_imagen = (
                            f"{DIRECCION_API}/documentos/"
                            f"{documento_id}/imagenes/{nombre_imagen}"
                        )

                        imagenes_relacionadas.append({
                            "url": direccion_imagen,
                            "descripcion": (
                                f"{imagen['documento']} - "
                                f"Página {imagen['pagina']}"
                            )
                        })

            except requests.exceptions.RequestException:
                st.warning(
                    "No fue posible consultar las imágenes del documento."
                )

            # Mostrar un máximo de tres imágenes por respuesta
            imagenes_relacionadas = imagenes_relacionadas[:3]

            # Guardar la respuesta y sus imágenes
            st.session_state.mensajes.append({
                "rol": "assistant",
                "contenido": respuesta,
                "imagenes": imagenes_relacionadas
            })

            with st.chat_message("assistant"):
                st.markdown(respuesta)

                for imagen in imagenes_relacionadas:
                    try:
                        respuesta_imagen = requests.get(
                            imagen["url"],
                            timeout=15
                        )

                        respuesta_imagen.raise_for_status()

                        st.image(
                            BytesIO(respuesta_imagen.content),
                            caption=imagen["descripcion"],
                            use_container_width=True
                        )

                    except requests.exceptions.RequestException:
                        st.warning(
                            "No fue posible mostrar una imagen."
                        )

        except requests.exceptions.HTTPError as error:
            st.error(
                f"La API devolvió un error HTTP: "
                f"{error.response.status_code}"
            )

       
        except requests.exceptions.Timeout:
            st.error(
                "La consulta tardó demasiado tiempo. "
                "FastAPI no respondió dentro del tiempo establecido."
            )

        except requests.exceptions.ConnectionError:
            st.error(
                "No se pudo establecer conexión con FastAPI."
            )

        except requests.exceptions.RequestException as error:
            st.error(
                f"Ocurrió un error al consultar FastAPI: {type(error).__name__}"
            )

