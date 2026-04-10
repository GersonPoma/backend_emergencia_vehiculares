from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Sistema de Emergencias Vehiculares",
    description="Backend para gestión de incidentes y asistencia",
    version="1.0.0"
)

# Configuración de CORS para Angular
origins = [
    "http://localhost:4200",  # El puerto por defecto de Angular
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "Online", "message": "API de Emergencias Vehiculares lista"}