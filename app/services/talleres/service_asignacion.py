import math
from fastapi import HTTPException
from sqlalchemy.orm import Session, subqueryload

from app.models.perfiles.servicio_taller import ServicioTaller
from app.models.perfiles.taller import Taller
from app.models.talleres.asignacion_candidato import AsignacionCandidato, EstadoNotificacion
from app.models.talleres.orden_servicio import OrdenServicio, EstadoOperacion


# ==========================================
# 1. MATEMÁTICA: CÁLCULO DE DISTANCIA
# ==========================================
def calcular_distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Fórmula de Haversine para calcular la distancia exacta en línea recta entre dos coordenadas GPS."""
    R = 6371.0  # Radio de la Tierra en kilómetros
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return round(R * c, 2)


def _subquery_talleres_contactados_por_incidente(db: Session, incidente_id: int):
    return (
        db.query(AsignacionCandidato.taller_id)
        .filter(AsignacionCandidato.incidente_id == incidente_id)
        .subquery()
    )


def _obtener_talleres_validos_para_broadcast(db: Session, categoria_problema: str, talleres_contactados_subquery):
    return (
        db.query(Taller)
        .join(ServicioTaller, Taller.id == ServicioTaller.taller_id)
        .options(subqueryload(Taller.servicios))
        .filter(
            Taller.disponible == True,
            Taller.deleted == False,
            ServicioTaller.categoria == categoria_problema,
            ~Taller.id.in_(talleres_contactados_subquery),
        )
        .all()
    )


def _obtener_asignacion_por_id(db: Session, asignacion_id: int):
    return db.query(AsignacionCandidato).filter(AsignacionCandidato.id == asignacion_id).first()


def _obtener_ganador_previo(db: Session, incidente_id: int):
    return db.query(AsignacionCandidato).filter(
        AsignacionCandidato.incidente_id == incidente_id,
        AsignacionCandidato.estado == EstadoNotificacion.ACEPTADO,
    ).first()


def _rechazar_otros_candidatos(db: Session, incidente_id: int, asignacion_id: int) -> None:
    db.query(AsignacionCandidato).filter(
        AsignacionCandidato.incidente_id == incidente_id,
        AsignacionCandidato.id != asignacion_id,
    ).update({"estado": EstadoNotificacion.RECHAZADO})


# ==========================================
# 2. ALGORITMO: BÚSQUEDA Y DIFUSIÓN (BROADCASTING)
# ==========================================
def buscar_y_notificar_talleres(
        db: Session,
        incidente_id: int,
        incidente_lat: float,
        incidente_lon: float,
        categoria_problema: str,
        prioridad: str,
        limite_candidatos: int = 3,
        distancia_maxima: float = 20.0
):
    """
    Busca a los talleres que ofrecen el servicio, calcula quiénes son los más óptimos
    según la prioridad, y les crea una notificación pendiente.
    """

    # ---------------------------------------------------------
    # LA MEJORA: Obtener los IDs de los talleres que YA participaron
    # ---------------------------------------------------------
    talleres_contactados_subquery = _subquery_talleres_contactados_por_incidente(db, incidente_id)

    # Paso A: Filtro en Base de Datos (Talleres disponibles, con servicio, Y QUE NO HAYAN SIDO CONTACTADOS)
    talleres_validos = _obtener_talleres_validos_para_broadcast(
        db,
        categoria_problema,
        talleres_contactados_subquery,
    )

    if not talleres_validos:
        return []  # No hay talleres disponibles para este problema

    # Paso B: Evaluación de Distancia y Precio
    evaluados = []
    for taller in talleres_validos:
        distancia = calcular_distancia_km(incidente_lat, incidente_lon, taller.latitud, taller.longitud)

        # Opcional: Ignorar talleres que estén a más de 20 km para no hacerlos viajar tanto
        if distancia > distancia_maxima:
            continue

        # Buscamos el precio del servicio específico dentro de la relación del taller
        servicio = next((s for s in taller.servicios if s.categoria == categoria_problema), None)
        precio_servicio = servicio.precio if servicio else 0.0

        evaluados.append({
            "taller_id": taller.id,
            "distancia_km": distancia,
            "precio": precio_servicio
        })

    # Paso C: La Inteligencia de Asignación (Reglas de Negocio)
    if prioridad == "Alta":
        # Prioridad Alta: La vida o el auto corren riesgo. Solo importa llegar rápido.
        evaluados.sort(key=lambda x: x["distancia_km"])
    elif prioridad == "Baja":
        # Prioridad Baja: No hay prisa. El cliente prefiere lo más barato.
        evaluados.sort(key=lambda x: (x["precio"], x["distancia_km"]))
    else:
        # Prioridad Media: Distancia por defecto
        evaluados.sort(key=lambda x: x["distancia_km"])

    # Paso D: Seleccionamos solo el "Top N" (Por defecto los 3 mejores)
    top_candidatos = evaluados[:limite_candidatos]

    # Paso E: Creamos las notificaciones en la BD
    nuevas_notificaciones = []
    for candidato in top_candidatos:
        nueva_asignacion = AsignacionCandidato(
            incidente_id=incidente_id,
            taller_id=candidato["taller_id"],
            distancia_km=candidato["distancia_km"],
            estado=EstadoNotificacion.NOTIFICADO
        )
        db.add(nueva_asignacion)
        nuevas_notificaciones.append(nueva_asignacion)

    db.commit()

    # Devolvemos las notificaciones creadas para que tu controlador las mande por WebSockets o Push a Flutter
    return nuevas_notificaciones


# ==========================================
# 4. CONSULTA: EMERGENCIAS PENDIENTES
# ==========================================
def obtener_pendientes_por_taller(db: Session, taller_id: int) -> list[AsignacionCandidato]:
    return (
        db.query(AsignacionCandidato)
        .filter(
            AsignacionCandidato.taller_id == taller_id,
            AsignacionCandidato.estado == EstadoNotificacion.NOTIFICADO,
            AsignacionCandidato.deleted == False,
        )
        .all()
    )


def contar_pendientes_por_incidente(db: Session, incidente_id: int) -> int:
    return (
        db.query(AsignacionCandidato)
        .filter(
            AsignacionCandidato.incidente_id == incidente_id,
            AsignacionCandidato.estado == EstadoNotificacion.NOTIFICADO,
            AsignacionCandidato.deleted == False,
        )
        .count()
    )


# ==========================================
# 3. CONCURRENCIA: ACEPTACIÓN DE LA ORDEN
# ==========================================
def taller_acepta_incidente(db: Session, asignacion_id: int):
    """
    Controla la carrera (Race Condition). Se ejecuta cuando un mecánico
    presiona 'Aceptar' en su app de Flutter.
    """
    # Paso A: Buscamos la notificación a la que el mecánico le dio clic
    asignacion = _obtener_asignacion_por_id(db, asignacion_id)

    if not asignacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada.")

    # Si alguien más ya rechazó esto o el cliente lo canceló
    if asignacion.estado != EstadoNotificacion.NOTIFICADO:
        raise HTTPException(status_code=400, detail="Esta solicitud ya no está disponible.")

    # Paso B: EL ÁRBITRO DE CONCURRENCIA - ¿Alguien más ya ganó este incidente?
    ganador_previo = _obtener_ganador_previo(db, asignacion.incidente_id)

    if ganador_previo:
        # El mecánico fue muy lento. Le cambiamos su estado a RECHAZADO para limpiar su pantalla
        asignacion.estado = EstadoNotificacion.RECHAZADO
        db.commit()
        raise HTTPException(status_code=400, detail="Otro taller aceptó esta emergencia antes que tú.")

    # Paso C: ¡TENEMOS UN GANADOR! (El mecánico actual se lleva el incidente)
    asignacion.estado = EstadoNotificacion.ACEPTADO

    # Paso D: Descalificamos a los perdedores (Rechazamos a los demás candidatos del mismo incidente)
    _rechazar_otros_candidatos(db, asignacion.incidente_id, asignacion_id)

    # Paso E: CREACIÓN DE LA ORDEN DE SERVICIO
    # Guardamos el tiempo estimado en segundos: (3 min por km + 5 min base) * 60
    tiempo_calculado = (int(asignacion.distancia_km * 3) + 5) * 60

    nueva_orden = OrdenServicio(
        asignacion_candidato_id=asignacion.id,
        tiempo_estimado_llegada=tiempo_calculado,
        estado=EstadoOperacion.EN_CAMINO
    )
    db.add(nueva_orden)

    # Paso F: Guardamos todo (El ganador, los perdedores y la nueva orden) en una sola transacción
    db.commit()
    db.refresh(nueva_orden)

    return nueva_orden


def aceptar_asignacion(db: Session, asignacion_id: int) -> dict:
    """Orquesta la aceptación y arma la respuesta consumible por la API."""
    orden = taller_acepta_incidente(db=db, asignacion_id=asignacion_id)
    return {
        "estado": "exito",
        "mensaje": "¡Felicidades! Has ganado esta emergencia.",
        "orden_servicio_id": orden.id,
        "tiempo_estimado_llegada": orden.tiempo_estimado_llegada,
    }


def taller_rechaza_incidente(db: Session, asignacion_id: int) -> AsignacionCandidato:
    """Marca una asignacion como rechazada si aun estaba pendiente."""
    asignacion = db.query(AsignacionCandidato).filter(
        AsignacionCandidato.id == asignacion_id,
        AsignacionCandidato.deleted == False,
    ).first()

    if not asignacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada.")

    if asignacion.estado != EstadoNotificacion.NOTIFICADO:
        raise HTTPException(status_code=400, detail="Esta solicitud ya fue procesada.")

    asignacion.estado = EstadoNotificacion.RECHAZADO
    db.commit()

    pendientes = contar_pendientes_por_incidente(db, asignacion.incidente_id)
    if pendientes == 0:
        incidente = asignacion.incidente
        categoria_problema = incidente.analisis.categoria_problema if incidente and incidente.analisis else None
        prioridad = incidente.prioridad.value if incidente and hasattr(incidente.prioridad, "value") else incidente.prioridad

        if incidente and categoria_problema:
            # Intentamos el rescate (Radio más amplio, más candidatos)
            nuevos_candidatos = buscar_y_notificar_talleres(
                db=db,
                incidente_id=incidente.id,
                incidente_lat=incidente.latitud,
                incidente_lon=incidente.longitud,
                categoria_problema=categoria_problema,
                prioridad=prioridad,
                limite_candidatos=6,
                distancia_maxima=40.0,
            )

            # SI LA FUNCIÓN DEVUELVE VACÍO: Significa que ya no hay talleres en toda la BD
            # que puedan atender este problema y no hayan rechazado ya.
            if not nuevos_candidatos:
                print(f"ALERTA CRÍTICA: Ningún taller en 40km quiso el incidente {incidente.id}.")

                # Aquí implementas tu Fallback
                # incidente.estado = EstadoIncidente.REQUIERE_ASISTENCIA_MANUAL
                # db.commit()
                # enviar_push_al_cliente(incidente.usuario_id, "Alta demanda. Te llamaremos en 5 minutos.")
        else:
            print(f"ALERTA: Todos los talleres rechazaron el incidente {asignacion.incidente_id}")

    return asignacion


def rechazar_asignacion(db: Session, asignacion_id: int) -> dict:
    """Orquesta el rechazo y arma la respuesta consumible por la API."""
    taller_rechaza_incidente(db=db, asignacion_id=asignacion_id)
    return {
        "estado": "exito",
        "mensaje": "Emergencia rechazada y removida de tu panel.",
    }
