import math

from sqlalchemy.orm import Session

from app.core.paginacion import PaginacionSalida
from app.models.pagos.detalle_orden import DetalleOrden
from app.schemas.pagos.detalle_orden import DetalleOrdenEntrada


def _mapear_salida(detalle: DetalleOrden) -> dict:
    return {
        "id": detalle.id,
        "precio_cobrado": detalle.precio_cobrado,
        "comentario": detalle.comentario,
        "orden_servicio_id": detalle.orden_servicio_id,
        "servicio_taller_id": detalle.servicio_taller_id,
        "nombre_servicio": detalle.servicio_taller.nombre if detalle.servicio_taller else "",
        "categoria": detalle.servicio_taller.categoria if detalle.servicio_taller else "",
    }


def crear(db: Session, entrada: DetalleOrdenEntrada) -> dict:
    detalle = DetalleOrden(
        precio_cobrado=entrada.precio_cobrado,
        comentario=entrada.comentario,
        orden_servicio_id=entrada.orden_servicio_id,
        servicio_taller_id=entrada.servicio_taller_id,
    )
    db.add(detalle)
    db.commit()
    db.refresh(detalle)
    return _mapear_salida(detalle)


def obtener_por_orden(db: Session, orden_id: int, pagina: int = 1, limite: int = 10) -> PaginacionSalida:
    skip = (pagina - 1) * limite
    query = db.query(DetalleOrden).filter(
        DetalleOrden.orden_servicio_id == orden_id,
        DetalleOrden.deleted == False,
    )
    total = query.count()
    datos = query.offset(skip).limit(limite).all()
    return PaginacionSalida(
        datos=[_mapear_salida(d) for d in datos],
        total=total,
        pagina=pagina,
        limite=limite,
        total_paginas=math.ceil(total / limite) if limite else 1,
    )


def obtener_por_id(db: Session, detalle_id: int):
    detalle = db.query(DetalleOrden).filter(
        DetalleOrden.id == detalle_id,
        DetalleOrden.deleted == False,
    ).first()
    if not detalle:
        return None
    return _mapear_salida(detalle)


def eliminar(db: Session, detalle_id: int) -> bool:
    detalle = db.query(DetalleOrden).filter(
        DetalleOrden.id == detalle_id,
        DetalleOrden.deleted == False,
    ).first()
    if not detalle:
        return False
    detalle.soft_delete()
    db.commit()
    return True
