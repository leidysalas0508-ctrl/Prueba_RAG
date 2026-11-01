import re
from rank_bm25 import BM25Okapi


def separar_palabras(texto):
    # Convertir a minúsculas y extraer palabras
    return re.findall(r"\w+", texto.lower())


class BuscadorBM25:

    def __init__(self, fragmentos):
        # Guardar los fragmentos originales
        self.fragmentos = fragmentos

        # Separar el texto de cada fragmento en palabras
        self.documentos = [
            separar_palabras(fragmento["texto"])
            for fragmento in fragmentos
        ]

        # Crear el índice de búsqueda
        self.modelo = BM25Okapi(self.documentos)

    def buscar(self, pregunta, cantidad=3):
        # Procesar las palabras de la pregunta
        palabras = separar_palabras(pregunta)

        # Calcular la relevancia de cada fragmento
        puntuaciones = self.modelo.get_scores(palabras)

        # Ordenar los resultados de mayor a menor
        indices = sorted(
            range(len(puntuaciones)),
            key=lambda indice: puntuaciones[indice],
            reverse=True
        )

        resultados = []

        for indice in indices[:cantidad]:
            if puntuaciones[indice] <= 0:
                continue

            resultados.append({
                "fragmento": self.fragmentos[indice],
                "puntuacion": float(puntuaciones[indice])
            })

        return resultados