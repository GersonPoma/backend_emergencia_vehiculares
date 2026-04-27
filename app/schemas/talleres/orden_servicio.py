from datetime import datetime

from pydantic import BaseModel

from app.models.talleres.orden_servicio import EstadoOperacion


class OrdenServicioSalida(BaseModel):
    id: int
    fecha_hora: datetime
    tiempo_estimado_llegada_segundos: int
    tiempo_estimado_llegada: str
    estado: EstadoOperacion
    asignacion_candidato_id: int

    incidente_id: int
    nombre_cliente: str
    tiene_transaccion: bool = False
    transaccion_id: int | None = None
