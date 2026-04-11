from datetime import datetime
import math

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.paginacion import PaginacionSalida
from app.core.security import hash_password
from app.models.cuentas.usuario import Usuario
from app.schemas.cuentas.usuario import UsuarioCrear, UsuarioActualizar


def verificar_username_disponible(db: Session, username: str, excluir_id: int = None):
    query = db.query(Usuario).filter(Usuario.username == username, Usuario.deleted == False)
    if excluir_id:
        query = query.filter(Usuario.id != excluir_id)
    if query.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El username '{username}' ya está en uso",
        )


def obtener_todos(db: Session, pagina: int = 1, limite: int = 10) -> PaginacionSalida:
    skip = (pagina - 1) * limite
    total = db.query(Usuario).filter(Usuario.deleted == False).count()
    datos = db.query(Usuario).filter(Usuario.deleted == False).offset(skip).limit(limite).all()
    return PaginacionSalida(
        datos=datos,
        total=total,
        pagina=pagina,
        limite=limite,
        total_paginas=math.ceil(total / limite) if limite else 1,
    )


def obtener_por_id(db: Session, usuario_id: int) -> Usuario | None:
    return db.query(Usuario).filter(Usuario.id == usuario_id, Usuario.deleted == False).first()


def crear(db: Session, data: UsuarioCrear) -> Usuario:
    verificar_username_disponible(db, data.username)
    usuario = Usuario(
        username=data.username,
        password=hash_password(data.password),
        rol_id=data.rol_id,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def actualizar(db: Session, usuario_id: int, data: UsuarioActualizar) -> Usuario | None:
    usuario = obtener_por_id(db, usuario_id)
    if not usuario:
        return None
    if data.username is not None:
        verificar_username_disponible(db, data.username, excluir_id=usuario_id)
        usuario.username = data.username
    if data.password is not None:
        usuario.password = hash_password(data.password)
    if data.rol_id is not None:
        usuario.rol_id = data.rol_id
    usuario.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(usuario)
    return usuario


def eliminar(db: Session, usuario_id: int) -> Usuario | None:
    usuario = obtener_por_id(db, usuario_id)
    if not usuario:
        return None
    usuario.soft_delete()
    db.commit()
    return usuario