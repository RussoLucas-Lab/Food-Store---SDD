"""
Pydantic schemas para Pedidos (órdenes).

Define DTOs para requests/responses de los endpoints de pedidos.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime


class CartItemDTO(BaseModel):
    """DTO para un item en el carrito"""
    producto_id: int = Field(..., description="ID del producto")
    cantidad: int = Field(..., gt=0, description="Cantidad (debe ser > 0)")
    personalizacion: Dict[str, Any] = Field(default_factory=dict, description="Personalización (ej: ingredientes excluidos)")
    
    class Config:
        schema_extra = {
            "example": {
                "producto_id": 1,
                "cantidad": 2,
                "personalizacion": {"excluidos": [5, 7]}
            }
        }


class CartCreateDTO(BaseModel):
    """DTO para crear un pedido desde el carrito"""
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
                    {"producto_id": 1, "cantidad": 2, "personalizacion": {}},
                    {"producto_id": 3, "cantidad": 1, "personalizacion": {"excluidos": [5]}}
                ],
                "direccion_id": 10
            }
        }


class DetallePedidoResponse(BaseModel):
    """DTO para respuesta de detalle de pedido"""
    id: int
    pedido_id: int
    producto_id: int
    cantidad: int
    precio_snapshot: float = Field(..., description="Precio al momento de la compra")
    personalizacion: Optional[Dict[str, Any]] = Field(default=None)
    creado_en: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "pedido_id": 100,
                "producto_id": 5,
                "cantidad": 2,
                "precio_snapshot": 150.00,
                "personalizacion": {"excluidos": [7]},
                "creado_en": "2026-05-13T10:30:00"
            }
        }


class HistorialEstadoPedidoResponse(BaseModel):
    """DTO para respuesta de historial de estado"""
    id: int
    pedido_id: int
    estado_anterior: Optional[str] = Field(default=None)
    estado_nuevo: str
    usuario_id: Optional[int] = Field(default=None)
    timestamp: datetime
    observacion: Optional[str] = Field(default=None)
    
    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "pedido_id": 100,
                "estado_anterior": None,
                "estado_nuevo": "PENDIENTE",
                "usuario_id": 5,
                "timestamp": "2026-05-13T10:30:00",
                "observacion": "Pedido creado"
            }
        }


class PedidoResponse(BaseModel):
    """DTO para respuesta de lista de pedidos (resumen)"""
    id: int
    cliente_id: int
    estado: str
    total: float
    creado_en: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": 100,
                "cliente_id": 5,
                "estado": "PENDIENTE",
                "total": 450.50,
                "creado_en": "2026-05-13T10:30:00"
            }
        }


class PedidoDetailResponse(BaseModel):
    """DTO para respuesta de detalle completo de pedido"""
    id: int
    cliente_id: int
    estado: str
    total: float
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
                "direccion_snapshot": {
                    "calle": "Av. San Martín",
                    "numero": "1234",
                    "departamento": "10A",
                    "ciudad": "Buenos Aires",
                    "provincia": "Buenos Aires",
                    "codigo_postal": "1636"
                },
                "detalles": [],
                "historial": [],
                "creado_en": "2026-05-13T10:30:00",
                "actualizado_en": "2026-05-13T10:30:00"
            }
        }


class PedidoCreateResponse(BaseModel):
    """DTO para respuesta de creación de pedido (con status 201)"""
    id: int
    cliente_id: int
    estado: str
    total: float
    creado_en: datetime
    
    class Config:
        schema_extra = {
            "example": {
                "id": 100,
                "cliente_id": 5,
                "estado": "PENDIENTE",
                "total": 450.50,
                "creado_en": "2026-05-13T10:30:00"
            }
        }
