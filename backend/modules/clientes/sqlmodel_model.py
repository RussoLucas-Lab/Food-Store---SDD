"""
Modelo SQLModel para la tabla `clientes`.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class ClienteDB(SQLModel, table=True):
    """Tabla `clientes` en PostgreSQL."""

    __tablename__ = "clientes"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=255)
    email: str = Field(index=True, unique=True, max_length=255)
    telefono: Optional[str] = Field(default=None, max_length=50)
    direccion: str = Field(max_length=500)
    activo: bool = Field(default=True)
    user_id: Optional[int] = Field(default=None, foreign_key="usuarios.id", index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
