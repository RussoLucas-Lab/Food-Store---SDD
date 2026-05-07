"""
Service de lógica de negocio para Productos.

Contiene la lógica de validación, cálculo de stock, validaciones de integridad
y operaciones complejas sobre productos.
"""

from typing import List, Optional, Dict
from models.producto import Product


class ProductService:
    """Servicio de lógica de negocio para productos"""
    
    def __init__(self, uow):
        """
        Inicializar service con Unit of Work.
        
        Args:
            uow: Unit of Work que proporciona acceso a repositorios
        """
        self.uow = uow
    
    def validate_product_input(
        self,
        nombre: str,
        base_price: float,
        descripcion: str = "",
        category_ids: Optional[List[int]] = None,
        ingredients: Optional[List[Dict]] = None
    ) -> Dict[str, bool]:
        """
        Valida un nuevo input de producto.
        
        Valida:
        - nombre: required, no vacío, max 100 chars
        - base_price: required, > 0
        - descripcion: max 500 chars
        - category_ids: array min 1 elemento, todas las categorías existen
        - ingredients: array min 1 elemento, todos los ingredientes existen, quantity > 0
        
        Returns:
            dict con validaciones si todas pasan. Lanza ValueError si alguna falla.
        """
        # Validar nombre
        if not nombre or not nombre.strip():
            raise ValueError("Nombre de producto es requerido")
        if len(nombre) > 100:
            raise ValueError("Nombre máximo 100 caracteres")
        
        # Validar descripción
        if descripcion and len(descripcion) > 500:
            raise ValueError("Descripción máxima 500 caracteres")
        
        # Validar precio
        try:
            price_float = float(base_price)
            if price_float <= 0:
                raise ValueError("Precio debe ser > 0")
        except (ValueError, TypeError):
            raise ValueError("Precio debe ser un número válido > 0")
        
        # Validar categorías
        if not category_ids or len(category_ids) == 0:
            raise ValueError("Al menos una categoría es requerida")
        
        for cat_id in category_ids:
            categoria = self.uow.categorias.find_by_id(cat_id)
            if not categoria:
                raise ValueError(f"Categoría con id {cat_id} no existe")
        
        # Validar ingredientes
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
        """
        Calcula el stock disponible de un producto.
        
        Stock = min(stock_disponible_ingrediente / quantity_required)
        para todos los ingredientes del producto.
        
        Returns:
            Float representando cantidad de unidades del producto disponibles.
            Returns 0.0 si no hay stock suficiente en algún ingrediente.
        """
        product = self.uow.productos.find_by_id(product_id)
        if not product:
            return 0.0
        
        if not product.ingredients:
            return 0.0
        
        available_stocks = []
        
        for ingredient in product.ingredients:
            ing_id = ingredient.get('ingredient_id')
            qty_required = ingredient.get('quantity_required', 1)
            
            ingrediente = self.uow.ingredientes.find_by_id(ing_id)
            if not ingrediente:
                return 0.0
            
            # Obtener stock disponible del ingrediente
            stock_disp = self.uow.ingredientes.stock_disponible(ing_id)
            
            if qty_required > 0:
                available = stock_disp / qty_required
                available_stocks.append(available)
        
        if not available_stocks:
            return 0.0
        
        return float(min(available_stocks))
    
    def check_can_delete_category(self, category_id: int) -> bool:
        """
        Verifica si una categoría puede ser eliminada.
        
        Retorna True si no hay productos activos asignados a esta categoría.
        Lanza ValueError si hay productos.
        """
        # En memoria: búsqueda lineal. En BD: una query a product_categories
        productos = self.uow.productos.find_by_category(category_id)
        active_productos = [p for p in productos if p.is_active()]
        
        if active_productos:
            raise ValueError(f"Categoría está en uso por {len(active_productos)} producto(s) activo(s)")
        
        return True
    
    def check_can_delete_ingredient(self, ingredient_id: int) -> bool:
        """
        Verifica si un ingrediente puede ser eliminado.
        
        Retorna True si no hay productos activos que lo usen.
        Lanza ValueError si hay productos.
        """
        # En memoria: búsqueda lineal. En BD: una query a product_ingredients
        productos = self.uow.productos.find_by_ingredient(ingredient_id)
        active_productos = [p for p in productos if p.is_active()]
        
        if active_productos:
            raise ValueError(f"Ingrediente está en uso por {len(active_productos)} producto(s) activo(s)")
        
        return True
    
    def check_can_modify_product(self, product_id: int) -> bool:
        """
        Verifica si un producto puede ser modificado.
        
        Retorna True si el producto no está en pedidos activos/pagados.
        Lanza ValueError si no puede modificarse.
        """
        # En memoria: siempre permitido. En BD: buscar en orders/order_items
        # Por ahora, siempre retornamos True (la lógica completa está en Change 8)
        return True
    
    def check_products_can_use_ingredient_stock(
        self,
        ingredient_id: int,
        new_stock: float
    ) -> bool:
        """
        Verifica que todos los productos activos que usan este ingrediente
        sigan siendo válidos con el nuevo stock.
        
        Por simplicidad en este change: siempre permitimos cambios de stock
        (la validación de suficiencia sucede en tiempo de lectura del stock del producto).
        """
        return True
