from pydantic import BaseModel


class RolCrear(BaseModel):
    nombre: str


class RolActualizar(BaseModel):
    nombre: str


class RolSalida(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True