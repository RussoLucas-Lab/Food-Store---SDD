"""
Modelos SQLModel para las tablas `productos` y `producto_categoria` (M2M).
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class ProductoDB(SQLModel, table=True):
    """Tabla `productos` en PostgreSQL."""

    __tablename__ = "productos"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True, max_length=255)
    descripcion: str = Field(default="", max_length=1000)
    base_price: float = Field(gt=0)
    status: str = Field(default="active", max_length=50)  # 'active' | 'inactive'
    stock: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)


class ProductoCategoriaDB(SQLModel, table=True):
    """Tabla M2M `producto_categoria`."""

    __tablename__ = "producto_categoria"

    id: Optional[int] = Field(default=None, primary_key=True)
    producto_id: int = Field(foreign_key="productos.id", index=True)
    categoria_id: int = Field(foreign_key="categorias.id", index=True)


class ProductoIngredienteDB(SQLModel, table=True):
    """Tabla M2M `producto_ingrediente` con cantidad requerida."""

    __tablename__ = "producto_ingrediente"

    id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="productos.id", index=True)
    ingredient_id: int = Field(foreign_key="ingredientes.id", index=True)
    quantity_required: float = Field(gt=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
