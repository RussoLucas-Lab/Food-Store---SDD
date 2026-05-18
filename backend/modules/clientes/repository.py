"""
Repository para la entidad Cliente.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from .model import Cliente


class IClienteRepository(ABC):
    """Interface para operaciones de Cliente"""

    @abstractmethod
    def create(self, nombre: str, email: str, direccion: str, telefono: Optional[str] = None, user_id: Optional[int] = None) -> Cliente:
        """Crear nuevo cliente"""
        pass

    @abstractmethod
    def find_by_id(self, cliente_id: int) -> Optional[Cliente]:
        """Buscar cliente por id (solo activos)"""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Cliente]:
        """Buscar cliente por email (solo activos)"""
        pass

    @abstractmethod
    def get_all_active(
        self,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "id"
    ) -> List[Cliente]:
        """Listar clientes activos con paginación"""
        pass

    @abstractmethod
    def search(self, query: str, skip: int = 0, limit: int = 20) -> List[Cliente]:
        """Buscar clientes por nombre o email (solo activos)"""
        pass

    @abstractmethod
    def update(self, cliente_id: int, nombre: str = None, email: str = None,
               telefono: Optional[str] = None, direccion: str = None) -> Optional[Cliente]:
        """Actualizar cliente existente"""
        pass

    @abstractmethod
    def soft_delete(self, cliente_id: int) -> bool:
        """Marcar cliente como inactivo (soft delete)"""
        pass

    @abstractmethod
    def reactivate(self, cliente_id: int) -> Optional[Cliente]:
        """Reactivar cliente inactivo"""
        pass

    @abstractmethod
    def find_all(self, include_inactive: bool = False) -> List[Cliente]:
        """Obtener todos los clientes (activos o todos)"""
        pass


class InMemoryClienteRepository(IClienteRepository):
    """Implementación en memoria de ClienteRepository (para testing/dev)"""

    def __init__(self):
        self._storage: dict[int, Cliente] = {}
        self._next_id = 1
        self._email_index: dict[str, int] = {}  # email -> cliente_id mapping

    def create(self, nombre: str, email: str, direccion: str, telefono: Optional[str] = None, user_id: Optional[int] = None) -> Cliente:
        """Crear nuevo cliente"""
        email_lower = email.lower()
        if email_lower in self._email_index:
            raise ValueError(f"Email '{email}' ya está registrado")

        cliente_id = self._next_id
        self._next_id += 1

        cliente = Cliente(
            id=cliente_id,
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion=direccion,
            activo=True,
            user_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self._storage[cliente_id] = cliente
        self._email_index[email_lower] = cliente_id
        return cliente

    def find_by_id(self, cliente_id: int) -> Optional[Cliente]:
        """Buscar cliente por id (solo activos)"""
        cliente = self._storage.get(cliente_id)
        if cliente and cliente.activo:
            return cliente
        return None

    def find_by_email(self, email: str) -> Optional[Cliente]:
        """Buscar cliente por email (solo activos)"""
        email_lower = email.lower()
        cliente_id = self._email_index.get(email_lower)
        if cliente_id:
            cliente = self._storage.get(cliente_id)
            if cliente and cliente.activo:
                return cliente
        return None

    def get_all_active(
        self,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "id"
    ) -> List[Cliente]:
        """Listar clientes activos con paginación"""
        clientes = [c for c in self._storage.values() if c.activo]

        if sort_by == "nombre":
            clientes.sort(key=lambda c: c.nombre.lower())
        elif sort_by == "created_at":
            clientes.sort(key=lambda c: c.created_at, reverse=True)
        else:
            clientes.sort(key=lambda c: c.id)

        return clientes[skip:skip + limit]

    def search(self, query: str, skip: int = 0, limit: int = 20) -> List[Cliente]:
        """Buscar clientes por nombre o email (solo activos)"""
        query_lower = query.lower()
        clientes = [
            c for c in self._storage.values()
            if c.activo and (query_lower in c.nombre.lower() or query_lower in c.email.lower())
        ]
        return clientes[skip:skip + limit]

    def update(
        self,
        cliente_id: int,
        nombre: str = None,
        email: str = None,
        telefono: Optional[str] = None,
        direccion: str = None
    ) -> Optional[Cliente]:
        """Actualizar cliente existente"""
        cliente = self._storage.get(cliente_id)
        if not cliente:
            return None

        if email and email.lower() != cliente.email.lower():
            email_lower = email.lower()
            if email_lower in self._email_index:
                raise ValueError(f"Email '{email}' ya está registrado")

            del self._email_index[cliente.email.lower()]
            self._email_index[email_lower] = cliente_id
            cliente.email = email

        if nombre:
            cliente.nombre = nombre
        if telefono is not None:
            cliente.telefono = telefono
        if direccion:
            cliente.direccion = direccion

        cliente.updated_at = datetime.utcnow()
        return cliente

    def soft_delete(self, cliente_id: int) -> bool:
        """Marcar cliente como inactivo (soft delete)"""
        cliente = self._storage.get(cliente_id)
        if not cliente:
            return False

        cliente.activo = False
        cliente.updated_at = datetime.utcnow()
        return True

    def reactivate(self, cliente_id: int) -> Optional[Cliente]:
        """Reactivar cliente inactivo"""
        cliente = self._storage.get(cliente_id)
        if not cliente:
            return None

        cliente.activo = True
        cliente.updated_at = datetime.utcnow()
        return cliente

    def find_all(self, include_inactive: bool = False) -> List[Cliente]:
        """Obtener todos los clientes (activos o todos)"""
        clientes = [
            c for c in self._storage.values()
            if (include_inactive or c.activo)
        ]
        clientes.sort(key=lambda c: c.id)
        return clientes
