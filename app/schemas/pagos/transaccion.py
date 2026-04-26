from datetime import datetime

from pydantic import BaseModel

from app.models.pagos.transaccion import EstadoTransaccion, MetodoPago


class TransaccionEntrada(BaseModel):
    monto_cobrado: float
    monto_comision: float
    metodo_pago: MetodoPago
    orden_servicio_id: int


class ActualizarEstadoEntrada(BaseModel):
    estado: EstadoTransaccion


class TransaccionSalida(BaseModel):
    id: int
    monto_cobrado: float
    monto_comision: float
    estado: EstadoTransaccion
    metodo_pago: MetodoPago
    fecha_hora: datetime
    orden_servicio_id: int
