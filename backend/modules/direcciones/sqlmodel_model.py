"""
Modelo SQLModel para la tabla `direcciones_entrega`.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class DireccionEntregaDB(SQLModel, table=True):
    """Tabla `direcciones_entrega` en PostgreSQL."""

    __tablename__ = "direcciones_entrega"

    id: Optional[int] = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="clientes.id", index=True)
    calle: str = Field(max_length=255)
    numero: str = Field(max_length=50)
    ciudad: str = Field(max_length=100)
    provincia: str = Field(max_length=100)
    codigo_postal: str = Field(max_length=20)
    piso: Optional[str] = Field(default=None, max_length=20)
    departamento: Optional[str] = Field(default=None, max_length=20)
    referencia: Optional[str] = Field(default=None, max_length=500)
    es_predeterminada: bool = Field(default=False)
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
