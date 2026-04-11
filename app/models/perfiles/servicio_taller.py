from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.base_model import SoftDelete
from app.db.session import Base


class ServicioTaller(Base, SoftDelete):
    __tablename__ = "servicio_taller"

    id = Column(Integer, primary_key=True)
    tipo_servicio = Column(String(150), nullable=False)
    taller_id = Column(Integer, ForeignKey("taller.id"), nullable=False)

    taller = relationship("Taller", back_populates="servicios")
