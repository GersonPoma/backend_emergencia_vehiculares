from pydantic import BaseModel

from app.models.talleres.asignacion_candidato import EstadoNotificacion


class AsignacionCandidatoSalida(BaseModel):
    id: int
    distancia_km: float
    estado: EstadoNotificacion
    incidente_id: int
    taller_id: int

    class Config:
        from_attributes = True


class AceptarEmergenciaSalida(BaseModel):
    estado: str
    mensaje: str
    orden_servicio_id: int
    tiempo_estimado_llegada: int


class RechazarEmergenciaSalida(BaseModel):
    estado: str
    mensaje: str

