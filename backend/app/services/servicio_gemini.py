
import os
import time
import logging

from dotenv import load_dotenv
from google import genai
from google.genai import errors

# Configurar el registro de eventos
logging.basicConfig(level=logging.INFO)
registro = logging.getLogger(__name__)

# Cargar las variables privadas
load_dotenv()


def generar_respuesta(pregunta: str):
    clave_api = os.getenv("GEMINI_API_KEY")

    if not clave_api:
        raise ValueError("No se encontró la clave de Gemini")

    cliente = genai.Client(api_key=clave_api)

    maximo_intentos = 3

    for intento in range(maximo_intentos):
        try:
            respuesta = cliente.models.generate_content(
                model="gemini-3.8-flash",
                contents=pregunta
            )

            if not respuesta.text:
                raise ValueError("Gemini no devolvió texto")

            return respuesta.text

        except (errors.ClientError, errors.ServerError) as error:
            codigo = getattr(error, "code", None)

            # Reintentar únicamente ante errores temporales
            if codigo not in (429, 500, 502, 503, 504):
                raise

            if intento == maximo_intentos - 1:
                registro.error(
                    "Gemini no respondió después de %s intentos",
                    maximo_intentos
                )
                raise

            espera = 2 ** (intento + 1)

            registro.warning(
                "Gemini devolvió HTTP %s. "
                "Reintentando en %s segundos...",
                codigo,
                espera
            )

            time.sleep(espera)
