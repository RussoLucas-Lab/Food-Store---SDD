"""
Pydantic schemas para Pedidos (órdenes).

Schemas de request (DTO) y response para la API de pedidos.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class PersonalizacionDTO(BaseModel):
    """DTO para personalización de un ítem del carrito (ingredientes excluidos)."""
    excluidos: List[int] = Field(default_factory=list, description="IDs de ingredientes excluidos")

    class Config:
        schema_extra = {
            "example": {"excluidos": [5, 7]}
        }


class CartItemDTO(BaseModel):
    """DTO para un ítem en el carrito."""
    producto_id: int = Field(..., description="ID del producto")
    cantidad: int = Field(..., gt=0, description="Cantidad (debe ser > 0)")
    personalizacion: PersonalizacionDTO = Field(
        default_factory=PersonalizacionDTO,
        description="Personalización (ingredientes excluidos)"
    )

    class Config:
        schema_extra = {
            "example": {
                "producto_id": 1,
                "cantidad": 2,
                "personalizacion": {"excluidos": [5, 7]}
            }
        }


class CartCreateDTO(BaseModel):
    """DTO para crear un pedido desde el carrito."""
    items: List[CartItemDTO] = Field(..., min_items=1, description="Items del carrito (mín 1)")
    direccion_id: int = Field(..., description="ID de la dirección de entrega")

    @validator('items')
    def validate_items(cls, v):
        if not v:
            raise ValueError('El carrito no puede estar vacío')
        return v

    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {"producto_id": 1, "cantidad": 2, "personalizacion": {"excluidos": []}},
                    {"producto_id": 3, "cantidad": 1, "personalizacion": {"excluidos": [5]}}
                ],
                "direccion_id": 10
            }
        }


class DetallePedidoResponse(BaseModel):
    """DTO para respuesta de un detalle de pedido."""
    id: int
    producto_id: int
    nombre_snapshot: str = Field(..., description="Nombre del producto al momento de la compra")
    cantidad: int
    precio_snapshot: float = Field(..., description="Precio al momento de la compra")
    personalizacion: List[int] = Field(default_factory=list, description="IDs de ingredientes excluidos")
    creado_en: datetime

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "producto_id": 5,
                "nombre_snapshot": "Pizza Margherita",
                "cantidad": 2,
                "precio_snapshot": 150.00,
                "personalizacion": [7],
                "creado_en": "2026-05-13T10:30:00"
            }
        }


class HistorialEstadoPedidoResponse(BaseModel):
    """DTO para respuesta de un registro de historial de estado."""
    id: int
    estado_anterior: Optional[str] = Field(default=None, description="Estado previo (None en el primer registro)")
    estado_nuevo: str = Field(..., description="Nuevo estado")
    usuario_id: Optional[int] = Field(default=None, description="ID del usuario que realizó la transición")
    timestamp: datetime
    observacion: Optional[str] = Field(default=None, description="Observación o motivo del cambio")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "estado_anterior": None,
                "estado_nuevo": "PENDIENTE",
                "usuario_id": 5,
                "timestamp": "2026-05-13T10:30:00",
                "observacion": "Pedido creado"
            }
        }


class PedidoResponse(BaseModel):
    """DTO para respuesta de lista de pedidos (resumen)."""
    id: int
    cliente_id: int
    estado: str
    total: float
    costo_envio: float = Field(default=0.0)
    creado_en: datetime

    class Config:
        schema_extra = {
            "example": {
                "id": 100,
                "cliente_id": 5,
                "estado": "PENDIENTE",
                "total": 450.50,
                "costo_envio": 0.0,
                "creado_en": "2026-05-13T10:30:00"
            }
        }


class EstadoUpdateDTO(BaseModel):
    """DTO para solicitar un cambio de estado manual en un pedido (FSM)."""
    nuevo_estado: str = Field(..., description="Estado destino (e.g. 'EN_PREPARACION', 'CANCELADO')")
    motivo: Optional[str] = Field(
        default=None,
        description="Motivo del cambio. Obligatorio cuando nuevo_estado == 'CANCELADO'."
    )

    @validator("motivo", always=True)
    def motivo_requerido_al_cancelar(cls, v, values):
        """RN-PE05: motivo obligatorio cuando se cancela un pedido."""
        nuevo_estado = values.get("nuevo_estado", "")
        if nuevo_estado == "CANCELADO":
            if not v or not v.strip():
                raise ValueError("El motivo es obligatorio cuando se cancela un pedido.")
        return v

    class Config:
        schema_extra = {
            "example": {
                "nuevo_estado": "EN_PREPARACION",
                "motivo": None
            }
        }


class PedidoGestionResponse(BaseModel):
    """DTO de resumen para el listado de gestión de pedidos (gestores/admin)."""
    id: int
    cliente_id: int
    estado: str
    total: float
    costo_envio: float = Field(default=0.0)
    creado_en: datetime

    class Config:
        schema_extra = {
            "example": {
                "id": 42,
                "cliente_id": 7,
                "estado": "CONFIRMADO",
                "total": 850.00,
                "costo_envio": 0.0,
                "creado_en": "2026-05-14T15:00:00"
            }
        }


class PedidoDetailResponse(BaseModel):
    """DTO para respuesta de detalle completo de pedido."""
    id: int
    cliente_id: int
    estado: str
    total: float
    costo_envio: float = Field(default=0.0)
    direccion_snapshot: Dict[str, Any]
    detalles: List[DetallePedidoResponse]
    historial: List[HistorialEstadoPedidoResponse]
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        schema_extra = {
            "example": {
                "id": 100,
                "cliente_id": 5,
                "estado": "PENDIENTE",
                "total": 450.50,
                "costo_envio": 0.0,
                "direccion_snapshot": {
                    "calle": "Av. San Martín",
                    "numero": "1234",
                    "ciudad": "Buenos Aires"
                },
                "detalles": [],
                "historial": [],
                "creado_en": "2026-05-13T10:30:00",
                "actualizado_en": "2026-05-13T10:30:00"
            }
        }
