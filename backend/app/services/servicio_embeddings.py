
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

# Cargar la clave privada desde .env
load_dotenv()


def generar_embedding(texto: str):
    # Obtener la clave de Gemini
    clave_api = os.getenv("GEMINI_API_KEY")

    if not clave_api:
        raise ValueError("No se encontró la clave de Gemini")

    # Crear el cliente
    cliente = genai.Client(api_key=clave_api)

    # Convertir el texto en un vector numérico
    resultado = cliente.models.embed_content(
        model="gemini-embedding-2",
        contents=texto,
        config=types.EmbedContentConfig(
            output_dimensionality=768
        )
    )

    if not resultado.embeddings:
        raise ValueError("No se generó ningún embedding")

    return resultado.embeddings[0].values
