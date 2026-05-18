"""
Repositorios in-memory para Pagos.

Implementa:
- IPagoRepository: Protocol/interfaz para repositorio de pagos
- InMemoryPagoRepository: Implementación in-memory para testing y desarrollo
"""

from typing import Optional, Dict
from datetime import datetime
from .model import Pago


class IPagoRepository:
    """
    Interfaz del repositorio de Pagos.

    Define las operaciones mínimas necesarias para gestionar pagos.
    Usar como contrato para mocks en tests.
    """

    def create(self, pago: Pago) -> Pago:
        raise NotImplementedError

    def get_by_id(self, pago_id: int) -> Optional[Pago]:
        raise NotImplementedError

    def get_by_pedido_id(self, pedido_id: int) -> Optional[Pago]:
        """Obtener pago por ID de pedido (uno a uno)."""
        raise NotImplementedError

    def get_by_mp_payment_id(self, mp_payment_id: str) -> Optional[Pago]:
        """Obtener pago por ID de pago de MercadoPago."""
        raise NotImplementedError

    def get_by_idempotency_key(self, key: str) -> Optional[Pago]:
        """Obtener pago por clave de idempotencia."""
        raise NotImplementedError

    def update_status(self, pago_id: int, mp_status: str, mp_payment_id: Optional[str] = None) -> Optional[Pago]:
        """Actualizar el estado de un pago y opcionalmente su mp_payment_id."""
        raise NotImplementedError


class InMemoryPagoRepository(IPagoRepository):
    """
    Repositorio in-memory para operaciones sobre Pagos.
    Consistente con el patrón InMemoryXRepository del proyecto.
    """

    def __init__(self):
        self._storage: Dict[int, Pago] = {}
        self._next_id = 1

    def create(self, pago: Pago) -> Pago:
        """Crear un nuevo pago asignando ID autoincremental."""
        pago.id = self._next_id
        self._next_id += 1
        self._storage[pago.id] = pago
        return pago

    def get_by_id(self, pago_id: int) -> Optional[Pago]:
        """Obtener pago por ID."""
        return self._storage.get(pago_id)

    def get_by_pedido_id(self, pedido_id: int) -> Optional[Pago]:
        """Obtener pago por ID de pedido (retorna el primero encontrado)."""
        for pago in self._storage.values():
            if pago.pedido_id == pedido_id:
                return pago
        return None

    def get_by_mp_payment_id(self, mp_payment_id: str) -> Optional[Pago]:
        """Obtener pago por mp_payment_id (ID de MercadoPago)."""
        for pago in self._storage.values():
            if pago.mp_payment_id == mp_payment_id:
                return pago
        return None

    def get_by_idempotency_key(self, key: str) -> Optional[Pago]:
        """Obtener pago por clave de idempotencia."""
        for pago in self._storage.values():
            if pago.idempotency_key == key:
                return pago
        return None

    def update_status(self, pago_id: int, mp_status: str, mp_payment_id: Optional[str] = None) -> Optional[Pago]:
        """Actualizar estado del pago y opcionalmente su mp_payment_id."""
        pago = self._storage.get(pago_id)
        if pago:
            pago.mp_status = mp_status
            if mp_payment_id is not None:
                pago.mp_payment_id = mp_payment_id
            pago.actualizado_en = datetime.utcnow()
        return pago
