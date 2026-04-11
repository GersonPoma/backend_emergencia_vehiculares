from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import Base, engine, SessionLocal
from app.db import seeder

# Modelos cuentas
from app.models.cuentas import rol, usuario, privilegio, rol_privilegio  # noqa: F401
# Modelos perfiles
from app.models.perfiles import cliente, vehiculo, taller, servicio_taller, tecnico  # noqa: F401

# APIs cuentas
from app.api.cuentas import auth, rol as rol_api, usuario as usuario_api, privilegio as privilegio_api
# APIs perfiles
from app.api.perfiles import (
    cliente as cliente_api,
    vehiculo as vehiculo_api,
    taller as taller_api,
    servicio_taller as servicio_taller_api,
    tecnico as tecnico_api,
)

Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    seeder.ejecutar(db)
finally:
    db.close()

app = FastAPI(
    title="AutoSOS",
    description="Backend para gestión de emergencias vehiculares en tiempo real",
    version="1.0.0"
)

origins = [
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cuentas
app.include_router(auth.router)
app.include_router(rol_api.router)
app.include_router(usuario_api.router)
app.include_router(privilegio_api.router)

# Perfiles
app.include_router(cliente_api.router)
app.include_router(vehiculo_api.router)
app.include_router(taller_api.router)
app.include_router(servicio_taller_api.router)
app.include_router(tecnico_api.router)


@app.get("/")
def read_root():
    return {"status": "Online", "message": "API de Emergencias Vehiculares lista"}
