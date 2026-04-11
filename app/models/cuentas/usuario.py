from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.base_model import SoftDelete
from app.db.session import Base


class Usuario(Base, SoftDelete):
    __tablename__ = "usuario"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    rol_id = Column(Integer, ForeignKey("rol.id"), nullable=False)

    rol = relationship("Rol", backref="usuarios")
