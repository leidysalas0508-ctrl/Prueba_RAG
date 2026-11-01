
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from backend.app.services.fragmentador import crear_fragmentos
from backend.app.services.buscador_hibrido import BuscadorHibrido
from backend.app.services.servicio_gemini import generar_respuesta

from pathlib import Path
from fastapi import UploadFile, File, BackgroundTasks
from backend.app.services.gestor_trabajos import gestor_trabajos

from backend.app.services.procesador_documentos import procesar_documento_completo
import json
from fastapi.responses import FileResponse


# Crear la aplicación
aplicacion = FastAPI(
    title="Sistema RAG Multimodal",
    description="API para consultar documentos PDF utilizando IA",
    version="1.0.0"
)


# Definir el formato de las preguntas
class SolicitudPregunta(BaseModel):
    pregunta: str


# Preparar el buscador cuando inicia la aplicación
fragmentos = crear_fragmentos(
    "data/procesados/resultado_documento.json"
)

buscador = BuscadorHibrido(fragmentos)


@aplicacion.get("/")
def verificar_servidor():
    return {
        "mensaje": "El sistema RAG está funcionando"
    }


class SolicitudPregunta(BaseModel):
    pregunta: str
    documento_id: str
    
@aplicacion.post("/preguntar")
def responder_pregunta(solicitud: SolicitudPregunta):

    # Comprobar que el documento esté procesado
    trabajo = gestor_trabajos.consultar_trabajo(
        solicitud.documento_id
    )

    if not trabajo:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el documento solicitado."
        )

    if trabajo["estado"] != "Completed":
        raise HTTPException(
            status_code=409,
            detail="El documento todavía no está listo para consultar."
        )

    # Buscar los fragmentos procesados de ese documento
    ruta_json = Path(
        f"data/procesados/{solicitud.documento_id}.json"
    )

    if not ruta_json.exists():
        raise HTTPException(
            status_code=404,
            detail="No se encontraron los datos del documento."
        )

    try:
        fragmentos = crear_fragmentos(str(ruta_json))

        # Usar identificadores únicos por documento
        for fragmento in fragmentos:
            fragmento["id"] = (
                f"{solicitud.documento_id}_{fragmento['id']}"
            )

        # Crear el buscador para el documento seleccionado
        buscador = BuscadorHibrido(fragmentos)

        resultados = buscador.buscar(
            solicitud.pregunta,
            cantidad=5
        )

        # Filtrar resultados del documento solicitado
        resultados = [
            resultado
            for resultado in resultados
            if resultado["id"].startswith(
                f"{solicitud.documento_id}_"
            )
        ]

        if not resultados:
            return {
                "respuesta": "No encontré información relevante en el documento.",
                "fuentes": []
            }

        # Preparar el contexto con las páginas encontradas
        contexto = "\n\n".join(
            f"Página {resultado['pagina']}:\n"
            f"{resultado['texto']}"
            for resultado in resultados
        )

        instrucciones = f"""
        Eres un asistente que responde preguntas sobre documentos PDF.

        Utiliza únicamente el contexto proporcionado.

        Si no existe información suficiente para responder,
        indica que no encontraste la respuesta en el documento.

        No inventes información ni fuentes.

        CONTEXTO:
        {contexto}

        PREGUNTA:
        {solicitud.pregunta}
        """

        respuesta = generar_respuesta(instrucciones)

        return {
            "documento_id": solicitud.documento_id,
            "respuesta": respuesta,
            "fuentes": [
                {
                    "documento": trabajo["archivo"],
                    "pagina": resultado["pagina"],
                    "fragmento": resultado["texto"][:250]
                }
                for resultado in resultados
            ]
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="No fue posible completar la consulta."
        )

def procesar_documento(identificador, ruta_archivo):
    try:
        gestor_trabajos.actualizar_trabajo(
            identificador,
            "Processing",
            "Procesando documento PDF"
        )

        # Aquí conectaremos la extracción e indexación reales
        if not ruta_archivo.exists():
            raise FileNotFoundError("No se encontró el archivo PDF")

        gestor_trabajos.actualizar_trabajo(
            identificador,
            "Completed",
            "Archivo recibido y verificado correctamente"
        )

    except Exception:
        gestor_trabajos.actualizar_trabajo(
            identificador,
            "Failed",
            "No se pudo procesar el documento"
        )


@aplicacion.post("/documentos")
async def subir_documento(
    tareas: BackgroundTasks,
    archivo: UploadFile = File(...)
):
    # Validar que el archivo sea PDF
    if not archivo.filename or not archivo.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Solo se permiten archivos PDF"
        )

    carpeta = Path("data/uploads")
    carpeta.mkdir(parents=True, exist_ok=True)

    # Crear el trabajo y un nombre único para el archivo
    trabajo = gestor_trabajos.crear_trabajo(archivo.filename)

    ruta_archivo = carpeta / f"{trabajo['job_id']}.pdf"

    # Guardar el archivo por bloques
    with ruta_archivo.open("wb") as destino:
        while contenido := await archivo.read(1024 * 1024):
            destino.write(contenido)

    # Ejecutar el trabajo después de devolver la respuesta
    tareas.add_task(
    procesar_documento_completo,
    trabajo["job_id"],
    ruta_archivo
)

    return trabajo


@aplicacion.get("/trabajos/{identificador}")
def consultar_estado(identificador: str):
    trabajo = gestor_trabajos.consultar_trabajo(identificador)

    if not trabajo:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el trabajo"
        )

    return trabajo


@aplicacion.get("/documentos/{identificador}/imagenes")
def consultar_imagenes(identificador: str):
    # Comprobar que el documento existe
    trabajo = gestor_trabajos.consultar_trabajo(identificador)

    if not trabajo:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el documento."
        )

    if trabajo["estado"] != "Completed":
        raise HTTPException(
            status_code=409,
            detail="El documento todavía no está listo."
        )

    # Abrir el resultado del procesamiento
    ruta_json = Path("data/procesados") / f"{identificador}.json"

    if not ruta_json.exists():
        raise HTTPException(
            status_code=404,
            detail="No se encontraron los datos procesados."
        )

    with ruta_json.open("r", encoding="utf-8") as archivo:
        paginas = json.load(archivo)

    # Reunir las imágenes del documento
    imagenes = []

    for pagina in paginas:
        for imagen in pagina.get("imagenes", []):
            imagenes.append({
                "documento": trabajo["archivo"],
                "pagina": pagina["pagina"],
                "nombre_archivo": imagen["nombre_archivo"],
                "bbox": imagen["bbox"]
            })

    return {
        "documento_id": identificador,
        "imagenes": imagenes
    }


@aplicacion.get("/documentos/{identificador}/imagenes/{nombre_imagen}")
def mostrar_imagen(identificador: str, nombre_imagen: str):

    # Comprobar que el documento existe y está listo
    trabajo = gestor_trabajos.consultar_trabajo(identificador)

    if not trabajo:
        raise HTTPException(
            status_code=404,
            detail="No se encontró el documento."
        )

    if trabajo["estado"] != "Completed":
        raise HTTPException(
            status_code=409,
            detail="El documento todavía no está listo."
        )

    # Evitar que se soliciten archivos fuera de su carpeta
    if Path(nombre_imagen).name != nombre_imagen:
        raise HTTPException(
            status_code=400,
            detail="Nombre de imagen no válido."
        )

    # Buscar la imagen dentro de la carpeta del documento
    ruta_imagen = (
        Path("data/imagenes")
        / identificador
        / nombre_imagen
    )

    if not ruta_imagen.is_file():
        raise HTTPException(
            status_code=404,
            detail="No se encontró la imagen."
        )

    return FileResponse(ruta_imagen)



