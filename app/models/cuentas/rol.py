from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.core.base_model import SoftDelete
from app.db.session import Base
from app.models.cuentas.rol_privilegio import rol_privilegio


class Rol(Base, SoftDelete):
    __tablename__ = "rol"

    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)

    privilegios = relationship("Privilegio", secondary=rol_privilegio)