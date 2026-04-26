from typing import Optional

from pydantic import BaseModel


class DetalleOrdenEntrada(BaseModel):
    precio_cobrado: float
    comentario: Optional[str] = None
    orden_servicio_id: int
    servicio_taller_id: int


class DetalleOrdenSalida(BaseModel):
    id: int
    precio_cobrado: float
    comentario: Optional[str]
    orden_servicio_id: int
    servicio_taller_id: int
    nombre_servicio: str
    categoria: str
