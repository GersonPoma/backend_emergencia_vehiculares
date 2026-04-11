from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    id_usuario: int
    id_perfil: int | None = None   # id_cliente o id_tecnico
    id_taller: int | None = None   # para admin_taller y tecnico
    rol: str
    privilegios: list[str] = []


class UsuarioCrear(BaseModel):
    username: str
    password: str
    rol_id: int


class UsuarioActualizar(BaseModel):
    username: str | None = None
    password: str | None = None
    rol_id: int | None = None


class UsuarioSalida(BaseModel):
    id: int
    username: str
    rol_id: int

    class Config:
        from_attributes = True