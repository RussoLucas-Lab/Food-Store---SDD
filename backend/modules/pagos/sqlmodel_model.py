"""
Modelo SQLModel para la tabla `pagos`.
"""

from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel


class PagoDB(SQLModel, table=True):
    """Tabla `pagos` en PostgreSQL."""

    __tablename__ = "pagos"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", index=True)
    mp_payment_id: Optional[str] = Field(default=None, max_length=100, index=True)
    mp_status: str = Field(default="pending", max_length=50)
    external_reference: str = Field(unique=True, max_length=100)  # UUID v4
    idempotency_key: str = Field(unique=True, max_length=100)  # UUID v4
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: datetime = Field(default_factory=datetime.utcnow)
