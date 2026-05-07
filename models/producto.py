"""
Modelo de Producto para el catálogo de Food Store.

Un Producto representa una unidad de venta con:
- Nombre, descripción y precio base
- Relación many-to-many con Categorías
- Relación many-to-many con Ingredientes (con cantidad requerida)
- Stock derivado transitivamente del stock de sus ingredientes
"""

from datetime import datetime
from typing import List, Optional, Dict


class Product:
    """Modelo de Producto"""
    
    def __init__(
        self,
        id: int,
        nombre: str,
        base_price: float,
        descripcion: str = "",
        status: str = "active",
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None
    ):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.base_price = float(base_price)
        self.status = status  # 'active' o 'inactive'
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.deleted_at = deleted_at
        
        # Relaciones (will be populated by repository)
        self.categories: List[Dict] = []  # [{ id, nombre, ... }]
        self.ingredients: List[Dict] = []  # [{ id, ingredient_id, nombre_ingrediente, quantity_required, stock_disponible }]
    
    def is_active(self) -> bool:
        """Verifica si el producto está activo"""
        return self.status == "active"
    
    def calculate_available_stock(self) -> float:
        """
        Calcula el stock disponible como:
        min(stock_disponible_ingrediente / cantidad_requerida para cada ingrediente)
        
        Retorna 0 si no hay ingredientes.
        """
        if not self.ingredients:
            return 0.0
        
        available_stocks = []
        for ingredient in self.ingredients:
            stock_disp = ingredient.get('stock_disponible', 0)
            qty_required = ingredient.get('quantity_required', 1)
            
            if qty_required > 0:
                available = stock_disp / qty_required
                available_stocks.append(available)
        
        if not available_stocks:
            return 0.0
        
        return min(available_stocks)
    
    def to_dict(self) -> Dict:
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'base_price': self.base_price,
            'status': self.status,
            'categories': self.categories,
            'ingredients': self.ingredients,
            'stock_disponible': self.calculate_available_stock(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
        }


class ProductIngredient:
    """Modelo para la relación muchos-a-muchos Producto <-> Ingrediente con cantidad"""
    
    def __init__(
        self,
        id: int,
        product_id: int,
        ingredient_id: int,
        quantity_required: float,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.product_id = product_id
        self.ingredient_id = ingredient_id
        self.quantity_required = float(quantity_required)
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self) -> Dict:
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'product_id': self.product_id,
            'ingredient_id': self.ingredient_id,
            'quantity_required': self.quantity_required,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
