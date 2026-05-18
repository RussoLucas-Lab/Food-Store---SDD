"""
Modelos SQLModel para pedidos: `pedidos`, `detalle_pedido`, `historial_estado_pedido`.
"""

from datetime import datetime
from typing import Optional, List
from sqlmodel import Field, SQLModel, Column
from sqlalchemy import JSON


class PedidoDB(SQLModel, table=True):
    """Tabla `pedidos` en PostgreSQL."""

    __tablename__ = "pedidos"

    id: Optional[int] = Field(default=None, primary_key=True)
    cliente_id: int = Field(foreign_key="clientes.id", index=True)
    estado: str = Field(default="PENDIENTE", max_length=50, index=True)
    direccion_snapshot: str = Field(default="", max_length=2000)  # JSON string inmutable
    total: float = Field(default=0.0, ge=0)
    costo_envio: float = Field(default=0.0, ge=0)
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: datetime = Field(default_factory=datetime.utcnow)


class DetallePedidoDB(SQLModel, table=True):
    """Tabla `detalle_pedido` en PostgreSQL."""

    __tablename__ = "detalle_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", index=True)
    producto_id: int = Field(index=True)
    nombre_snapshot: str = Field(max_length=255)  # snapshot inmutable
    cantidad: int = Field(ge=1)
    precio_snapshot: float = Field(ge=0)  # snapshot inmutable
    personalizacion: Optional[List[int]] = Field(
        default=None, sa_column=Column(JSON)
    )
    creado_en: datetime = Field(default_factory=datetime.utcnow)


class HistorialEstadoPedidoDB(SQLModel, table=True):
    """
    Tabla `historial_estado_pedido` en PostgreSQL.

    APPEND-ONLY: nunca UPDATE ni DELETE sobre esta tabla.
    """

    __tablename__ = "historial_estado_pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    pedido_id: int = Field(foreign_key="pedidos.id", index=True)
    estado_anterior: Optional[str] = Field(default=None, max_length=50)
    estado_nuevo: str = Field(max_length=50)
    usuario_id: Optional[int] = Field(default=None)
    observacion: Optional[str] = Field(default=None, max_length=1000)
    timestamp: datetime = Field(default_factory=datetime.utcnow, index=True)
