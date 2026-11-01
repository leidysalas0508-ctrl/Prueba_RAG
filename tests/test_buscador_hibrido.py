
from unittest.mock import patch

from backend.app.services.buscador_hibrido import BuscadorHibrido


def test_busqueda_hibrida():
    # Crear fragmentos pequeños para la prueba
    fragmentos = [
        {
            "id": "fragmento_1",
            "pagina": 1,
            "texto": "Los ejercicios deben adaptarse a cada persona."
        },
        {
            "id": "fragmento_2",
            "pagina": 2,
            "texto": "El sistema utiliza inteligencia artificial."
        }
    ]

    # Simular los servicios externos
    with patch(
        "backend.app.services.buscador_hibrido.BaseVectorial"
    ) as base_falsa, patch(
        "backend.app.services.buscador_hibrido.generar_embedding"
    ) as embedding_falso:

        embedding_falso.return_value = [0.1, 0.2, 0.3]

        base_falsa.return_value.buscar_similares.return_value = [
            {
                "id": "fragmento_1",
                "pagina": 1,
                "texto": fragmentos[0]["texto"],
                "distancia": 0.2
            }
        ]

        # Crear el buscador híbrido
        buscador = BuscadorHibrido(fragmentos)

        # Ejecutar una pregunta
        resultados = buscador.buscar(
            "¿Cómo adaptar ejercicios a cada persona?",
            cantidad=2
        )

    # Verificar que obtuvimos resultados
    assert len(resultados) > 0
    assert resultados[0]["id"] == "fragmento_1"
