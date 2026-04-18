from sqlalchemy.orm import Session

from app.models.cuentas.privilegio import Privilegio
from app.models.cuentas.rol import Rol

ROLES = [
    "cliente",
    "tecnico",
    "admin_taller",
]

PRIVILEGIOS = [
    # Roles
    {"nombre": "ver_roles",          "descripcion": "Listar y consultar roles"},
    {"nombre": "crear_rol",          "descripcion": "Crear nuevos roles"},
    {"nombre": "actualizar_rol",     "descripcion": "Editar roles existentes"},
    {"nombre": "eliminar_rol",       "descripcion": "Eliminar roles (lógico)"},
    # Usuarios
    {"nombre": "ver_usuarios",       "descripcion": "Listar y consultar usuarios"},
    {"nombre": "crear_usuario",      "descripcion": "Crear nuevos usuarios"},
    {"nombre": "actualizar_usuario", "descripcion": "Editar usuarios existentes"},
    {"nombre": "eliminar_usuario",   "descripcion": "Eliminar usuarios (lógico)"},
    # Privilegios
    {"nombre": "ver_privilegios",    "descripcion": "Listar y consultar privilegios"},
    {"nombre": "asignar_privilegio", "descripcion": "Asignar privilegios a roles"},
    {"nombre": "remover_privilegio", "descripcion": "Remover privilegios de roles"},
    # Clientes
    {"nombre": "ver_clientes",       "descripcion": "Listar y consultar clientes"},
    {"nombre": "eliminar_cliente",   "descripcion": "Eliminar clientes (lógico)"},
    # Talleres
    {"nombre": "ver_talleres",       "descripcion": "Listar y consultar talleres"},
    {"nombre": "eliminar_taller",    "descripcion": "Eliminar talleres (lógico)"},
    # Técnicos
    {"nombre": "ver_tecnicos",       "descripcion": "Listar y consultar técnicos"},
    {"nombre": "crear_tecnico",      "descripcion": "Crear técnicos"},
    {"nombre": "actualizar_tecnico", "descripcion": "Editar técnicos"},
    {"nombre": "eliminar_tecnico",   "descripcion": "Eliminar técnicos (lógico)"},
    # Servicios taller
    {"nombre": "ver_servicios",      "descripcion": "Listar servicios de talleres"},
    {"nombre": "gestionar_servicios","descripcion": "Crear, editar y eliminar servicios"},
    # Emergencias
    {"nombre": "crear_incidente",        "descripcion": "Registrar nuevos incidentes"},
    {"nombre": "ver_incidente",          "descripcion": "Consultar incidente por ID"},
    {"nombre": "ver_incidentes_usuario", "descripcion": "Listar incidentes por usuario"},
    {"nombre": "cancelar_incidente",     "descripcion": "Cancelar incidente por ID"},
    #{"nombre": "actualizar_incidente",   "descripcion": "Actualizar estado o prioridad de incidentes"},
    # Evidencia
    {"nombre": "crear_evidencia",        "descripcion": "Registrar nuevas evidencias"},
    {"nombre": "ver_evidencia",          "descripcion": "Consultar evidencia por ID"},
    {"nombre": "ver_evidencias_incidente","descripcion": "Listar evidencias por incidente"},
    {"nombre": "actualizar_evidencia",   "descripcion": "Editar evidencias existentes"},
]


def ejecutar(db: Session):
    for nombre in ROLES:
        existe = db.query(Rol).filter(Rol.nombre == nombre).first()
        if not existe:
            db.add(Rol(nombre=nombre))
    db.commit()

    for item in PRIVILEGIOS:
        existe = db.query(Privilegio).filter(Privilegio.nombre == item["nombre"]).first()
        if not existe:
            db.add(Privilegio(nombre=item["nombre"], descripcion=item["descripcion"]))
    db.commit()
