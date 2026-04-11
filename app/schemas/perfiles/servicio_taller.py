from pydantic import BaseModel


class ServicioTallerCrear(BaseModel):
    tipo_servicio: str
    taller_id: int


class ServicioTallerActualizar(BaseModel):
    tipo_servicio: str | None = None


class ServicioTallerSalida(BaseModel):
    id: int
    tipo_servicio: str
    taller_id: int

    class Config:
        from_attributes = True
