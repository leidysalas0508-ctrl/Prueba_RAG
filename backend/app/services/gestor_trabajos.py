
import json
from pathlib import Path
from threading import Lock
from uuid import uuid4


class GestorTrabajos:

    def __init__(self):
        # Archivo donde se conservarán los trabajos
        self.ruta_datos = Path("data/trabajos.json")
        self.ruta_datos.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.bloqueo = Lock()
        self.trabajos = {}

        # Recuperar los trabajos guardados anteriormente
        if self.ruta_datos.exists():
            with self.ruta_datos.open(
                "r",
                encoding="utf-8"
            ) as archivo:
                self.trabajos = json.load(archivo)

    def guardar_cambios(self):
        # Guardar primero en un archivo temporal
        ruta_temporal = self.ruta_datos.with_suffix(".tmp")

        with ruta_temporal.open(
            "w",
            encoding="utf-8"
        ) as archivo:
            json.dump(
                self.trabajos,
                archivo,
                ensure_ascii=False,
                indent=2
            )

        # Reemplazar el archivo anterior
        ruta_temporal.replace(self.ruta_datos)

    def crear_trabajo(self, nombre_archivo):
        identificador = str(uuid4())

        trabajo = {
            "job_id": identificador,
            "archivo": nombre_archivo,
            "estado": "Pending",
            "mensaje": "Documento pendiente de procesamiento"
        }

        with self.bloqueo:
            self.trabajos[identificador] = trabajo
            self.guardar_cambios()

        return trabajo.copy()

    def actualizar_trabajo(self, identificador, estado, mensaje):
        with self.bloqueo:
            if identificador in self.trabajos:
                self.trabajos[identificador]["estado"] = estado
                self.trabajos[identificador]["mensaje"] = mensaje

                self.guardar_cambios()

    def consultar_trabajo(self, identificador):
        with self.bloqueo:
            trabajo = self.trabajos.get(identificador)

            return trabajo.copy() if trabajo else None


gestor_trabajos = GestorTrabajos()
