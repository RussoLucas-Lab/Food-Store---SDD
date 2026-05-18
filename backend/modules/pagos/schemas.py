"""
Pydantic schemas para Pagos (MercadoPago).

Schemas de request (DTO) y response para la API de pagos.
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime


class PagoCreateDTO(BaseModel):
    """DTO para crear un pago con MercadoPago."""

    pedido_id: int = Field(..., description="ID del pedido a pagar")
    token: str = Field(..., description="Token de tarjeta generado por MP SDK en el browser")
    installments: int = Field(1, ge=1, description="Número de cuotas")
    payment_method_id: str = Field(..., description="ID del método de pago (ej: visa, master)")
    issuer_id: Optional[str] = Field(None, description="ID del banco emisor (opcional)")

    class Config:
        schema_extra = {
            "example": {
                "pedido_id": 42,
                "token": "abc123token",
                "installments": 1,
                "payment_method_id": "visa",
                "issuer_id": "310"
            }
        }


class PagoResponse(BaseModel):
    """DTO para respuesta de creación/consulta de pago."""

    id: int
    pedido_id: int
    mp_payment_id: Optional[str] = Field(None, description="ID del pago en MercadoPago")
    mp_status: str = Field(..., description="Estado del pago en MercadoPago")
    creado_en: datetime

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "pedido_id": 42,
                "mp_payment_id": "12345678",
                "mp_status": "approved",
                "creado_en": "2026-05-16T10:30:00"
            }
        }


class WebhookPayload(BaseModel):
    """DTO para el payload del webhook de MercadoPago."""

    id: Optional[int] = Field(None, description="ID de la notificación")
    action: Optional[str] = Field(None, description="Acción (payment.created, payment.updated)")
    data: Optional[dict] = Field(None, description="Datos del evento")
    type: Optional[str] = Field(None, description="Tipo de notificación")

    class Config:
        schema_extra = {
            "example": {
                "id": 1234,
                "action": "payment.updated",
                "data": {"id": "87654321"},
                "type": "payment"
            }
        }
