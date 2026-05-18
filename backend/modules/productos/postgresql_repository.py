"""
Implementaciones PostgreSQL de IProductRepository e IProductIngredientRepository.
"""

from typing import List, Optional, Dict
from datetime import datetime
from sqlmodel import Session, select

from .repository import IProductRepository, IProductIngredientRepository
from .model import Product, ProductIngredient
from .sqlmodel_model import ProductoDB, ProductoCategoriaDB, ProductoIngredienteDB


def _to_domain(db_obj: ProductoDB) -> Product:
    """Convertir ProductoDB → Product (dominio)."""
    product = Product(
        id=db_obj.id,
        nombre=db_obj.nombre,
        base_price=db_obj.base_price,
        descripcion=db_obj.descripcion,
        status=db_obj.status,
        created_at=db_obj.created_at,
        updated_at=db_obj.updated_at,
        deleted_at=db_obj.deleted_at,
    )
    # Exponer stock como atributo para compatibilidad
    product.stock = db_obj.stock
    return product


def _to_pi_domain(db_obj: ProductoIngredienteDB) -> ProductIngredient:
    """Convertir ProductoIngredienteDB → ProductIngredient (dominio)."""
    return ProductIngredient(
        id=db_obj.id,
        product_id=db_obj.product_id,
        ingredient_id=db_obj.ingredient_id,
        quantity_required=db_obj.quantity_required,
        created_at=db_obj.created_at,
        updated_at=db_obj.updated_at,
    )


class PostgreSQLProductRepository(IProductRepository):
    """Implementación PostgreSQL de IProductRepository."""

    def __init__(self, session: Session):
        self._session = session

    def create(
        self,
        nombre: str,
        base_price: float,
        descripcion: str = "",
        category_ids: Optional[List[int]] = None,
        ingredients: Optional[List[Dict]] = None,
    ) -> Product:
        """Crear nuevo producto con categorías e ingredientes."""
        existing = self._session.exec(
            select(ProductoDB).where(ProductoDB.nombre == nombre)
        ).first()
        if existing:
            raise ValueError(f"Producto '{nombre}' ya existe")

        if base_price <= 0:
            raise ValueError("Precio debe ser mayor a 0")

        now = datetime.utcnow()
        db_obj = ProductoDB(
            nombre=nombre,
            base_price=base_price,
            descripcion=descripcion,
            status="active",
            stock=0,
            created_at=now,
            updated_at=now,
        )
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)

        # Crear relaciones con categorías
        if category_ids:
            for cat_id in category_ids:
                if cat_id is not None:
                    rel = ProductoCategoriaDB(
                        producto_id=db_obj.id,
                        categoria_id=cat_id,
                    )
                    self._session.add(rel)

        # Crear relaciones con ingredientes
        if ingredients:
            for ing in ingredients:
                ing_id = ing.get("ingredient_id")
                qty = ing.get("quantity_required", 1)
                if ing_id is not None:
                    rel = ProductoIngredienteDB(
                        product_id=db_obj.id,
                        ingredient_id=ing_id,
                        quantity_required=qty,
                        created_at=now,
                        updated_at=now,
                    )
                    self._session.add(rel)

        self._session.flush()
        return _to_domain(db_obj)

    def find_by_id(self, product_id: int) -> Optional[Product]:
        """Buscar producto por id (solo activos)."""
        db_obj = self._session.exec(
            select(ProductoDB).where(
                ProductoDB.id == product_id,
                ProductoDB.status == "active",
            )
        ).first()
        return _to_domain(db_obj) if db_obj else None

    def find_by_name(self, nombre: str) -> Optional[Product]:
        """Buscar producto por nombre (solo activos)."""
        db_obj = self._session.exec(
            select(ProductoDB).where(
                ProductoDB.nombre == nombre,
                ProductoDB.status == "active",
            )
        ).first()
        return _to_domain(db_obj) if db_obj else None

    def list_active(
        self,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[int] = None,
        search: Optional[str] = None,
        sort_by: str = "id",
    ) -> List[Product]:
        """Listar productos activos con paginación y filtros."""
        stmt = select(ProductoDB).where(ProductoDB.status == "active")

        if search:
            stmt = stmt.where(ProductoDB.nombre.ilike(f"%{search}%"))

        if category_id is not None:
            # Join con producto_categoria para filtrar por categoría
            stmt = stmt.join(
                ProductoCategoriaDB,
                ProductoDB.id == ProductoCategoriaDB.producto_id,
            ).where(ProductoCategoriaDB.categoria_id == category_id)

        if sort_by == "nombre":
            stmt = stmt.order_by(ProductoDB.nombre)
        elif sort_by == "base_price":
            stmt = stmt.order_by(ProductoDB.base_price)
        else:
            stmt = stmt.order_by(ProductoDB.id)

        stmt = stmt.offset(skip).limit(limit)
        db_objs = self._session.exec(stmt).all()
        return [_to_domain(obj) for obj in db_objs]

    def update(
        self,
        product_id: int,
        nombre: str = None,
        descripcion: str = None,
        base_price: float = None,
        category_ids: Optional[List[int]] = None,
        ingredients: Optional[List[Dict]] = None,
    ) -> Optional[Product]:
        """Actualizar producto existente."""
        db_obj = self._session.exec(
            select(ProductoDB).where(
                ProductoDB.id == product_id,
                ProductoDB.status == "active",
            )
        ).first()
        if not db_obj:
            return None

        if nombre is not None and nombre != db_obj.nombre:
            conflict = self._session.exec(
                select(ProductoDB).where(ProductoDB.nombre == nombre)
            ).first()
            if conflict:
                raise ValueError(f"Producto '{nombre}' ya existe")
            db_obj.nombre = nombre

        if descripcion is not None:
            db_obj.descripcion = descripcion

        if base_price is not None:
            if base_price <= 0:
                raise ValueError("Precio debe ser mayor a 0")
            db_obj.base_price = base_price

        # Actualizar categorías si se proporcionan
        if category_ids is not None:
            existing_cats = self._session.exec(
                select(ProductoCategoriaDB).where(ProductoCategoriaDB.producto_id == product_id)
            ).all()
            for cat_rel in existing_cats:
                self._session.delete(cat_rel)
            for cat_id in category_ids:
                if cat_id is not None:
                    self._session.add(ProductoCategoriaDB(producto_id=product_id, categoria_id=cat_id))

        # Actualizar ingredientes si se proporcionan
        if ingredients is not None:
            existing_ings = self._session.exec(
                select(ProductoIngredienteDB).where(ProductoIngredienteDB.product_id == product_id)
            ).all()
            for ing_rel in existing_ings:
                self._session.delete(ing_rel)
            now_ts = datetime.utcnow()
            for ing in ingredients:
                ing_id = ing.get('ingredient_id') if isinstance(ing, dict) else getattr(ing, 'ingredient_id', None)
                qty = ing.get('quantity_required', 1.0) if isinstance(ing, dict) else getattr(ing, 'quantity_required', 1.0)
                if ing_id is not None:
                    self._session.add(ProductoIngredienteDB(
                        product_id=product_id, ingredient_id=ing_id,
                        quantity_required=float(qty), created_at=now_ts, updated_at=now_ts,
                    ))

        db_obj.updated_at = datetime.utcnow()
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        return _to_domain(db_obj)

    def get_categories_for_product(self, product_id: int) -> List[Dict]:
        """Obtener categorías de un producto como lista de dicts."""
        from backend.modules.categorias.sqlmodel_model import CategoriDB
        cat_rels = self._session.exec(
            select(ProductoCategoriaDB).where(ProductoCategoriaDB.producto_id == product_id)
        ).all()
        categories = []
        for rel in cat_rels:
            cat = self._session.get(CategoriDB, rel.categoria_id)
            if cat:
                categories.append({'id': cat.id, 'nombre': cat.nombre, 'descripcion': cat.descripcion})
        return categories

    def update_stock(self, product_id: int, stock: int) -> bool:
        """Actualizar stock manual de un producto."""
        db_obj = self._session.get(ProductoDB, product_id)
        if not db_obj:
            return False
        db_obj.stock = stock
        db_obj.updated_at = datetime.utcnow()
        self._session.add(db_obj)
        self._session.flush()
        return True

    def soft_delete(self, product_id: int) -> bool:
        """Marcar producto como inactivo."""
        db_obj = self._session.get(ProductoDB, product_id)
        if not db_obj:
            return False
        db_obj.status = "inactive"
        db_obj.deleted_at = datetime.utcnow()
        self._session.add(db_obj)
        self._session.flush()
        return True

    def find_by_category(self, category_id: int) -> List[Product]:
        """Buscar productos activos de una categoría."""
        stmt = (
            select(ProductoDB)
            .join(ProductoCategoriaDB, ProductoDB.id == ProductoCategoriaDB.producto_id)
            .where(
                ProductoCategoriaDB.categoria_id == category_id,
                ProductoDB.status == "active",
            )
        )
        db_objs = self._session.exec(stmt).all()
        return [_to_domain(obj) for obj in db_objs]

    def find_by_ingredient(self, ingredient_id: int) -> List[Product]:
        """Buscar productos activos que usan un ingrediente."""
        stmt = (
            select(ProductoDB)
            .join(ProductoIngredienteDB, ProductoDB.id == ProductoIngredienteDB.product_id)
            .where(
                ProductoIngredienteDB.ingredient_id == ingredient_id,
                ProductoDB.status == "active",
            )
        )
        db_objs = self._session.exec(stmt).all()
        return [_to_domain(obj) for obj in db_objs]

    def is_used_in_orders(self, product_id: int) -> bool:
        """Verifica si el producto está en algún pedido (siempre False si no hay pedidos)."""
        from backend.modules.pedidos.sqlmodel_model import DetallePedidoDB
        result = self._session.exec(
            select(DetallePedidoDB).where(DetallePedidoDB.producto_id == product_id)
        ).first()
        return result is not None

    def find_all(self, include_inactive: bool = False) -> List[Product]:
        """Obtener todos los productos."""
        stmt = select(ProductoDB).order_by(ProductoDB.id)
        if not include_inactive:
            stmt = stmt.where(ProductoDB.status == "active")
        db_objs = self._session.exec(stmt).all()
        return [_to_domain(obj) for obj in db_objs]

    def count_by_category(self, category_id: int) -> int:
        """Contar productos activos de una categoría."""
        return len(self.find_by_category(category_id))

    def count_by_ingredient(self, ingredient_id: int) -> int:
        """Contar productos activos que usan un ingrediente."""
        return len(self.find_by_ingredient(ingredient_id))

    def restore_stock(self, producto_id: int, cantidad: int) -> bool:
        """Restaurar stock de un producto tras cancelación."""
        db_obj = self._session.get(ProductoDB, producto_id)
        if not db_obj:
            return False
        db_obj.stock = (db_obj.stock or 0) + cantidad
        self._session.add(db_obj)
        self._session.flush()
        return True


class PostgreSQLProductIngredientRepository(IProductIngredientRepository):
    """Implementación PostgreSQL de IProductIngredientRepository."""

    def __init__(self, session: Session):
        self._session = session

    def create(self, product_id: int, ingredient_id: int, quantity_required: float) -> ProductIngredient:
        """Crear relación producto-ingrediente."""
        if quantity_required <= 0:
            raise ValueError("Cantidad requerida debe ser mayor a 0")

        now = datetime.utcnow()
        db_obj = ProductoIngredienteDB(
            product_id=product_id,
            ingredient_id=ingredient_id,
            quantity_required=quantity_required,
            created_at=now,
            updated_at=now,
        )
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        return _to_pi_domain(db_obj)

    def get_by_product(self, product_id: int) -> List[ProductIngredient]:
        """Obtener todos los ingredientes de un producto."""
        db_objs = self._session.exec(
            select(ProductoIngredienteDB).where(
                ProductoIngredienteDB.product_id == product_id
            )
        ).all()
        return [_to_pi_domain(obj) for obj in db_objs]

    def get_by_ingredient(self, ingredient_id: int) -> List[ProductIngredient]:
        """Obtener todos los productos que usan un ingrediente."""
        db_objs = self._session.exec(
            select(ProductoIngredienteDB).where(
                ProductoIngredienteDB.ingredient_id == ingredient_id
            )
        ).all()
        return [_to_pi_domain(obj) for obj in db_objs]

    def delete_by_product(self, product_id: int) -> bool:
        """Eliminar todos los ingredientes de un producto."""
        db_objs = self._session.exec(
            select(ProductoIngredienteDB).where(
                ProductoIngredienteDB.product_id == product_id
            )
        ).all()
        for obj in db_objs:
            self._session.delete(obj)
        self._session.flush()
        return True

    def find_all(self) -> List[ProductIngredient]:
        """Obtener todas las relaciones."""
        db_objs = self._session.exec(select(ProductoIngredienteDB)).all()
        return [_to_pi_domain(obj) for obj in db_objs]
