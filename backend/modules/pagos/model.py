"""
Modelo de dominio para Pagos (MercadoPago).

Representa un intento de pago asociado a un pedido.
Implementa idempotencia via external_reference y idempotency_key únicos.
"""

from datetime import datetime
from typing import Optional


class Pago:
    """
    Modelo de Pago asociado a un Pedido.

    Almacena el estado del pago en MercadoPago y los identificadores
    necesarios para idempotencia (external_reference, idempotency_key)
    y para consultas a la API de MP (mp_payment_id).

    Nota: external_reference y idempotency_key son únicos por pago.
    """

    def __init__(
        self,
        pedido_id: int,
        external_reference: str,
        idempotency_key: str,
        mp_payment_id: Optional[str] = None,
        mp_status: str = "pending",
        id: Optional[int] = None,
        creado_en: Optional[datetime] = None,
        actualizado_en: Optional[datetime] = None,
    ):
        self.id = id
        self.pedido_id = pedido_id
        self.mp_payment_id = mp_payment_id
        self.mp_status = mp_status
        self.external_reference = external_reference  # UUID v4, único
        self.idempotency_key = idempotency_key  # UUID v4, único
        self.creado_en = creado_en or datetime.utcnow()
        self.actualizado_en = actualizado_en or datetime.utcnow()

    def to_dict(self) -> dict:
        """Serializa Pago a diccionario serializable."""
        return {
            "id": self.id,
            "pedido_id": self.pedido_id,
            "mp_payment_id": self.mp_payment_id,
            "mp_status": self.mp_status,
            "external_reference": self.external_reference,
            "idempotency_key": self.idempotency_key,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "actualizado_en": self.actualizado_en.isoformat() if self.actualizado_en else None,
        }
