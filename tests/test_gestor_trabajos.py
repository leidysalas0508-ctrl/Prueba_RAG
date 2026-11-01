
from backend.app.services.gestor_trabajos import GestorTrabajos


def test_crear_y_consultar_trabajo(tmp_path):
    # Crear un gestor independiente para esta prueba
    gestor = GestorTrabajos()

    # Utilizar un archivo temporal para no modificar los datos reales
    gestor.ruta_datos = tmp_path / "trabajos_prueba.json"
    gestor.trabajos = {}

    # Simular la recepción de un documento
    trabajo = gestor.crear_trabajo("documento_prueba.pdf")

    # Comprobar que el trabajo se creó correctamente
    assert trabajo["estado"] == "Pending"
    assert trabajo["archivo"] == "documento_prueba.pdf"
    assert trabajo["job_id"]

    # Cambiar el estado del documento
    gestor.actualizar_trabajo(
        trabajo["job_id"],
        "Completed",
        "Documento procesado correctamente"
    )

    # Consultar nuevamente el trabajo
    resultado = gestor.consultar_trabajo(trabajo["job_id"])

    # Verificar el resultado
    assert resultado["estado"] == "Completed"
    assert resultado["mensaje"] == "Documento procesado correctamente"
    assert gestor.ruta_datos.exists()
