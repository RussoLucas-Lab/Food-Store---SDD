"""
Repository para la entidad Ingrediente.

Proporciona la interfaz e implementación en memoria para operaciones CRUD de ingredientes,
incluyendo lógica de stock y disponibilidad, siguiendo el patrón Unit of Work + Repository.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from models.ingrediente import Ingrediente, UnidadMedida


class IIngredienteRepository(ABC):
    """Interface para operaciones de Ingrediente"""
    
    @abstractmethod
    def create(
        self,
        nombre: str,
        unidad_medida: str,
        cantidad_stock: int,
        cantidad_minima: int,
        descripcion: str = "",
        categoria_id: Optional[int] = None
    ) -> Ingrediente:
        """Crear nuevo ingrediente"""
        pass
    
    @abstractmethod
    def find_by_id(self, ingrediente_id: int) -> Optional[Ingrediente]:
        """Buscar ingrediente por id (solo activos)"""
        pass
    
    @abstractmethod
    def find_by_name(self, nombre: str) -> Optional[Ingrediente]:
        """Buscar ingrediente por nombre (solo activos)"""
        pass
    
    @abstractmethod
    def list_active(
        self,
        skip: int = 0,
        limit: int = 20,
        categoria_id: Optional[int] = None,
        disponibles_solo: bool = False,
        alerta_stock_bajo: bool = False,
        unidad_medida: Optional[str] = None,
        ordenar_por: str = "id",
        orden: str = "asc"
    ) -> List[Ingrediente]:
        """Listar ingredientes con opciones de paginación, filtros y ordenamiento"""
        pass
    
    @abstractmethod
    def buscar_por_nombre(self, q: str, skip: int = 0, limit: int = 20) -> List[Ingrediente]:
        """Buscar ingredientes por nombre (búsqueda parcial, case-insensitive)"""
        pass
    
    @abstractmethod
    def update(
        self,
        ingrediente_id: int,
        nombre: str = None,
        descripcion: str = None,
        cantidad_stock: int = None,
        cantidad_minima: int = None
    ) -> Optional[Ingrediente]:
        """Actualizar ingrediente existente"""
        pass
    
    @abstractmethod
    def soft_delete(self, ingrediente_id: int) -> bool:
        """Marcar ingrediente como inactivo (soft delete)"""
        pass
    
    @abstractmethod
    def puede_descontar(self, ingrediente_id: int, cantidad: int) -> bool:
        """Verifica si hay stock suficiente para descontar la cantidad"""
        pass
    
    @abstractmethod
    def stock_disponible(self, ingrediente_id: int) -> int:
        """Obtiene el stock disponible (stock - reservadas) de un ingrediente"""
        pass
    
    @abstractmethod
    def find_all(self, include_inactive: bool = False) -> List[Ingrediente]:
        """Obtener todos los ingredientes (activos o todos)"""
        pass


class InMemoryIngredienteRepository(IIngredienteRepository):
    """Implementación en memoria de IngredienteRepository (para testing/dev)"""
    
    def __init__(self):
        self._storage: dict[int, Ingrediente] = {}
        self._next_id = 1
        self._name_index: dict[str, int] = {}  # nombre -> ingrediente_id mapping
    
    def create(
        self,
        nombre: str,
        unidad_medida: str,
        cantidad_stock: int,
        cantidad_minima: int,
        descripcion: str = "",
        categoria_id: Optional[int] = None
    ) -> Ingrediente:
        """Crear nuevo ingrediente"""
        # Validar nombre único (case-insensitive)
        nombre_lower = nombre.lower()
        if nombre_lower in self._name_index:
            raise ValueError(f"Ingrediente '{nombre}' ya existe")
        
        # Validar unidad de medida
        try:
            UnidadMedida(unidad_medida)
        except ValueError:
            raise ValueError(f"Unidad de medida '{unidad_medida}' inválida")
        
        ingrediente_id = self._next_id
        self._next_id += 1
        
        ingrediente = Ingrediente(
            id=ingrediente_id,
            nombre=nombre,
            unidad_medida=unidad_medida,
            cantidad_stock=cantidad_stock,
            cantidad_minima=cantidad_minima,
            descripcion=descripcion,
            categoria_id=categoria_id,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self._storage[ingrediente_id] = ingrediente
        self._name_index[nombre_lower] = ingrediente_id
        return ingrediente
    
    def find_by_id(self, ingrediente_id: int) -> Optional[Ingrediente]:
        """Buscar ingrediente por id (solo activos)"""
        ingrediente = self._storage.get(ingrediente_id)
        if ingrediente and ingrediente.is_active:
            return ingrediente
        return None
    
    def find_by_name(self, nombre: str) -> Optional[Ingrediente]:
        """Buscar ingrediente por nombre (solo activos)"""
        nombre_lower = nombre.lower()
        ingrediente_id = self._name_index.get(nombre_lower)
        if ingrediente_id:
            ingrediente = self._storage.get(ingrediente_id)
            if ingrediente and ingrediente.is_active:
                return ingrediente
        return None
    
    def list_active(
        self,
        skip: int = 0,
        limit: int = 20,
        categoria_id: Optional[int] = None,
        disponibles_solo: bool = False,
        alerta_stock_bajo: bool = False,
        unidad_medida: Optional[str] = None,
        ordenar_por: str = "id",
        orden: str = "asc"
    ) -> List[Ingrediente]:
        """Listar ingredientes con opciones de paginación, filtros y ordenamiento"""
        # Filtrar activos
        ingredientes = [i for i in self._storage.values() if i.is_active]
        
        # Aplicar filtros
        if categoria_id is not None:
            ingredientes = [i for i in ingredientes if i.categoria_id == categoria_id]
        
        if disponibles_solo:
            ingredientes = [i for i in ingredientes if i.stock_disponible > 0]
        
        if alerta_stock_bajo:
            ingredientes = [i for i in ingredientes if i.alerta_stock_bajo]
        
        if unidad_medida:
            ingredientes = [i for i in ingredientes if i.unidad_medida == unidad_medida]
        
        # Ordenar
        reverse = orden.lower() == "desc"
        if ordenar_por == "nombre":
            ingredientes.sort(key=lambda i: i.nombre.lower(), reverse=reverse)
        elif ordenar_por == "cantidad_stock":
            ingredientes.sort(key=lambda i: i.cantidad_stock, reverse=reverse)
        elif ordenar_por == "created_at":
            ingredientes.sort(key=lambda i: i.created_at, reverse=reverse)
        else:  # default: id
            ingredientes.sort(key=lambda i: i.id, reverse=reverse)
        
        # Paginar
        return ingredientes[skip:skip + limit]
    
    def buscar_por_nombre(self, q: str, skip: int = 0, limit: int = 20) -> List[Ingrediente]:
        """Buscar ingredientes por nombre (búsqueda parcial, case-insensitive)"""
        q_lower = q.lower()
        ingredientes = [
            i for i in self._storage.values()
            if i.is_active and q_lower in i.nombre.lower()
        ]
        ingredientes.sort(key=lambda i: i.nombre.lower())
        return ingredientes[skip:skip + limit]
    
    def update(
        self,
        ingrediente_id: int,
        nombre: str = None,
        descripcion: str = None,
        cantidad_stock: int = None,
        cantidad_minima: int = None
    ) -> Optional[Ingrediente]:
        """Actualizar ingrediente existente"""
        ingrediente = self._storage.get(ingrediente_id)
        if not ingrediente:
            return None
        
        # Validar nombre único si se cambia
        if nombre and nombre.lower() != ingrediente.nombre.lower():
            nombre_lower = nombre.lower()
            if nombre_lower in self._name_index:
                raise ValueError(f"Ingrediente '{nombre}' ya existe")
            
            # Actualizar índice
            del self._name_index[ingrediente.nombre.lower()]
            self._name_index[nombre_lower] = ingrediente_id
            ingrediente.nombre = nombre
        
        if descripcion is not None:
            ingrediente.descripcion = descripcion
        
        if cantidad_stock is not None:
            if cantidad_stock < 0:
                raise ValueError("cantidad_stock no puede ser negativa")
            ingrediente.cantidad_stock = cantidad_stock
        
        if cantidad_minima is not None:
            if cantidad_minima < 0:
                raise ValueError("cantidad_minima no puede ser negativa")
            ingrediente.cantidad_minima = cantidad_minima
        
        ingrediente.updated_at = datetime.utcnow()
        return ingrediente
    
    def soft_delete(self, ingrediente_id: int) -> bool:
        """Marcar ingrediente como inactivo (soft delete) - idempotente"""
        ingrediente = self._storage.get(ingrediente_id)
        if not ingrediente:
            return False
        
        if ingrediente.is_active:
            ingrediente.is_active = False
            ingrediente.deleted_at = datetime.utcnow()
            ingrediente.updated_at = datetime.utcnow()
        
        return True
    
    def puede_descontar(self, ingrediente_id: int, cantidad: int) -> bool:
        """Verifica si hay stock suficiente para descontar la cantidad"""
        ingrediente = self._storage.get(ingrediente_id)
        if not ingrediente:
            raise ValueError(f"Ingrediente {ingrediente_id} no existe")
        if not ingrediente.is_active:
            raise ValueError(f"Ingrediente {ingrediente_id} no está activo")
        return ingrediente.puede_descontar(cantidad)
    
    def stock_disponible(self, ingrediente_id: int) -> int:
        """Obtiene el stock disponible (stock - reservadas) de un ingrediente"""
        ingrediente = self._storage.get(ingrediente_id)
        if not ingrediente:
            raise ValueError(f"Ingrediente {ingrediente_id} no existe")
        return ingrediente.stock_disponible
    
    def find_all(self, include_inactive: bool = False) -> List[Ingrediente]:
        """Obtener todos los ingredientes (activos o todos)"""
        ingredientes = [
            i for i in self._storage.values()
            if (include_inactive or i.is_active)
        ]
        return sorted(ingredientes, key=lambda i: i.id)
