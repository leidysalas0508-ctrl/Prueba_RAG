
import json


def crear_fragmentos(ruta_json: str):
    # Leer la información extraída del documento PDF
    with open(ruta_json, "r", encoding="utf-8") as archivo:
        paginas = json.load(archivo)

    fragmentos = []

    # Recorrer las páginas del documento
    for pagina in paginas:
        numero_pagina = pagina["pagina"]
        bloques = pagina["bloques_texto"]

        # Organizar los textos por columnas
        columnas = {
            "izquierda": [],
            "derecha": []
        }

        for bloque in bloques:
            # Eliminar espacios al principio y al final
            texto_limpio = bloque["texto"].strip()

            # Ignorar textos vacíos
            if not texto_limpio:
                continue

            # Ignorar textos que solo contienen signos
            if not any(caracter.isalnum() for caracter in texto_limpio):
                continue

            # Identificar la posición horizontal del texto
            x0, y0, x1, y1 = bloque["bbox"]
            centro_x = (x0 + x1) / 2

            # Separar las columnas del PDF de prueba
            columna = "izquierda" if centro_x < 306 else "derecha"

            columnas[columna].append(bloque)

        # Procesar cada columna de forma independiente
        for nombre_columna, bloques_columna in columnas.items():

            # Ordenar los bloques de arriba hacia abajo
            bloques_columna.sort(
                key=lambda bloque: bloque["bbox"][1]
            )

            grupo = []

            # Guardar los bloques agrupados como un fragmento
            def guardar_grupo():
                if not grupo:
                    return

                texto = "\n".join(
                    bloque["texto"] for bloque in grupo
                )

                fragmentos.append({
                    "id": f"fragmento_{len(fragmentos) + 1}",
                    "pagina": numero_pagina,
                    "columna": nombre_columna,
                    "texto": texto,
                    "bbox": [
                        min(b["bbox"][0] for b in grupo),
                        min(b["bbox"][1] for b in grupo),
                        max(b["bbox"][2] for b in grupo),
                        max(b["bbox"][3] for b in grupo)
                    ]
                })

            # Agrupar los bloques cercanos
            for bloque in bloques_columna:
                if grupo:
                    distancia = (
                        bloque["bbox"][1] - grupo[-1]["bbox"][3]
                    )

                    longitud_actual = sum(
                        len(b["texto"]) for b in grupo
                    )

                    # Crear un nuevo grupo si los bloques
                    # están muy separados o son muy extensos
                    if (
                        distancia > 24
                        or longitud_actual + len(bloque["texto"]) > 900
                    ):
                        guardar_grupo()
                        grupo = []

                grupo.append(bloque)

            # Guardar el último grupo de cada columna
            guardar_grupo()

    return fragmentos
