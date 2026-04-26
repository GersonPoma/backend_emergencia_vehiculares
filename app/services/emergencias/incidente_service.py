import math
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.paginacion import PaginacionSalida
from app.models.emergencias.incidente import EstadoIncidente, Incidente
from app.schemas.emergencias.incidente import IncidenteActualizar, IncidenteCrear


def crear(db: Session, data: IncidenteCrear, usuario_id: int) -> Incidente:
    incidente = Incidente()
    incidente.latitud = data.latitud
    incidente.longitud = data.longitud
    incidente.usuario_id = usuario_id
    db.add(incidente)
    db.commit()
    db.refresh(incidente)
    return incidente


def obtener_por_id(db: Session, incidente_id: int):
    return db.query(Incidente).filter(
        Incidente.id == incidente_id,
        Incidente.deleted == False,
    ).first()


def obtener_por_usuario_id(db: Session, usuario_id: int, pagina: int = 1, limite: int = 10) -> PaginacionSalida:
    skip = (pagina - 1) * limite
    query = db.query(Incidente).filter(
        Incidente.usuario_id == usuario_id,
        Incidente.deleted == False,
    )
    total = query.count()
    datos = query.offset(skip).limit(limite).all()
    return PaginacionSalida(
        datos=datos,
        total=total,
        pagina=pagina,
        limite=limite,
        total_paginas=math.ceil(total / limite) if limite else 1,
    )


def obtener_activo_por_usuario(db: Session, usuario_id: int) -> Incidente | None:
    return (
        db.query(Incidente)
        .filter(
            Incidente.usuario_id == usuario_id,
            Incidente.estado == EstadoIncidente.EN_PROCESO,
            Incidente.deleted == False,
        )
        .order_by(Incidente.fecha_hora.desc())
        .first()
    )


def actualizar(db: Session, incidente_id: int, data: IncidenteActualizar):
    incidente = obtener_por_id(db, incidente_id)
    if not incidente:
        return None

    if data.latitud is not None:
        incidente.latitud = data.latitud
    if data.longitud is not None:
        incidente.longitud = data.longitud
    if data.estado is not None:
        incidente.estado = data.estado
    if data.prioridad is not None:
        incidente.prioridad = data.prioridad

    incidente.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(incidente)
    return incidente


def cancelar_incidente(db: Session, incidente_id: int):
    incidente = obtener_por_id(db, incidente_id)
    if not incidente:
        return None

    if incidente.estado != EstadoIncidente.PENDIENTE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Solo se puede cancelar un incidente en estado Pendiente",
        )

    incidente.estado = EstadoIncidente.CANCELADO
    incidente.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(incidente)
    return incidente


