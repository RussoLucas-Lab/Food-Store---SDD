"""
Repository para la entidad DireccionEntrega.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from .model import DireccionEntrega


class IDireccionRepository(ABC):
    """Interface abstracta para operaciones de DireccionEntrega."""

    @abstractmethod
    def create(self, cliente_id: int, calle: str, numero: str, ciudad: str,
               provincia: str, codigo_postal: str,
               piso: Optional[str] = None, departamento: Optional[str] = None,
               referencia: Optional[str] = None,
               es_predeterminada: bool = False) -> DireccionEntrega:
        """Crear nueva dirección con id autoincremental."""
        pass

    @abstractmethod
    def get_by_id(self, direccion_id: int) -> Optional[DireccionEntrega]:
        """Buscar dirección por id (solo activas)."""
        pass

    @abstractmethod
    def list_by_cliente(self, cliente_id: int) -> List[DireccionEntrega]:
        """Listar direcciones activas de un cliente."""
        pass

    @abstractmethod
    def update(self, direccion_id: int, **campos) -> Optional[DireccionEntrega]:
        """Actualizar campos de una dirección existente."""
        pass

    @abstractmethod
    def soft_delete(self, direccion_id: int) -> bool:
        """Marcar dirección como inactiva (soft delete)."""
        pass

    @abstractmethod
    def count_by_cliente(self, cliente_id: int) -> int:
        """Contar direcciones activas de un cliente (para RN-DI01)."""
        pass

    @abstractmethod
    def set_predeterminada(self, direccion_id: int) -> Optional[DireccionEntrega]:
        """
        Marcar una dirección como predeterminada y desmarcar el resto del mismo cliente.

        Mantiene la invariante RN-DI02: solo una predeterminada por cliente.
        """
        pass


class InMemoryDireccionRepository(IDireccionRepository):
    """Implementación en memoria de IDireccionRepository (para testing/dev)."""

    def __init__(self):
        self._storage: dict[int, DireccionEntrega] = {}
        self._next_id: int = 1

    def create(self, cliente_id: int, calle: str, numero: str, ciudad: str,
               provincia: str, codigo_postal: str,
               piso: Optional[str] = None, departamento: Optional[str] = None,
               referencia: Optional[str] = None,
               es_predeterminada: bool = False) -> DireccionEntrega:
        """Crear nueva dirección con id autoincremental."""
        direccion_id = self._next_id
        self._next_id += 1

        direccion = DireccionEntrega(
            id=direccion_id,
            cliente_id=cliente_id,
            calle=calle,
            numero=numero,
            ciudad=ciudad,
            provincia=provincia,
            codigo_postal=codigo_postal,
            piso=piso,
            departamento=departamento,
            referencia=referencia,
            es_predeterminada=es_predeterminada,
            activo=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        self._storage[direccion_id] = direccion
        return direccion

    def get_by_id(self, direccion_id: int) -> Optional[DireccionEntrega]:
        """Buscar dirección por id (solo activas)."""
        direccion = self._storage.get(direccion_id)
        if direccion and direccion.activo:
            return direccion
        return None

    def list_by_cliente(self, cliente_id: int) -> List[DireccionEntrega]:
        """Listar direcciones activas de un cliente, ordenadas por id."""
        return [
            d for d in self._storage.values()
            if d.cliente_id == cliente_id and d.activo
        ]

    def update(self, direccion_id: int, **campos) -> Optional[DireccionEntrega]:
        """Actualizar campos de una dirección existente."""
        direccion = self._storage.get(direccion_id)
        if not direccion:
            return None

        allowed_fields = {
            "calle", "numero", "ciudad", "provincia", "codigo_postal",
            "piso", "departamento", "referencia", "es_predeterminada",
        }
        for key, value in campos.items():
            if key in allowed_fields:
                setattr(direccion, key, value)

        direccion.updated_at = datetime.utcnow()
        return direccion

    def soft_delete(self, direccion_id: int) -> bool:
        """Marcar dirección como inactiva (soft delete)."""
        direccion = self._storage.get(direccion_id)
        if not direccion:
            return False
        direccion.activo = False
        direccion.updated_at = datetime.utcnow()
        return True

    def count_by_cliente(self, cliente_id: int) -> int:
        """Contar direcciones activas de un cliente."""
        return sum(
            1 for d in self._storage.values()
            if d.cliente_id == cliente_id and d.activo
        )

    def set_predeterminada(self, direccion_id: int) -> Optional[DireccionEntrega]:
        """
        Marcar una dirección como predeterminada y desmarcar el resto del mismo cliente.

        Garantiza la invariante RN-DI02 a nivel de repositorio.
        """
        target = self._storage.get(direccion_id)
        if not target or not target.activo:
            return None

        # Desmarcar todas las demás del mismo cliente
        for d in self._storage.values():
            if d.cliente_id == target.cliente_id and d.id != direccion_id:
                d.es_predeterminada = False
                d.updated_at = datetime.utcnow()

        target.es_predeterminada = True
        target.updated_at = datetime.utcnow()
        return target
