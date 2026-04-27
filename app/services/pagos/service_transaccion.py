import stripe
import os
from typing import List

from sqlalchemy.orm import Session

from app.models.pagos.transaccion import EstadoTransaccion, Transaccion, MetodoPago
from app.models.talleres.orden_servicio import EstadoOperacion, OrdenServicio
from app.schemas.pagos.detalle_orden import DetalleOrdenItemEntrada
from app.schemas.pagos.transaccion import TransaccionEntrada
from app.services.pagos import service_detalle_orden


def _mapear_salida(t: Transaccion) -> dict:
    return {
        "id": t.id,
        "monto_cobrado": t.monto_cobrado,
        "monto_comision": t.monto_comision,
        "estado": t.estado,
        "metodo_pago": t.metodo_pago,
        "fecha_hora": t.fecha_hora,
        "orden_servicio_id": t.orden_servicio_id,
    }


def generar_pago(
    db: Session,
    orden_servicio_id: int,
    items: List[DetalleOrdenItemEntrada],
) -> dict:
    detalles, monto_cobrado = service_detalle_orden.crear_lote(db, orden_servicio_id, items)
    monto_comision = round(monto_cobrado * 0.10, 2)
    transaccion = Transaccion(
        monto_cobrado=monto_cobrado,
        monto_comision=monto_comision,
        orden_servicio_id=orden_servicio_id,
    )
    db.add(transaccion)
    orden = db.query(OrdenServicio).filter(OrdenServicio.id == orden_servicio_id).first()
    if orden:
        orden.estado = EstadoOperacion.FINALIZADO
    db.commit()
    db.refresh(transaccion)
    for d in detalles:
        db.refresh(d)
    return {
        "transaccion": _mapear_salida(transaccion),
        "detalles": [service_detalle_orden._mapear_salida(d) for d in detalles],
    }


def crear(db: Session, entrada: TransaccionEntrada) -> dict:
    transaccion = Transaccion(
        monto_cobrado=entrada.monto_cobrado,
        monto_comision=entrada.monto_comision,
        metodo_pago=entrada.metodo_pago,
        orden_servicio_id=entrada.orden_servicio_id,
    )
    db.add(transaccion)
    db.commit()
    db.refresh(transaccion)
    return _mapear_salida(transaccion)


def obtener_por_orden(db: Session, orden_id: int):
    t = db.query(Transaccion).filter(
        Transaccion.orden_servicio_id == orden_id,
        Transaccion.deleted == False,
    ).first()
    if not t:
        return None
    return _mapear_salida(t)


def obtener_por_id(db: Session, transaccion_id: int):
    t = db.query(Transaccion).filter(
        Transaccion.id == transaccion_id,
        Transaccion.deleted == False,
    ).first()
    if not t:
        return None
    return _mapear_salida(t)


def actualizar_estado(db: Session, transaccion_id: int, nuevo_estado: EstadoTransaccion):
    t = db.query(Transaccion).filter(
        Transaccion.id == transaccion_id,
        Transaccion.deleted == False,
    ).first()
    if not t:
        return None
    t.estado = nuevo_estado

    # Si se paga la transacción, finalizamos el incidente atado a la orden de servicio
    if nuevo_estado == EstadoTransaccion.PAGADO and t.orden_servicio and t.orden_servicio.asignacion_candidato and t.orden_servicio.asignacion_candidato.incidente:
        from app.models.emergencias.incidente import EstadoIncidente
        t.orden_servicio.asignacion_candidato.incidente.estado = EstadoIncidente.ATENDIDO

    db.commit()
    db.refresh(t)
    return _mapear_salida(t)

def crear_payment_intent(db: Session, transaccion_id: int) -> dict:
    t = db.query(Transaccion).filter(
        Transaccion.id == transaccion_id,
        Transaccion.deleted == False,
    ).first()
    if not t:
        raise ValueError("Transacción no encontrada")

    if t.estado == EstadoTransaccion.PAGADO:
        raise ValueError("Esta transacción ya fue pagada")

    stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "") # Usa test keys por defecto
    publishable_key = os.getenv("STRIPE_PUBLISHABLE_KEY", "")

    # Stripe cobra en los centavos de la moneda, por lo tanto multiplicamos por 100
    monto_en_centavos = int(t.monto_cobrado * 100)

    try:
        intent = stripe.PaymentIntent.create(
            amount=monto_en_centavos,
            currency="bob", # Boliviano boliviano (código ISO correcto)
        )

        # Actualizamos el método de pago a tarjeta en la base de datos temporalmente
        t.metodo_pago = MetodoPago.TARJETA
        db.commit()

        return {
            "client_secret": intent.client_secret,
            "publishable_key": publishable_key
        }
    except Exception as e:
        db.rollback()
        raise ValueError(f"Error al generar pago en Stripe: {str(e)}")
