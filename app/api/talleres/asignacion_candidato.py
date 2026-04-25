from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.talleres.asignacion_candidato import (
    AceptarEmergenciaSalida,
    AsignacionCandidatoSalida,
    RechazarEmergenciaSalida,
)
from app.services.talleres import service_asignacion

router = APIRouter(
    prefix="/asignaciones",
    tags=["Asignaciones"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/taller/{taller_id}/emergencias-pendientes", response_model=list[AsignacionCandidatoSalida])
def ver_emergencias_pendientes(taller_id: int, db: Session = Depends(get_db)):
    return service_asignacion.obtener_pendientes_por_taller(db, taller_id)


@router.post("/asignacion/{asignacion_id}/aceptar", response_model=AceptarEmergenciaSalida)
def aceptar_emergencia(asignacion_id: int, db: Session = Depends(get_db)):
    """Endpoint cuando el mecánico acepta una emergencia."""
    return service_asignacion.aceptar_asignacion(db=db, asignacion_id=asignacion_id)


@router.post("/asignacion/{asignacion_id}/rechazar", response_model=RechazarEmergenciaSalida)
def rechazar_emergencia(asignacion_id: int, db: Session = Depends(get_db)):
    """Endpoint cuando el mecánico rechaza o ignora una emergencia."""
    return service_asignacion.rechazar_asignacion(db=db, asignacion_id=asignacion_id)
