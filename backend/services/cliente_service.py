"""
Service para operaciones de negocio de Clientes.

Proporciona una capa de servicios que encapsula toda la lógica de validación,
control de acceso basado en roles y coordina el acceso a repositorios a través del UoW.

Lanza excepciones de negocio (ValueError) que los routers mapean a HTTP.
"""

from typing import Optional, List, Dict
import re
from uow.interfaces import IUnitOfWork


class ClienteService:
    """
    Servicio de lógica de negocio para Clientes.
    
    Responsabilidades:
    - Validación de datos de entrada (email, campos requeridos, formato)
    - Control de acceso basado en roles (ADMIN/USER)
    - Coordinación de repositorios a través del UoW
    - Garantizar integridad de negocio (ej: email único)
    - Lanzar ValueError con mensajes específicos para que routers mapeen a HTTP
    """
    
    # Patrón para validar email
    EMAIL_PATTERN = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def __init__(self, uow: IUnitOfWork):
        """
        Inicializar servicio.
        
        Args:
            uow: Unit of Work para acceso a repositorios
        """
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
        """Validar formato de teléfono (opcional pero si existe debe ser válido)"""
        if phone is None:
            return
        
        phone = phone.strip()
        if not phone:
            return
        
        # Teléfono debe ser numérico o contener solo números y caracteres permitidos
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
        """
        Crear nuevo cliente con validaciones.
        
        Args:
            nombre: Nombre del cliente (1-255 chars, requerido)
            email: Email del cliente (requerido, único)
            direccion: Dirección del cliente (requerido)
            telefono: Teléfono opcional
            user_id: User ID asociado (opcional)
            requesting_user_role: Rol del usuario que hace la solicitud (ADMIN/USER)
            
        Returns:
            Dict con datos del cliente creado
            
        Raises:
            ValueError: Si validación falla o si USER intenta crear cliente
        """
        # Control de acceso: solo ADMIN puede crear clientes
        if requesting_user_role != "ADMIN":
            raise PermissionError("Solo ADMIN puede crear clientes")
        
        # Validar datos
        nombre = self._validate_name(nombre)
        self._validate_email(email)
        direccion = self._validate_address(direccion)
        self._validate_phone(telefono)
        
        # Validar email único
        existing = self.uow.clientes.find_by_email(email)
        if existing:
            raise ValueError(f"Email '{email}' ya está registrado")
        
        # Crear cliente
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
        """
        Obtener cliente por ID.
        
        Control de acceso:
        - ADMIN: puede obtener cualquier cliente
        - USER: solo puede obtener su propio cliente
        
        Args:
            cliente_id: ID del cliente
            requesting_user_id: ID del usuario que hace la solicitud
            requesting_user_role: Rol del usuario
            
        Returns:
            Dict con datos del cliente
            
        Raises:
            ValueError: Si cliente no existe (→ 404)
            PermissionError: Si USER intenta acceder a otro cliente (→ 403)
        """
        # Control de acceso
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
        """
        Listar clientes.
        
        Control de acceso:
        - ADMIN: ve todos los clientes activos
        - USER: solo ve su propio cliente (se retorna en lista de 1)
        
        Args:
            skip: Cantidad de registros a saltar
            limit: Límite de registros por página
            requesting_user_id: ID del usuario que hace la solicitud
            requesting_user_role: Rol del usuario
            
        Returns:
            Lista de dicts con clientes
        """
        if requesting_user_role == "USER":
            # USER solo ve su propio cliente
            if requesting_user_id:
                cliente = self.uow.clientes.find_by_id(requesting_user_id)
                return [cliente.to_dict()] if cliente else []
            return []
        
        # ADMIN ve todos
        clientes = self.uow.clientes.get_all_active(skip=skip, limit=limit, sort_by="created_at")
        return [c.to_dict() for c in clientes]
    
    def search_clientes(
        self,
        query: str,
        skip: int = 0,
        limit: int = 10,
        requesting_user_role: str = "ADMIN"
    ) -> List[Dict]:
        """
        Buscar clientes por nombre o email.
        
        Solo ADMIN puede buscar.
        
        Args:
            query: Texto a buscar
            skip: Paginación
            limit: Límite de resultados
            requesting_user_role: Rol del usuario
            
        Returns:
            Lista de clientes que coinciden
            
        Raises:
            PermissionError: Si no es ADMIN
        """
        # Control de acceso
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
        """
        Actualizar cliente existente.
        
        Control de acceso:
        - ADMIN: puede actualizar cualquier cliente
        - USER: solo puede actualizar su propio cliente
        
        Args:
            cliente_id: ID del cliente a actualizar
            nombre: Nuevo nombre (opcional)
            email: Nuevo email (opcional, debe ser único)
            telefono: Nuevo teléfono (opcional)
            direccion: Nueva dirección (opcional)
            requesting_user_id: ID del usuario que hace la solicitud
            requesting_user_role: Rol del usuario
            
        Returns:
            Dict con datos actualizados
            
        Raises:
            ValueError: Si cliente no existe o validaciones fallan
            PermissionError: Si USER intenta actualizar otro cliente
        """
        # Control de acceso
        if requesting_user_role == "USER" and requesting_user_id and requesting_user_id != cliente_id:
            raise PermissionError("No tienes permiso para actualizar este cliente")
        
        # Verificar que cliente existe
        cliente = self.uow.clientes.find_by_id(cliente_id)
        if not cliente:
            raise ValueError(f"Cliente {cliente_id} no existe")
        
        # Validar datos si se proporcionan
        if nombre:
            nombre = self._validate_name(nombre)
        
        if email:
            self._validate_email(email)
            # Validar email único (excepto self)
            existing = self.uow.clientes.find_by_email(email)
            if existing and existing.id != cliente_id:
                raise ValueError(f"Email '{email}' ya está registrado")
        
        if telefono:
            self._validate_phone(telefono)
        
        if direccion:
            direccion = self._validate_address(direccion)
        
        # Actualizar
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
        """
        Soft-delete de cliente (marcar como inactivo).
        
        Solo ADMIN puede eliminar.
        
        Args:
            cliente_id: ID del cliente a eliminar
            requesting_user_role: Rol del usuario
            
        Returns:
            Dict con estado de eliminación
            
        Raises:
            ValueError: Si cliente no existe
            PermissionError: Si no es ADMIN
        """
        # Control de acceso
        if requesting_user_role != "ADMIN":
            raise PermissionError("Solo ADMIN puede eliminar clientes")
        
        # Verificar que cliente existe
        cliente = self.uow.clientes.find_by_id(cliente_id)
        if not cliente:
            raise ValueError(f"Cliente {cliente_id} no existe")
        
        # Soft-delete
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
        """
        Reactivar cliente inactivo.
        
        Solo ADMIN puede reactivar.
        
        Args:
            cliente_id: ID del cliente a reactivar
            requesting_user_role: Rol del usuario
            
        Returns:
            Dict con datos del cliente reactivado
            
        Raises:
            ValueError: Si cliente no existe
            PermissionError: Si no es ADMIN
        """
        # Control de acceso
        if requesting_user_role != "ADMIN":
            raise PermissionError("Solo ADMIN puede reactivar clientes")
        
        cliente = self.uow.clientes.reactivate(cliente_id)
        if not cliente:
            raise ValueError(f"Cliente {cliente_id} no existe")
        
        self.uow.commit()
        
        return cliente.to_dict()
