"""
Modelo SQLModel para la tabla `categorias`.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class CategoriDB(SQLModel, table=True):
    """Tabla `categorias` en PostgreSQL."""

    __tablename__ = "categorias"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, unique=True, max_length=255)
    descripcion: str = Field(default="", max_length=1000)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)
