
import json
import logging
from pathlib import Path

from backend.app.services.pdf_processor import procesar_pdf
from backend.app.services.fragmentador import crear_fragmentos
from backend.app.services.servicio_embeddings import generar_embedding
from backend.app.services.base_vectorial import BaseVectorial
from backend.app.services.gestor_trabajos import gestor_trabajos

registro = logging.getLogger(__name__)


def procesar_documento_completo(identificador, ruta_archivo):
    try:
        gestor_trabajos.actualizar_trabajo(
            identificador,
            "Processing",
            "Extrayendo información del PDF"
        )

        # Crear carpetas independientes para cada documento
        carpeta_resultados = Path("data/procesados")
        carpeta_resultados.mkdir(parents=True, exist_ok=True)

        ruta_json = carpeta_resultados / f"{identificador}.json"
        carpeta_imagenes = f"data/imagenes/{identificador}"

        # Extraer textos, imágenes y coordenadas
        paginas = procesar_pdf(
            str(ruta_archivo),
            carpeta_imagenes
        )

        # Guardar el resultado de extracción
        with ruta_json.open("w", encoding="utf-8") as archivo:
            json.dump(
                paginas,
                archivo,
                ensure_ascii=False,
                indent=2
            )

        # Crear fragmentos
        fragmentos = crear_fragmentos(str(ruta_json))

        if not fragmentos:
            raise ValueError("El PDF no contiene texto procesable")

        gestor_trabajos.actualizar_trabajo(
            identificador,
            "Processing",
            f"Indexando {len(fragmentos)} fragmentos"
        )

        base = BaseVectorial()

        # Indexar cada fragmento
        for fragmento in fragmentos:
            fragmento["documento_id"] = identificador

        fragmento["id"] = (
            f"{identificador}_{fragmento['id']}"
        )

        vector = generar_embedding(fragmento["texto"])
        base.guardar_fragmento(fragmento, vector)  
        for fragmento in fragmentos:
            
            # Evitar identificadores repetidos entre documentos
            fragmento["id"] = (
                f"{identificador}_{fragmento['id']}"
            )

            vector = generar_embedding(fragmento["texto"])
            base.guardar_fragmento(fragmento, vector)

        gestor_trabajos.actualizar_trabajo(
            identificador,
            "Completed",
            f"Documento indexado: {len(fragmentos)} fragmentos"
        )

    except Exception:
        registro.exception(
            "Error procesando el documento %s",
            identificador
        )

        gestor_trabajos.actualizar_trabajo(
            identificador,
            "Failed",
            "No se pudo completar la indexación del documento"
        )
