from enum import Enum as PyEnum

from sqlalchemy import Column, Integer, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship

from app.core.base_model import SoftDelete
from app.db.session import Base


class EstadoNotificacion(str, PyEnum):
    NOTIFICADO = "Notificado"
    ACEPTADO = "Aceptado"
    RECHAZADO = "Rechazado"


class AsignacionCandidato(Base, SoftDelete):
    __tablename__ = "asignacion_candidato"

    id = Column(Integer, primary_key=True)
    distancia_km = Column(Float, nullable=False)
    estado = Column(
        Enum(
            EstadoNotificacion,
            name="estado_notificacion_enum",
            native_enum=False,
            validate_strings=True
        ),
        nullable=False,
        default=EstadoNotificacion.NOTIFICADO,
    )

    incidente_id = Column(
        Integer,
        ForeignKey("incidente.id"),
        nullable=False,
    )
    taller_id = Column(
        Integer,
        ForeignKey("taller.id"),
        nullable=False,
    )

    incidente = relationship("Incidente", backref="asignaciones_candidato")
    taller = relationship("Taller", backref="asignaciones_candidato")
    orden_servicio = relationship("OrdenServicio", back_populates="asignacion_candidato", uselist=False)
