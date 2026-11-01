
from unittest.mock import patch, MagicMock

from backend.app.services.servicio_gemini import generar_respuesta


def test_generar_respuesta_correctamente():
    # Simular una respuesta exitosa de Gemini
    respuesta_falsa = MagicMock()
    respuesta_falsa.text = "Respuesta de prueba"

    cliente_falso = MagicMock()
    cliente_falso.models.generate_content.return_value = respuesta_falsa

    # Reemplazar temporalmente el cliente real
    with patch(
        "backend.app.services.servicio_gemini.genai.Client",
        return_value=cliente_falso
    ):
        with patch(
            "backend.app.services.servicio_gemini.os.getenv",
            return_value="clave_de_prueba"
        ):
            respuesta = generar_respuesta(
                "¿Qué es un sistema RAG?"
            )

    assert respuesta == "Respuesta de prueba"
    cliente_falso.models.generate_content.assert_called_once()
