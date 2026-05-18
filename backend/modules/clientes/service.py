"""
Service para operaciones de negocio de Clientes.
"""

from typing import Optional, List, Dict
import re
from backend.core.uow import IUnitOfWork


class ClienteService:
    """
    Servicio de lógica de negocio para Clientes.
    """

    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    @staticmethod
    def _validate_email(email: str) -> None:
        """Validar formato de email"""
        if not email or not email.strip():
            raise ValueError("Email es requerido")

        email = email.strip()
        if len(email) > 254:
            raise ValueError("Email no puede exceder 254 caracteres")

        if not re.match(ClienteService.EMAIL_PATTERN, email):
            raise ValueError("Formato de email inválido")

    @staticmethod
    def _validate_phone(phone: Optional[str]) -> None:
        """Validar formato de teléfono"""
        if phone is None:
            return

        phone = phone.strip()
        if not phone:
            return

        if not re.match(r'^[\d\-\+\s\(\)]{7,20}$', phone):
            raise ValueError("Formato de teléfono inválido")

    @staticmethod
    def _validate_name(nombre: str) -> str:
        """Validar nombre"""
        if not nombre or not nombre.strip():
            raise ValueError("Nombre es requerido")

        nombre = nombre.strip()
        if len(nombre) > 255:
            raise ValueError("Nombre no puede exceder 255 caracteres")

        return nombre

    @staticmethod
    def _validate_address(direccion: str) -> str:
        """Validar dirección"""
        if not direccion or not direccion.strip():
            raise ValueError("Dirección es requerida")

        direccion = direccion.strip()
        if len(direccion) > 500:
            raise ValueError("Dirección no puede exceder 500 caracteres")

        return direccion

    def create_cliente(
        self,
        nombre: str,
        email: str,
        direccion: str,
        telefono: Optional[str] = None,
        user_id: Optional[int] = None,
        requesting_user_role: str = "ADMIN"
    ) -> Dict:
        """Crear nuevo cliente con validaciones."""
        if requesting_user_role != "ADMIN":
            raise PermissionError("Solo ADMIN puede crear clientes")

        nombre = self._validate_name(nombre)
        self._validate_email(email)
        direccion = self._validate_address(direccion)
        self._validate_phone(telefono)

        existing = self.uow.clientes.find_by_email(email)
        if existing:
            raise ValueError(f"Email '{email}' ya está registrado")

        cliente = self.uow.clientes.create(
            nombre=nombre,
            email=email,
            direccion=direccion,
            telefono=telefono,
            user_id=user_id
        )
        self.uow.commit()

        return cliente.to_dict()

    def get_cliente(
        self,
        cliente_id: int,
        requesting_user_id: Optional[int] = None,
        requesting_user_role: str = "ADMIN"
    ) -> Dict:
        """Obtener cliente por ID."""
        if requesting_user_role == "USER" and requesting_user_id and requesting_user_id != cliente_id:
            raise PermissionError("No tienes permiso para acceder a este cliente")

        cliente = self.uow.clientes.find_by_id(cliente_id)
        if not cliente:
            raise ValueError(f"Cliente {cliente_id} no existe")

        return cliente.to_dict()

    def list_clientes(
        self,
        skip: int = 0,
        limit: int = 10,
        requesting_user_id: Optional[int] = None,
        requesting_user_role: str = "ADMIN"
    ) -> List[Dict]:
        """Listar clientes."""
        if requesting_user_role == "USER":
            if requesting_user_id:
                cliente = self.uow.clientes.find_by_id(requesting_user_id)
                return [cliente.to_dict()] if cliente else []
            return []

        clientes = self.uow.clientes.get_all_active(skip=skip, limit=limit, sort_by="created_at")
        return [c.to_dict() for c in clientes]

    def search_clientes(
        self,
        query: str,
        skip: int = 0,
        limit: int = 10,
        requesting_user_role: str = "ADMIN"
    ) -> List[Dict]:
        """Buscar clientes por nombre o email."""
        if requesting_user_role != "ADMIN":
            raise PermissionError("Solo ADMIN puede buscar clientes")

        if not query or not query.strip():
            raise ValueError("Consulta de búsqueda requerida")

        clientes = self.uow.clientes.search(query=query, skip=skip, limit=limit)
        return [c.to_dict() for c in clientes]

    def update_cliente(
        self,
        cliente_id: int,
        nombre: Optional[str] = None,
        email: Optional[str] = None,
        telefono: Optional[str] = None,
        direccion: Optional[str] = None,
        requesting_user_id: Optional[int] = None,
        requesting_user_role: str = "ADMIN"
    ) -> Dict:
        """Actualizar cliente existente."""
        if requesting_user_role == "USER" and requesting_user_id and requesting_user_id != cliente_id:
            raise PermissionError("No tienes permiso para actualizar este cliente")

        cliente = self.uow.clientes.find_by_id(cliente_id)
        if not cliente:
            raise ValueError(f"Cliente {cliente_id} no existe")

        if nombre:
            nombre = self._validate_name(nombre)

        if email:
            self._validate_email(email)
            existing = self.uow.clientes.find_by_email(email)
            if existing and existing.id != cliente_id:
                raise ValueError(f"Email '{email}' ya está registrado")

        if telefono:
            self._validate_phone(telefono)

        if direccion:
            direccion = self._validate_address(direccion)

        cliente = self.uow.clientes.update(
            cliente_id=cliente_id,
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion=direccion
        )
        self.uow.commit()

        return cliente.to_dict()

    def soft_delete_cliente(
        self,
        cliente_id: int,
        requesting_user_role: str = "ADMIN"
    ) -> Dict:
        """Soft-delete de cliente."""
        if requesting_user_role != "ADMIN":
            raise PermissionError("Solo ADMIN puede eliminar clientes")

        cliente = self.uow.clientes.find_by_id(cliente_id)
        if not cliente:
            raise ValueError(f"Cliente {cliente_id} no existe")

        success = self.uow.clientes.soft_delete(cliente_id)
        self.uow.commit()

        return {
            "id": cliente_id,
            "status": "inactivo" if success else "error",
            "message": "Cliente marcado como inactivo" if success else "Error al eliminar cliente"
        }

    def reactivate_cliente(
        self,
        cliente_id: int,
        requesting_user_role: str = "ADMIN"
    ) -> Dict:
        """Reactivar cliente inactivo."""
        if requesting_user_role != "ADMIN":
            raise PermissionError("Solo ADMIN puede reactivar clientes")

        cliente = self.uow.clientes.reactivate(cliente_id)
        if not cliente:
            raise ValueError(f"Cliente {cliente_id} no existe")

        self.uow.commit()

        return cliente.to_dict()
