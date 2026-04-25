import math
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.paginacion import PaginacionSalida
from app.core.security import hash_password
from app.models.cuentas.usuario import Usuario
from app.services.cuentas.usuario_service import verificar_username_disponible
from app.models.perfiles.taller import Taller
from app.schemas.perfiles.taller import TallerRegistrar, TallerActualizar


def obtener_rol_por_nombre(db: Session, nombre: str):
    from app.models.cuentas.rol import Rol
    return db.query(Rol).filter(Rol.nombre == nombre, Rol.deleted == False).first()


def registrar(db: Session, data: TallerRegistrar) -> Taller:
    verificar_username_disponible(db, data.username)
    rol = obtener_rol_por_nombre(db, "admin_taller")
    usuario = Usuario(
        username=data.username,
        password=hash_password(data.password),
        rol_id=rol.id,
    )
    db.add(usuario)
    db.flush()

    taller = Taller(
        nombre=data.nombre,
        telefono=data.telefono,
        direccion=data.direccion,
        latitud=data.latitud,
        longitud=data.longitud,
        usuario_id=usuario.id,
    )
    db.add(taller)
    db.commit()
    db.refresh(taller)
    return taller


def obtener_todos(db: Session, pagina: int = 1, limite: int = 10) -> PaginacionSalida:
    skip = (pagina - 1) * limite
    total = db.query(Taller).filter(Taller.deleted == False).count()
    datos = db.query(Taller).filter(Taller.deleted == False).offset(skip).limit(limite).all()
    return PaginacionSalida(
        datos=datos,
        total=total,
        pagina=pagina,
        limite=limite,
        total_paginas=math.ceil(total / limite) if limite else 1,
    )


def obtener_por_id(db: Session, taller_id: int) -> Taller | None:
    return db.query(Taller).filter(Taller.id == taller_id, Taller.deleted == False).first()


def actualizar(db: Session, taller_id: int, data: TallerActualizar) -> Taller | None:
    taller = obtener_por_id(db, taller_id)
    if not taller:
        return None
    if data.nombre is not None:
        taller.nombre = data.nombre
    if data.telefono is not None:
        taller.telefono = data.telefono
    if data.direccion is not None:
        taller.direccion = data.direccion
    if data.latitud is not None:
        taller.latitud = data.latitud
    if data.longitud is not None:
        taller.longitud = data.longitud
    if data.disponible is not None:
        taller.disponible = data.disponible
    taller.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(taller)
    return taller


def eliminar(db: Session, taller_id: int) -> Taller | None:
    taller = obtener_por_id(db, taller_id)
    if not taller:
        return None
    taller.soft_delete()
    usuario = db.query(Usuario).filter(Usuario.id == taller.usuario_id).first()
    if usuario:
        usuario.soft_delete()
    db.commit()
    return taller
