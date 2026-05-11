"""
Service para operaciones de negocio de Ingredientes.

Proporciona una capa de servicios que encapsula toda la lógica de validación,
coordina repositorios a través del Unit of Work, y gestiona el historial de stock.

Lanza excepciones de negocio (ValueError) que los routers mapean a HTTP.
"""

from typing import Optional, List, Dict
from uow.interfaces import IUnitOfWork

# Unidades de medida válidas
VALID_UNITS = {"gramos", "litros", "unidades", "kilos", "mililitros"}


class IngredientService:
    """
    Servicio de lógica de negocio para Ingredientes.
    
    Responsabilidades:
    - Validación de datos (nombre, unidad, stock, etc.)
    - Coordinación de repositorios a través del UoW
    - Garantizar integridad (nombre único, no eliminar si está en uso, stock no negativo)
    - Gestión de historial de stock
    - Lanzar ValueError con mensajes específicos para que routers mapeen a HTTP
    """
    
    def __init__(self, uow: IUnitOfWork):
        """
        Inicializar servicio.
        
        Args:
            uow: Unit of Work para acceso a repositorios
        """
        self.uow = uow
    
    def create_ingrediente(
        self,
        nombre: str,
        unidad_medida: str,
        cantidad_stock: float,
        cantidad_minima: float,
        descripcion: str = "",
        categoria_id: Optional[int] = None
    ) -> Dict:
        """
        Crear nuevo ingrediente con validaciones.
        
        Args:
            nombre: Nombre del ingrediente (1-100 chars, requerido)
            unidad_medida: Uno de {gramos, litros, unidades, kilos, mililitros}
            cantidad_stock: Stock inicial (>= 0)
            cantidad_minima: Cantidad mínima para alerta (>= 0)
            descripcion: Descripción opcional (0-500 chars)
            categoria_id: ID de categoría opcional (FK)
            
        Returns:
            Dict con datos del ingrediente creado
            
        Raises:
            ValueError: Si validación falla (mapea a 400, 409)
        """
        # Validar nombre no vacío
        if not nombre or not nombre.strip():
            raise ValueError("Nombre requerido")
        
        nombre = nombre.strip()
        
        # Validar longitud de nombre
        if len(nombre) > 100:
            raise ValueError("Nombre no puede exceder 100 caracteres")
        
        # Validar unidad de medida
        if not unidad_medida or unidad_medida.lower() not in VALID_UNITS:
            raise ValueError(f"Unidad medida debe ser: {', '.join(VALID_UNITS)}")
        
        # Validar stock no negativo
        if cantidad_stock < 0:
            raise ValueError("Stock no puede ser negativo")
        
        # Validar cantidad mínima no negativa
        if cantidad_minima < 0:
            raise ValueError("Cantidad mínima no puede ser negativa")
        
        # Validar descripción
        if descripcion and len(descripcion) > 500:
            raise ValueError("Descripción no puede exceder 500 caracteres")
        
        # Validar nombre único (case-insensitive)
        existing = self.uow.ingredientes.find_by_name(nombre)
        if existing:
            raise ValueError(f"Ingrediente '{nombre}' ya existe")
        
        # Crear ingrediente
        ingrediente = self.uow.ingredientes.create(
            nombre=nombre,
            unidad_medida=unidad_medida.lower(),
            cantidad_stock=cantidad_stock,
            cantidad_minima=cantidad_minima,
            descripcion=descripcion or "",
            categoria_id=categoria_id
        )
        self.uow.commit()
        
        return ingrediente.to_dict()
    
    def update_ingrediente(
        self,
        id: int,
        nombre: Optional[str] = None,
        unidad_medida: Optional[str] = None,
        cantidad_stock: Optional[float] = None,
        cantidad_minima: Optional[float] = None,
        descripcion: Optional[str] = None,
        categoria_id: Optional[int] = None
    ) -> Dict:
        """
        Actualizar ingrediente existente.
        
        Args:
            id: ID del ingrediente
            nombre: Nuevo nombre (opcional)
            unidad_medida: Nueva unidad (opcional)
            cantidad_stock: Nuevo stock (optional)
            cantidad_minima: Nueva cantidad mínima (optional)
            descripcion: Nueva descripción (optional)
            categoria_id: Nueva categoría (optional)
            
        Returns:
            Dict con datos actualizados
            
        Raises:
            ValueError: Si validación falla
        """
        # Verificar que existe
        ingrediente = self.uow.ingredientes.find_by_id(id)
        if not ingrediente:
            raise ValueError(f"Ingrediente {id} no existe")
        
        # Validar nombre si se proporciona
        if nombre is not None:
            nombre = nombre.strip()
            if not nombre:
                raise ValueError("Nombre requerido")
            if len(nombre) > 100:
                raise ValueError("Nombre no puede exceder 100 caracteres")
            
            # Validar nombre único (excepto self)
            existing = self.uow.ingredientes.find_by_name(nombre)
            if existing and existing.id != id:
                raise ValueError(f"Nombre ya está en uso")
            
            ingrediente.nombre = nombre
        
        # Validar unidad si se proporciona
        if unidad_medida is not None:
            if unidad_medida.lower() not in VALID_UNITS:
                raise ValueError(f"Unidad medida debe ser: {', '.join(VALID_UNITS)}")
            ingrediente.unidad_medida = unidad_medida.lower()
        
        # Validar stock si se proporciona
        if cantidad_stock is not None:
            if cantidad_stock < 0:
                raise ValueError("Stock no puede ser negativo")
            ingrediente.cantidad_stock = cantidad_stock
        
        # Validar cantidad mínima si se proporciona
        if cantidad_minima is not None:
            if cantidad_minima < 0:
                raise ValueError("Cantidad mínima no puede ser negativa")
            ingrediente.cantidad_minima = cantidad_minima
        
        # Validar descripción si se proporciona
        if descripcion is not None:
            if len(descripcion) > 500:
                raise ValueError("Descripción no puede exceder 500 caracteres")
            ingrediente.descripcion = descripcion
        
        # Actualizar categoría si se proporciona
        if categoria_id is not None:
            ingrediente.categoria_id = categoria_id
        
        self.uow.ingredientes.update(ingrediente)
        self.uow.commit()
        
        return ingrediente.to_dict()
    
    def delete_ingrediente(self, id: int) -> Dict:
        """
        Soft-delete de ingrediente (marcar como inactivo).
        
        Valida que no esté siendo usado por productos activos.
        
        Args:
            id: ID del ingrediente
            
        Returns:
            Dict con datos de ingrediente eliminado (status='inactive')
            
        Raises:
            ValueError: Si ID no existe (→ 404),
                       está en uso por productos activos (→ 409)
        """
        # Verificar que existe
        ingrediente = self.uow.ingredientes.find_by_id(id)
        if not ingrediente:
            raise ValueError(f"Ingrediente {id} no existe")
        
        # Verificar que no está en uso por productos activos
        products_using = self.uow.productos.count_by_ingredient(id)
        if products_using > 0:
            raise ValueError(f"Ingrediente '{ingrediente.nombre}' está en uso por {products_using} productos activos")
        
        # Soft-delete
        ingrediente.status = "inactive"
        self.uow.ingredientes.update(ingrediente)
        self.uow.commit()
        
        return ingrediente.to_dict()
    
    def get_ingrediente(self, id: int) -> Dict:
        """
        Obtener ingrediente por ID.
        
        Args:
            id: ID del ingrediente
            
        Returns:
            Dict con datos del ingrediente
            
        Raises:
            ValueError: Si ID no existe (→ 404)
        """
        ingrediente = self.uow.ingredientes.find_by_id(id)
        if not ingrediente:
            raise ValueError(f"Ingrediente {id} no existe")
        
        return ingrediente.to_dict()
    
    def list_ingredientes(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        unidad_medida: Optional[str] = None,
        categoria_id: Optional[int] = None
    ) -> List[Dict]:
        """
        Listar ingredientes con paginación y filtros opcionales.
        
        Args:
            skip: Cantidad de registros a saltar
            limit: Límite de registros por página
            search: Texto para buscar en nombre/descripción (case-insensitive)
            unidad_medida: Filtrar por unidad de medida (opcional)
            categoria_id: Filtrar por categoría (opcional)
            
        Returns:
            Lista de dicts con ingredientes
        """
        ingredientes = self.uow.ingredientes.list_active(
            skip=skip,
            limit=limit,
            unidad_medida=unidad_medida,
            categoria_id=categoria_id
        )
        
        # Convertir a dicts
        return [ing.to_dict() for ing in ingredientes]
    
    def get_stock_history(self, id: int) -> List[Dict]:
        """
        Obtener historial de cambios de stock para un ingrediente.
        
        Args:
            id: ID del ingrediente
            
        Returns:
            Lista de dicts con cambios de stock (ordenados por fecha DESC)
            
        Raises:
            ValueError: Si ID no existe (→ 404)
        """
        # Verificar que existe
        ingrediente = self.uow.ingredientes.find_by_id(id)
        if not ingrediente:
            raise ValueError(f"Ingrediente {id} no existe")
        
        # Si existe repositorio de historial, usarlo. Por ahora retornamos []
        # En una implementación real, esto consultaría una tabla de historial
        history = self.uow.ingredientes.get_stock_history(id)
        return history if history else []
