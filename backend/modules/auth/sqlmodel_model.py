"""
Modelo SQLModel para la tabla `usuarios`.

Coexiste con model.py (modelo de dominio puro usado por tests unitarios).
Esta es la fuente de verdad para la base de datos.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class UsuarioDB(SQLModel, table=True):
    """Tabla `usuarios` en PostgreSQL."""

    __tablename__ = "usuarios"

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True, unique=True, max_length=255)
    password_hash: str = Field(max_length=255)
    nombre: Optional[str] = Field(default=None, max_length=255)
    role: str = Field(default="customer", max_length=50)  # 'admin' | 'customer'
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
