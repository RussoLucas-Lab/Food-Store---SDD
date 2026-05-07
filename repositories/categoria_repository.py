"""
Repository para la entidad Categoría.

Proporciona la interfaz y implementación en memoria para operaciones CRUD de categorías,
siguiendo el patrón Unit of Work + Repository.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from models.categoria import Categoria


class ICategoriaRepository(ABC):
    """Interface para operaciones de Categoría"""
    
    @abstractmethod
    def create(self, nombre: str, descripcion: str = "") -> Categoria:
        """Crear nueva categoría"""
        pass
    
    @abstractmethod
    def find_by_id(self, categoria_id: int) -> Optional[Categoria]:
        """Buscar categoría por id (solo activas)"""
        pass
    
    @abstractmethod
    def find_by_name(self, nombre: str) -> Optional[Categoria]:
        """Buscar categoría por nombre (solo activas)"""
        pass
    
    @abstractmethod
    def list_active(
        self,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "id",
        include_inactive: bool = False
    ) -> List[Categoria]:
        """Listar categorías con opciones de paginación y ordenamiento"""
        pass
    
    @abstractmethod
    def update(self, categoria_id: int, nombre: str = None, descripcion: str = None) -> Optional[Categoria]:
        """Actualizar categoría existente"""
        pass
    
    @abstractmethod
    def soft_delete(self, categoria_id: int) -> bool:
        """Marcar categoría como inactiva (soft delete)"""
        pass
    
    @abstractmethod
    def find_all(self, include_inactive: bool = False) -> List[Categoria]:
        """Obtener todas las categorías (activas o todas)"""
        pass


class InMemoryCategoriaRepository(ICategoriaRepository):
    """Implementación en memoria de CategoriaRepository (para testing/dev)"""
    
    def __init__(self):
        self._storage: dict[int, Categoria] = {}
        self._next_id = 1
        self._name_index: dict[str, int] = {}  # nombre -> categoria_id mapping
    
    def create(self, nombre: str, descripcion: str = "") -> Categoria:
        """Crear nueva categoría"""
        # Validar nombre único (case-insensitive)
        nombre_lower = nombre.lower()
        if nombre_lower in self._name_index:
            raise ValueError(f"Categoría '{nombre}' ya existe")
        
        categoria_id = self._next_id
        self._next_id += 1
        
        categoria = Categoria(
            id=categoria_id,
            nombre=nombre,
            descripcion=descripcion,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self._storage[categoria_id] = categoria
        self._name_index[nombre_lower] = categoria_id
        return categoria
    
    def find_by_id(self, categoria_id: int) -> Optional[Categoria]:
        """Buscar categoría por id (solo activas)"""
        categoria = self._storage.get(categoria_id)
        if categoria and categoria.is_active:
            return categoria
        return None
    
    def find_by_name(self, nombre: str) -> Optional[Categoria]:
        """Buscar categoría por nombre (solo activas)"""
        nombre_lower = nombre.lower()
        categoria_id = self._name_index.get(nombre_lower)
        if categoria_id:
            categoria = self._storage.get(categoria_id)
            if categoria and categoria.is_active:
                return categoria
        return None
    
    def list_active(
        self,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "id",
        include_inactive: bool = False
    ) -> List[Categoria]:
        """Listar categorías con opciones de paginación y ordenamiento"""
        # Filtrar activas o todas
        categorias = [
            c for c in self._storage.values()
            if (include_inactive or c.is_active)
        ]
        
        # Ordenar
        if sort_by == "nombre":
            categorias.sort(key=lambda c: c.nombre.lower())
        elif sort_by == "created_at":
            categorias.sort(key=lambda c: c.created_at, reverse=True)
        else:  # default: id
            categorias.sort(key=lambda c: c.id)
        
        # Paginar
        return categorias[skip:skip + limit]
    
    def update(
        self,
        categoria_id: int,
        nombre: str = None,
        descripcion: str = None
    ) -> Optional[Categoria]:
        """Actualizar categoría existente"""
        categoria = self._storage.get(categoria_id)
        if not categoria:
            return None
        
        # Validar nombre único si se cambia
        if nombre and nombre.lower() != categoria.nombre.lower():
            nombre_lower = nombre.lower()
            if nombre_lower in self._name_index:
                raise ValueError(f"Categoría '{nombre}' ya existe")
            
            # Actualizar índice
            del self._name_index[categoria.nombre.lower()]
            self._name_index[nombre_lower] = categoria_id
            categoria.nombre = nombre
        
        if descripcion is not None:
            categoria.descripcion = descripcion
        
        categoria.updated_at = datetime.utcnow()
        return categoria
    
    def soft_delete(self, categoria_id: int) -> bool:
        """Marcar categoría como inactiva (soft delete) - idempotente"""
        categoria = self._storage.get(categoria_id)
        if not categoria:
            return False
        
        if categoria.is_active:
            categoria.is_active = False
            categoria.deleted_at = datetime.utcnow()
            categoria.updated_at = datetime.utcnow()
        
        return True
    
    def find_all(self, include_inactive: bool = False) -> List[Categoria]:
        """Obtener todas las categorías (activas o todas)"""
        categorias = [
            c for c in self._storage.values()
            if (include_inactive or c.is_active)
        ]
        return sorted(categorias, key=lambda c: c.id)
