"""
Repository para la entidad Producto.

Proporciona la interfaz e implementación en memoria para operaciones CRUD de productos,
incluyendo lógica de relaciones con Categorías e Ingredientes, cálculo de stock,
siguiendo el patrón Unit of Work + Repository.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from datetime import datetime
from models.producto import Product, ProductIngredient


class IProductRepository(ABC):
    """Interface para operaciones de Producto"""
    
    @abstractmethod
    def create(
        self,
        nombre: str,
        base_price: float,
        descripcion: str = "",
        category_ids: Optional[List[int]] = None,
        ingredients: Optional[List[Dict]] = None
    ) -> Product:
        """Crear nuevo producto con categorías e ingredientes"""
        pass
    
    @abstractmethod
    def find_by_id(self, product_id: int) -> Optional[Product]:
        """Buscar producto por id (solo activos)"""
        pass
    
    @abstractmethod
    def find_by_name(self, nombre: str) -> Optional[Product]:
        """Buscar producto por nombre (solo activos)"""
        pass
    
    @abstractmethod
    def list_active(
        self,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "id"
    ) -> List[Product]:
        """Listar productos activos con opciones de paginación y filtros"""
        pass
    
    @abstractmethod
    def update(
        self,
        product_id: int,
        nombre: str = None,
        descripcion: str = None,
        base_price: float = None,
        category_ids: Optional[List[int]] = None,
        ingredients: Optional[List[Dict]] = None
    ) -> Optional[Product]:
        """Actualizar producto existente"""
        pass
    
    @abstractmethod
    def soft_delete(self, product_id: int) -> bool:
        """Marcar producto como inactivo (soft delete)"""
        pass
    
    @abstractmethod
    def find_by_category(self, category_id: int) -> List[Product]:
        """Buscar productos activos de una categoría específica"""
        pass
    
    @abstractmethod
    def find_by_ingredient(self, ingredient_id: int) -> List[Product]:
        """Buscar productos activos que usan un ingrediente específico"""
        pass
    
    @abstractmethod
    def is_used_in_orders(self, product_id: int) -> bool:
        """Verifica si el producto está en algún pedido"""
        pass
    
    @abstractmethod
    def find_all(self, include_inactive: bool = False) -> List[Product]:
        """Obtener todos los productos (activos o todos)"""
        pass


class IProductIngredientRepository(ABC):
    """Interface para operaciones de ProductIngredient"""
    
    @abstractmethod
    def create(self, product_id: int, ingredient_id: int, quantity_required: float) -> ProductIngredient:
        """Crear relación producto-ingrediente"""
        pass
    
    @abstractmethod
    def get_by_product(self, product_id: int) -> List[ProductIngredient]:
        """Obtener todos los ingredientes de un producto"""
        pass
    
    @abstractmethod
    def get_by_ingredient(self, ingredient_id: int) -> List[ProductIngredient]:
        """Obtener todos los productos que usan un ingrediente"""
        pass
    
    @abstractmethod
    def delete_by_product(self, product_id: int) -> bool:
        """Eliminar todos los ingredientes de un producto"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[ProductIngredient]:
        """Obtener todas las relaciones"""
        pass


class InMemoryProductRepository(IProductRepository):
    """Implementación en memoria de ProductRepository (para testing/dev)"""
    
    def __init__(self):
        self._storage: Dict[int, Product] = {}
        self._next_id = 1
        self._name_index: Dict[str, int] = {}  # nombre -> product_id mapping
        self._category_index: Dict[int, set] = {}  # category_id -> set de product_ids
        self._ingredient_index: Dict[int, set] = {}  # ingredient_id -> set de product_ids
    
    def create(
        self,
        nombre: str,
        base_price: float,
        descripcion: str = "",
        category_ids: Optional[List[int]] = None,
        ingredients: Optional[List[Dict]] = None
    ) -> Product:
        """Crear nuevo producto"""
        # Validar nombre único (case-insensitive)
        nombre_lower = nombre.lower()
        if nombre_lower in self._name_index:
            raise ValueError(f"Producto '{nombre}' ya existe")
        
        # Validar precio
        if base_price <= 0:
            raise ValueError("Precio debe ser mayor a 0")
        
        product_id = self._next_id
        self._next_id += 1
        
        product = Product(
            id=product_id,
            nombre=nombre,
            base_price=base_price,
            descripcion=descripcion,
            status="active"
        )
        
        self._storage[product_id] = product
        self._name_index[nombre_lower] = product_id
        
        # Aquí en una repo real se agregarían las categorías e ingredientes desde params
        # Por ahora, solo guardamos el producto base
        
        return product
    
    def find_by_id(self, product_id: int) -> Optional[Product]:
        """Buscar producto por id (solo activos)"""
        product = self._storage.get(product_id)
        if product and product.is_active():
            return product
        return None
    
    def find_by_name(self, nombre: str) -> Optional[Product]:
        """Buscar producto por nombre (solo activos)"""
        nombre_lower = nombre.lower()
        product_id = self._name_index.get(nombre_lower)
        if product_id:
            return self.find_by_id(product_id)
        return None
    
    def list_active(
        self,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "id"
    ) -> List[Product]:
        """Listar productos activos"""
        products = [p for p in self._storage.values() if p.is_active()]
        
        # Filtrar por búsqueda
        if search:
            search_lower = search.lower()
            products = [p for p in products if search_lower in p.nombre.lower()]
        
        # Ordenar
        if sort_by == "nombre":
            products.sort(key=lambda p: p.nombre)
        elif sort_by == "base_price":
            products.sort(key=lambda p: p.base_price)
        else:
            products.sort(key=lambda p: p.id)
        
        # Paginar
        return products[skip:skip + limit]
    
    def update(
        self,
        product_id: int,
        nombre: str = None,
        descripcion: str = None,
        base_price: float = None,
        category_ids: Optional[List[int]] = None,
        ingredients: Optional[List[Dict]] = None
    ) -> Optional[Product]:
        """Actualizar producto"""
        product = self._storage.get(product_id)
        if not product or not product.is_active():
            return None
        
        if nombre is not None:
            nombre_lower = nombre.lower()
            if nombre_lower != product.nombre.lower():
                if nombre_lower in self._name_index:
                    raise ValueError(f"Producto '{nombre}' ya existe")
                del self._name_index[product.nombre.lower()]
                self._name_index[nombre_lower] = product_id
            product.nombre = nombre
        
        if descripcion is not None:
            product.descripcion = descripcion
        
        if base_price is not None:
            if base_price <= 0:
                raise ValueError("Precio debe ser mayor a 0")
            product.base_price = base_price
        
        product.updated_at = datetime.now()
        return product
    
    def soft_delete(self, product_id: int) -> bool:
        """Marcar como inactivo"""
        product = self._storage.get(product_id)
        if not product:
            return False
        
        product.status = "inactive"
        product.deleted_at = datetime.now()
        return True
    
    def find_by_category(self, category_id: int) -> List[Product]:
        """Buscar productos de una categoría (mock, no implementado en memoria)"""
        # En una repo real, buscaría en la tabla product_categories
        return []
    
    def find_by_ingredient(self, ingredient_id: int) -> List[Product]:
        """Buscar productos que usan un ingrediente (mock)"""
        # En una repo real, buscaría en la tabla product_ingredients
        return []
    
    def is_used_in_orders(self, product_id: int) -> bool:
        """Verifica si está en pedidos (mock)"""
        # En una repo real, verificaría si existe en tabla orders/order_items
        return False
    
    def find_all(self, include_inactive: bool = False) -> List[Product]:
        """Obtener todos los productos"""
        if include_inactive:
            return list(self._storage.values())
        return [p for p in self._storage.values() if p.is_active()]


class InMemoryProductIngredientRepository(IProductIngredientRepository):
    """Implementación en memoria de ProductIngredientRepository"""
    
    def __init__(self):
        self._storage: Dict[int, ProductIngredient] = {}
        self._next_id = 1
        self._product_index: Dict[int, List[int]] = {}  # product_id -> [pi_ids]
        self._ingredient_index: Dict[int, List[int]] = {}  # ingredient_id -> [pi_ids]
    
    def create(self, product_id: int, ingredient_id: int, quantity_required: float) -> ProductIngredient:
        """Crear relación"""
        if quantity_required <= 0:
            raise ValueError("Cantidad requerida debe ser mayor a 0")
        
        pi_id = self._next_id
        self._next_id += 1
        
        pi = ProductIngredient(
            id=pi_id,
            product_id=product_id,
            ingredient_id=ingredient_id,
            quantity_required=quantity_required
        )
        
        self._storage[pi_id] = pi
        
        if product_id not in self._product_index:
            self._product_index[product_id] = []
        self._product_index[product_id].append(pi_id)
        
        if ingredient_id not in self._ingredient_index:
            self._ingredient_index[ingredient_id] = []
        self._ingredient_index[ingredient_id].append(pi_id)
        
        return pi
    
    def get_by_product(self, product_id: int) -> List[ProductIngredient]:
        """Obtener ingredientes de un producto"""
        pi_ids = self._product_index.get(product_id, [])
        return [self._storage[pi_id] for pi_id in pi_ids if pi_id in self._storage]
    
    def get_by_ingredient(self, ingredient_id: int) -> List[ProductIngredient]:
        """Obtener productos que usan un ingrediente"""
        pi_ids = self._ingredient_index.get(ingredient_id, [])
        return [self._storage[pi_id] for pi_id in pi_ids if pi_id in self._storage]
    
    def delete_by_product(self, product_id: int) -> bool:
        """Eliminar todos los ingredientes de un producto"""
        pi_ids = self._product_index.get(product_id, [])
        for pi_id in pi_ids:
            if pi_id in self._storage:
                del self._storage[pi_id]
        self._product_index[product_id] = []
        return True
    
    def find_all(self) -> List[ProductIngredient]:
        """Obtener todas las relaciones"""
        return list(self._storage.values())
