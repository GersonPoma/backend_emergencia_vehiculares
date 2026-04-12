import math
from datetime import datetime

from sqlalchemy.orm import Session

from app.core.paginacion import PaginacionSalida
from app.models.perfiles.servicio_taller import ServicioTaller
from app.schemas.perfiles.servicio_taller import ServicioTallerCrear, ServicioTallerActualizar


def obtener_por_taller(db: Session, taller_id: int, pagina: int = 1, limite: int = 10) -> PaginacionSalida:
    skip = (pagina - 1) * limite
    query = db.query(ServicioTaller).filter(ServicioTaller.taller_id == taller_id, ServicioTaller.deleted == False)
    total = query.count()
    datos = query.offset(skip).limit(limite).all()
    return PaginacionSalida(
        datos=datos,
        total=total,
        pagina=pagina,
        limite=limite,
        total_paginas=math.ceil(total / limite) if limite else 1,
    )


def obtener_por_id(db: Session, servicio_id: int) -> ServicioTaller | None:
    return db.query(ServicioTaller).filter(ServicioTaller.id == servicio_id, ServicioTaller.deleted == False).first()


def crear(db: Session, data: ServicioTallerCrear) -> ServicioTaller:
    servicio = ServicioTaller(tipo_servicio=data.tipo_servicio, precio=data.precio, taller_id=data.taller_id)
    db.add(servicio)
    db.commit()
    db.refresh(servicio)
    return servicio


def actualizar(db: Session, servicio_id: int, data: ServicioTallerActualizar) -> ServicioTaller | None:
    servicio = obtener_por_id(db, servicio_id)
    if not servicio:
        return None
    if data.tipo_servicio is not None:
        servicio.tipo_servicio = data.tipo_servicio
    if data.precio is not None:
        servicio.precio = data.precio
    servicio.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(servicio)
    return servicio


def eliminar(db: Session, servicio_id: int) -> ServicioTaller | None:
    servicio = obtener_por_id(db, servicio_id)
    if not servicio:
        return None
    servicio.soft_delete()
    db.commit()
    return servicio