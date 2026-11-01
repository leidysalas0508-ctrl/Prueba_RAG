
from pathlib import Path
import chromadb


class BaseVectorial:

    def __init__(self):
        # Crear la carpeta de la base vectorial
        ruta_base = Path("data/base_vectorial")
        ruta_base.mkdir(parents=True, exist_ok=True)

        # Abrir la base de datos local
        self.cliente = chromadb.PersistentClient(
            path=str(ruta_base)
        )

        # Recuperar nuestra colección de documentos
        self.coleccion = self.cliente.get_or_create_collection(
            name="documentos_reales_rag",
            metadata={"hnsw:space": "cosine"}
        )

    def guardar_fragmento(self, fragmento, vector):
        # Identificar el documento de origen
        documento_id = fragmento.get(
            "documento_id",
            "documento_inicial"
        )

        # Guardar el fragmento y su vector
        self.coleccion.upsert(
            ids=[fragmento["id"]],
            embeddings=[vector],
            documents=[fragmento["texto"]],
            metadatas=[{
                "pagina": fragmento["pagina"],
                "columna": str(
                    fragmento.get("columna", "desconocida")
                ),
                "documento_id": documento_id
            }]
        )

    def buscar_similares(
        self,
        vector_pregunta,
        cantidad=3,
        documento_id=None
    ):
        # Preparar un filtro opcional por documento
        filtros = (
            {"documento_id": documento_id}
            if documento_id else None
        )

        # Contar los fragmentos disponibles
        if filtros:
            disponibles = self.coleccion.get(
                where=filtros,
                include=[]
            )
            total = len(disponibles["ids"])
        else:
            total = self.coleccion.count()

        if total == 0:
            return []

        # No solicitar más resultados de los disponibles
        cantidad = min(cantidad, total)

        # Realizar la búsqueda vectorial
        parametros = {
            "query_embeddings": [vector_pregunta],
            "n_results": cantidad,
            "include": ["documents", "metadatas", "distances"]
        }

        if filtros:
            parametros["where"] = filtros

        resultados = self.coleccion.query(**parametros)

        coincidencias = []

        for indice, identificador in enumerate(resultados["ids"][0]):
            coincidencias.append({
                "id": identificador,
                "texto": resultados["documents"][0][indice],
                "pagina": resultados["metadatas"][0][indice]["pagina"],
                "distancia": resultados["distances"][0][indice]
            })

        return coincidencias
