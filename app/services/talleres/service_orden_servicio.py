import math

from sqlalchemy.orm import Session

from app.core.paginacion import PaginacionSalida
from app.models.talleres.orden_servicio import OrdenServicio


def formatear_tiempo_hms(segundos: int) -> str:
    horas = segundos // 3600
    minutos = (segundos % 3600) // 60
    segs = segundos % 60
    return f"{horas}:{minutos}:{segs:02d}"


def _mapear_orden_salida(orden) -> dict:
    return {
        "id": orden.id,
        "fecha_hora": orden.fecha_hora,
        "tiempo_estimado_llegada_segundos": orden.tiempo_estimado_llegada,
        "tiempo_estimado_llegada": formatear_tiempo_hms(orden.tiempo_estimado_llegada),
        "estado": orden.estado,
        "asignacion_candidato_id": orden.asignacion_candidato_id,
    }


def obtener_todos(db: Session, pagina: int = 1, limite: int = 10) -> PaginacionSalida:
    skip = (pagina - 1) * limite
    query = db.query(OrdenServicio).filter(OrdenServicio.deleted == False)
    total = query.count()
    datos = query.offset(skip).limit(limite).all()
    return PaginacionSalida(
        datos=[_mapear_orden_salida(orden) for orden in datos],
        total=total,
        pagina=pagina,
        limite=limite,
        total_paginas=math.ceil(total / limite) if limite else 1,
    )


def obtener_por_id(db: Session, orden_id: int):
    orden = db.query(OrdenServicio).filter(
        OrdenServicio.id == orden_id,
        OrdenServicio.deleted == False,
    ).first()
    if not orden:
        return None
    return _mapear_orden_salida(orden)


def obtener_por_incidente_id(db: Session, incidente_id: int):
    from app.models.talleres.asignacion_candidato import AsignacionCandidato, EstadoNotificacion
    orden = (
        db.query(OrdenServicio)
        .join(AsignacionCandidato, OrdenServicio.asignacion_candidato_id == AsignacionCandidato.id)
        .filter(
            AsignacionCandidato.incidente_id == incidente_id,
            AsignacionCandidato.estado == EstadoNotificacion.ACEPTADO,
            OrdenServicio.deleted == False,
        )
        .first()
    )
    if not orden:
        return None
    return _mapear_orden_salida(orden)


