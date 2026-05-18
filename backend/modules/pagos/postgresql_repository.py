"""
Implementación PostgreSQL de IPagoRepository usando SQLModel Session.
"""

from typing import Optional
from datetime import datetime
from sqlmodel import Session, select

from .repository import IPagoRepository
from .model import Pago
from .sqlmodel_model import PagoDB


def _to_domain(db_obj: PagoDB) -> Pago:
    """Convertir PagoDB → Pago (dominio)."""
    return Pago(
        id=db_obj.id,
        pedido_id=db_obj.pedido_id,
        mp_payment_id=db_obj.mp_payment_id,
        mp_status=db_obj.mp_status,
        external_reference=db_obj.external_reference,
        idempotency_key=db_obj.idempotency_key,
        creado_en=db_obj.creado_en,
        actualizado_en=db_obj.actualizado_en,
    )


class PostgreSQLPagoRepository(IPagoRepository):
    """Implementación PostgreSQL de IPagoRepository."""

    def __init__(self, session: Session):
        self._session = session

    def create(self, pago: Pago) -> Pago:
        """Crear un nuevo pago."""
        now = datetime.utcnow()
        db_obj = PagoDB(
            pedido_id=pago.pedido_id,
            mp_payment_id=pago.mp_payment_id,
            mp_status=pago.mp_status,
            external_reference=pago.external_reference,
            idempotency_key=pago.idempotency_key,
            creado_en=pago.creado_en or now,
            actualizado_en=pago.actualizado_en or now,
        )
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        result = _to_domain(db_obj)
        pago.id = result.id
        return result

    def get_by_id(self, pago_id: int) -> Optional[Pago]:
        """Obtener pago por ID."""
        db_obj = self._session.get(PagoDB, pago_id)
        return _to_domain(db_obj) if db_obj else None

    def get_by_pedido_id(self, pedido_id: int) -> Optional[Pago]:
        """Obtener pago por ID de pedido (uno a uno)."""
        db_obj = self._session.exec(
            select(PagoDB).where(PagoDB.pedido_id == pedido_id)
        ).first()
        return _to_domain(db_obj) if db_obj else None

    def get_by_mp_payment_id(self, mp_payment_id: str) -> Optional[Pago]:
        """Obtener pago por ID de MercadoPago."""
        db_obj = self._session.exec(
            select(PagoDB).where(PagoDB.mp_payment_id == mp_payment_id)
        ).first()
        return _to_domain(db_obj) if db_obj else None

    def get_by_idempotency_key(self, key: str) -> Optional[Pago]:
        """Obtener pago por clave de idempotencia."""
        db_obj = self._session.exec(
            select(PagoDB).where(PagoDB.idempotency_key == key)
        ).first()
        return _to_domain(db_obj) if db_obj else None

    def update_status(
        self,
        pago_id: int,
        mp_status: str,
        mp_payment_id: Optional[str] = None,
    ) -> Optional[Pago]:
        """Actualizar estado del pago."""
        db_obj = self._session.get(PagoDB, pago_id)
        if not db_obj:
            return None
        db_obj.mp_status = mp_status
        if mp_payment_id is not None:
            db_obj.mp_payment_id = mp_payment_id
        db_obj.actualizado_en = datetime.utcnow()
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        return _to_domain(db_obj)
