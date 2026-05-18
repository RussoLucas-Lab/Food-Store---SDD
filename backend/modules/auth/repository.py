from abc import ABC, abstractmethod
from typing import List, Optional
from .model import Usuario, RoleEnum
from datetime import datetime

class IUsuarioRepository(ABC):
    """Interface para operaciones de Usuario"""

    @abstractmethod
    def create(self, email: str, password_hash: str, role: RoleEnum = RoleEnum.CUSTOMER) -> Usuario:
        """Crear nuevo usuario"""
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[Usuario]:
        """Buscar usuario por email"""
        pass

    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[Usuario]:
        """Buscar usuario por id"""
        pass

    @abstractmethod
    def update(self, user_id: int, **kwargs) -> Optional[Usuario]:
        """Actualizar usuario"""
        pass

    @abstractmethod
    def deactivate(self, user_id: int) -> bool:
        """Desactivar usuario"""
        pass

    @abstractmethod
    def list_all(self, limit: int = 100, offset: int = 0) -> List[Usuario]:
        """Listar todos los usuarios"""
        pass


class InMemoryUsuarioRepository(IUsuarioRepository):
    """Implementación en memoria de UsuarioRepository (para testing/dev)"""

    def __init__(self):
        self._storage: dict[int, Usuario] = {}
        self._next_id = 1
        self._email_index: dict[str, int] = {}  # email -> user_id mapping

    def create(self, email: str, password_hash: str, role: RoleEnum = RoleEnum.CUSTOMER) -> Usuario:
        """Crear nuevo usuario"""
        if email in self._email_index:
            raise ValueError(f"Email {email} ya registrado")

        user_id = self._next_id
        self._next_id += 1

        usuario = Usuario(
            id=user_id,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        self._storage[user_id] = usuario
        self._email_index[email] = user_id
        return usuario

    def find_by_email(self, email: str) -> Optional[Usuario]:
        """Buscar usuario por email"""
        if email not in self._email_index:
            return None
        user_id = self._email_index[email]
        return self._storage.get(user_id)

    def find_by_id(self, user_id: int) -> Optional[Usuario]:
        """Buscar usuario por id"""
        return self._storage.get(user_id)

    def update(self, user_id: int, **kwargs) -> Optional[Usuario]:
        """Actualizar usuario"""
        usuario = self._storage.get(user_id)
        if not usuario:
            return None

        for key, value in kwargs.items():
            if hasattr(usuario, key) and key != "id":
                setattr(usuario, key, value)

        usuario.updated_at = datetime.utcnow()
        return usuario

    def deactivate(self, user_id: int) -> bool:
        """Desactivar usuario"""
        usuario = self._storage.get(user_id)
        if not usuario:
            return False
        usuario.is_active = False
        usuario.updated_at = datetime.utcnow()
        return True

    def list_all(self, limit: int = 100, offset: int = 0) -> List[Usuario]:
        """Listar todos los usuarios con paginación"""
        users = list(self._storage.values())
        return users[offset:offset + limit]
