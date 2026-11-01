from pathlib import Path
import pymupdf


def procesar_pdf(ruta_pdf: str, carpeta_imagenes: str = "data/imagenes"):
    ruta_documento = Path(ruta_pdf)
    carpeta_salida = Path(carpeta_imagenes)

    if not ruta_documento.is_file():
        raise FileNotFoundError(f"No existe el PDF: {ruta_documento}")

    carpeta_salida.mkdir(parents=True, exist_ok=True)

    resultados = []

    with pymupdf.open(ruta_documento) as documento:
        for numero_pagina, pagina in enumerate(documento, start=1):
            bloques_texto = []
            imagenes_pagina = []

            # Extraer bloques de texto con coordenadas
            bloques = pagina.get_text("blocks")

            for bloque in bloques:
                x0, y0, x1, y1, contenido, *_ = bloque

                if not isinstance(contenido, str):
                    continue

                contenido = contenido.strip()

                if not contenido:
                    continue

                bloques_texto.append({
                    "texto": contenido,
                    "bbox": [x0, y0, x1, y1]
                })

            # Extraer imágenes con coordenadas
            imagenes = pagina.get_images(full=True)

            for numero_imagen, imagen in enumerate(imagenes, start=1):
                xref = imagen[0]
                datos_imagen = documento.extract_image(xref)

                extension = datos_imagen["ext"]
                contenido_imagen = datos_imagen["image"]

                nombre_archivo = f"pagina_{numero_pagina}_imagen_{numero_imagen}.{extension}"
                ruta_imagen = carpeta_salida / nombre_archivo
                ruta_imagen.write_bytes(contenido_imagen)

                rectangulos = pagina.get_image_rects(xref)
                coordenadas = []

                for rect in rectangulos:
                    coordenadas.append([rect.x0, rect.y0, rect.x1, rect.y1])

                imagenes_pagina.append({
                    "nombre_archivo": nombre_archivo,
                    "ruta": str(ruta_imagen),
                    "bbox": coordenadas
                })

            resultados.append({
                "pagina": numero_pagina,
                "bloques_texto": bloques_texto,
                "imagenes": imagenes_pagina
            })

    return resultados