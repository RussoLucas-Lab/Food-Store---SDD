"""
Modelo SQLModel para la tabla `ingredientes`.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class IngredienteDB(SQLModel, table=True):
    """Tabla `ingredientes` en PostgreSQL."""

    __tablename__ = "ingredientes"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True, max_length=255)
    descripcion: str = Field(default="", max_length=1000)
    unidad_medida: str = Field(max_length=50)  # gramos, litros, unidades, kilos, mililitros
    cantidad_stock: int = Field(default=0, ge=0)
    cantidad_minima: int = Field(default=0, ge=0)
    cantidad_reservada: int = Field(default=0, ge=0)
    categoria_id: Optional[int] = Field(default=None, foreign_key="categorias.id")
    es_alergeno: bool = Field(default=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)
