"""
Service para operaciones de negocio de Categorías.

Proporciona una capa de servicios que encapsula toda la lógica de validación
y coordina el acceso a repositorios a través del Unit of Work.

Lanza excepciones de negocio (ValueError) que los routers mapean a HTTP.
"""

from typing import Optional, List, Dict
from uow.interfaces import IUnitOfWork


class CategoryService:
    """
    Servicio de lógica de negocio para Categorías.
    
    Responsabilidades:
    - Validación de datos de entrada
    - Coordinación de repositorios a través del UoW
    - Garantizar integridad de negocio (ej: nombre único, no eliminar si está en uso)
    - Lanzar ValueError con mensajes específicos para que routers mapeen a HTTP
    """
    
    def __init__(self, uow: IUnitOfWork):
        """
        Inicializar servicio.
        
        Args:
            uow: Unit of Work para acceso a repositorios
        """
        self.uow = uow
    
    def create_categoria(self, nombre: str, descripcion: str = "") -> Dict:
        """
        Crear nueva categoría con validaciones.
        
        Args:
            nombre: Nombre de la categoría (1-100 chars, requerido)
            descripcion: Descripción opcional (0-500 chars)
            
        Returns:
            Dict con datos de la categoría creada (id, nombre, descripcion, status, timestamps)
            
        Raises:
            ValueError: Si nombre vacío (→ 400), nombre duplicado (→ 409), 
                       descripción excede 500 chars (→ 400)
        """
        # Validar nombre no vacío
        if not nombre or not nombre.strip():
            raise ValueError("Nombre requerido")
        
        nombre = nombre.strip()
        
        # Validar longitud de nombre
        if len(nombre) > 100:
            raise ValueError("Nombre no puede exceder 100 caracteres")
        
        # Validar longitud de descripción
        if descripcion and len(descripcion) > 500:
            raise ValueError("Descripción no puede exceder 500 caracteres")
        
        # Validar nombre único (case-insensitive)
        existing = self.uow.categorias.find_by_name(nombre)
        if existing:
            raise ValueError(f"Categoría '{nombre}' ya existe")
        
        # Crear categoría
        categoria = self.uow.categorias.create(nombre, descripcion or "")
        self.uow.commit()
        
        return categoria.to_dict()
    
    def update_categoria(self, id: int, nombre: str, descripcion: str = "") -> Dict:
        """
        Actualizar categoría existente.
        
        Args:
            id: ID de la categoría a actualizar
            nombre: Nuevo nombre (requerido)
            descripcion: Nueva descripción
            
        Returns:
            Dict con datos actualizados
            
        Raises:
            ValueError: Si ID no existe (→ 404), nombre vacío (→ 400),
                       nombre duplicado en otra categoría (→ 409),
                       descripción > 500 chars (→ 400)
        """
        # Validar nombre no vacío
        if not nombre or not nombre.strip():
            raise ValueError("Nombre requerido")
        
        nombre = nombre.strip()
        
        # Validar longitud de nombre
        if len(nombre) > 100:
            raise ValueError("Nombre no puede exceder 100 caracteres")
        
        # Validar longitud de descripción
        if descripcion and len(descripcion) > 500:
            raise ValueError("Descripción no puede exceder 500 caracteres")
        
        # Verificar que categoría existe
        categoria = self.uow.categorias.find_by_id(id)
        if not categoria:
            raise ValueError(f"Categoría {id} no existe")
        
        # Validar nombre único (excepto self)
        existing = self.uow.categorias.find_by_name(nombre)
        if existing and existing.id != id:
            raise ValueError(f"Nombre '{nombre}' ya está en uso")
        
        # Actualizar
        categoria = self.uow.categorias.update(
            categoria_id=id,
            nombre=nombre,
            descripcion=descripcion or ""
        )
        self.uow.commit()
        
        return categoria.to_dict()
    
    def delete_categoria(self, id: int) -> Dict:
        """
        Soft-delete de categoría (marcar como inactiva).
        
        Valida que no esté siendo usada por productos activos.
        
        Args:
            id: ID de la categoría a eliminar
            
        Returns:
            Dict con datos de categoría eliminada (status='inactive')
            
        Raises:
            ValueError: Si ID no existe (→ 404),
                       está en uso por productos activos (→ 409)
        """
        # Verificar que categoría existe
        categoria = self.uow.categorias.find_by_id(id)
        if not categoria:
            raise ValueError(f"Categoría {id} no existe")
        
        # Verificar que no está en uso por productos activos
        products_using = self.uow.productos.count_by_category(id)
        if products_using > 0:
            raise ValueError(f"Categoría '{categoria.nombre}' está en uso por {products_using} productos activos")
        
        # Soft-delete
        self.uow.categorias.soft_delete(id)
        self.uow.commit()
        
        # Retornar el objeto como inactivo
        return {
            "id": id,
            "nombre": categoria.nombre,
            "descripcion": getattr(categoria, "descripcion", ""),
            "status": "inactive",
            "created_at": getattr(categoria, "created_at", None),
            "updated_at": getattr(categoria, "updated_at", None)
        }
    
    def get_categoria(self, id: int) -> Dict:
        """
        Obtener categoría por ID.
        
        Args:
            id: ID de la categoría
            
        Returns:
            Dict con datos de categoría
            
        Raises:
            ValueError: Si ID no existe (→ 404)
        """
        categoria = self.uow.categorias.find_by_id(id)
        if not categoria:
            raise ValueError(f"Categoría {id} no existe")
        
        return categoria.to_dict()
    
    def list_categorias(
        self, 
        skip: int = 0, 
        limit: int = 10, 
        search: Optional[str] = None
    ) -> List[Dict]:
        """
        Listar categorías con paginación y búsqueda opcional.
        
        Args:
            skip: Cantidad de registros a saltar (paginación)
            limit: Límite de registros por página
            search: Texto para buscar en nombre/descripción (case-insensitive)
            
        Returns:
            Lista de dicts con categorías
        """
        categorias = self.uow.categorias.list_active(skip=skip, limit=limit)
        
        # Convertir a dicts
        return [cat.to_dict() for cat in categorias]
