from sqlalchemy.orm import Session

from app.models.pagos.transaccion import EstadoTransaccion, Transaccion
from app.schemas.pagos.transaccion import TransaccionEntrada


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
    db.commit()
    db.refresh(t)
    return _mapear_salida(t)
