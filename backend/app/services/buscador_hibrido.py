
from backend.app.services.buscador_bm25 import BuscadorBM25
from backend.app.services.base_vectorial import BaseVectorial
from backend.app.services.servicio_embeddings import generar_embedding


class BuscadorHibrido:

    def __init__(self, fragmentos):
        # Crear los dos buscadores
        self.buscador_palabras = BuscadorBM25(fragmentos)
        self.base_vectorial = BaseVectorial()

        # Guardar los fragmentos por identificador
        self.fragmentos = {
            fragmento["id"]: fragmento
            for fragmento in fragmentos
        }

    def buscar(self, pregunta, cantidad=5):
        # Buscar por palabras clave
        resultados_bm25 = self.buscador_palabras.buscar(
            pregunta,
            cantidad=10
        )

        # Convertir la pregunta en un embedding
        vector_pregunta = generar_embedding(pregunta)

        # Buscar por similitud semántica
        resultados_semanticos = self.base_vectorial.buscar_similares(
            vector_pregunta,
            cantidad=10
        )

        # Diccionario para combinar puntuaciones
        puntuaciones = {}

        # Constante habitual de Reciprocal Rank Fusion
        constante_rrf = 60

        # Sumar la contribución de BM25
        for posicion, resultado in enumerate(resultados_bm25, start=1):
            identificador = resultado["fragmento"]["id"]

            puntuaciones[identificador] = (
                puntuaciones.get(identificador, 0)
                + 1 / (constante_rrf + posicion)
            )

        # Sumar la contribución semántica
        for posicion, resultado in enumerate(resultados_semanticos, start=1):
            identificador = resultado["id"]

            puntuaciones[identificador] = (
                puntuaciones.get(identificador, 0)
                + 1 / (constante_rrf + posicion)
            )

        # Ordenar los fragmentos por puntuación combinada
        identificadores_ordenados = sorted(
            puntuaciones,
            key=puntuaciones.get,
            reverse=True
        )

        # Preparar los resultados finales
        resultados = []

        for identificador in identificadores_ordenados:
            if identificador not in self.fragmentos:
                continue

            fragmento = self.fragmentos[identificador]

            resultados.append({
                "id": identificador,
                "pagina": fragmento["pagina"],
                "texto": fragmento["texto"],
                "puntuacion": puntuaciones[identificador]
            })

            if len(resultados) >= cantidad:
                break

        return resultados
