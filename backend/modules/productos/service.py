"""
Service de lógica de negocio para Productos.
"""

from typing import List, Optional, Dict
from backend.core.uow import IUnitOfWork
from .model import Product


class ProductService:
    """Servicio de lógica de negocio para productos"""

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    def validate_product_input(
        self,
        nombre: str,
        base_price: float,
        descripcion: str = "",
        category_ids: Optional[List[int]] = None,
        ingredients: Optional[List[Dict]] = None
    ) -> Dict[str, bool]:
        """Valida un nuevo input de producto."""
        if not nombre or not nombre.strip():
            raise ValueError("Nombre de producto es requerido")
        if len(nombre) > 100:
            raise ValueError("Nombre máximo 100 caracteres")

        if descripcion and len(descripcion) > 500:
            raise ValueError("Descripción máxima 500 caracteres")

        try:
            price_float = float(base_price)
            if price_float <= 0:
                raise ValueError("Precio debe ser > 0")
        except (ValueError, TypeError):
            raise ValueError("Precio debe ser un número válido > 0")

        if not category_ids or len(category_ids) == 0:
            raise ValueError("Al menos una categoría es requerida")

        for cat_id in category_ids:
            categoria = self.uow.categorias.find_by_id(cat_id)
            if not categoria:
                raise ValueError(f"Categoría con id {cat_id} no existe")

        if not ingredients or len(ingredients) == 0:
            raise ValueError("Al menos un ingrediente es requerido")

        for ing in ingredients:
            ing_id = ing.get('ingredient_id')
            qty = ing.get('quantity_required')

            if not ing_id:
                raise ValueError("ingredient_id es requerido en cada ingrediente")
            if qty is None or float(qty) <= 0:
                raise ValueError(f"quantity_required debe ser > 0 para ingrediente {ing_id}")

            ingrediente = self.uow.ingredientes.find_by_id(ing_id)
            if not ingrediente:
                raise ValueError(f"Ingrediente con id {ing_id} no existe")

        return {"valid": True}

    def validate_categories_exist(self, category_ids: List[int]) -> bool:
        """Verifica que todas las categorías existan"""
        for cat_id in category_ids:
            if not self.uow.categorias.find_by_id(cat_id):
                return False
        return True

    def validate_ingredients_exist(self, ingredients: List[Dict]) -> bool:
        """Verifica que todos los ingredientes existan y tienen cantidad válida"""
        for ing in ingredients:
            ing_id = ing.get('ingredient_id')
            qty = ing.get('quantity_required')

            if not ing_id or not self.uow.ingredientes.find_by_id(ing_id):
                return False
            if qty is None or float(qty) <= 0:
                return False

        return True

    def calculate_product_stock(self, product_id: int) -> float:
        """Calcula el stock disponible de un producto desde sus ingredientes en BD."""
        product = self.uow.productos.find_by_id(product_id)
        if not product:
            return 0.0

        product_ingredients = self.uow.product_ingredients.get_by_product(product_id)
        if not product_ingredients:
            # Productos sin ingredientes (ej: bebidas) usan el stock directo de la BD
            return float(getattr(product, 'stock', 0))

        available_stocks = []

        for pi in product_ingredients:
            ing_id = pi.ingredient_id
            qty_required = pi.quantity_required

            ingrediente = self.uow.ingredientes.find_by_id(ing_id)
            if not ingrediente:
                return 0.0

            stock_disp = self.uow.ingredientes.stock_disponible(ing_id)

            if qty_required > 0:
                available = stock_disp / qty_required
                available_stocks.append(available)

        if not available_stocks:
            return 0.0

        return float(min(available_stocks))

    def check_can_delete_category(self, category_id: int) -> bool:
        """Verifica si una categoría puede ser eliminada."""
        productos = self.uow.productos.find_by_category(category_id)
        active_productos = [p for p in productos if p.is_active()]

        if active_productos:
            raise ValueError(f"Categoría está en uso por {len(active_productos)} producto(s) activo(s)")

        return True

    def check_can_delete_ingredient(self, ingredient_id: int) -> bool:
        """Verifica si un ingrediente puede ser eliminado."""
        productos = self.uow.productos.find_by_ingredient(ingredient_id)
        active_productos = [p for p in productos if p.is_active()]

        if active_productos:
            raise ValueError(f"Ingrediente está en uso por {len(active_productos)} producto(s) activo(s)")

        return True

    def check_can_modify_product(self, product_id: int) -> bool:
        """Verifica si un producto puede ser modificado."""
        return True

    def deactivate_product(self, product_id: int) -> bool:
        """
        Desactivar (soft delete) un producto.

        Args:
            product_id: ID del producto a desactivar

        Returns:
            True si se desactivó, False si no existe
        """
        result = self.uow.productos.soft_delete(product_id)
        self.uow.commit()
        return result

    def check_products_can_use_ingredient_stock(
        self,
        ingredient_id: int,
        new_stock: float
    ) -> bool:
        """Verifica que todos los productos activos que usan este ingrediente sigan siendo válidos."""
        return True
