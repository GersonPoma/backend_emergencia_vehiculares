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

