"""
Pydantic v2 schemas para DireccionEntrega.

Separados en Create / Update / Response siguiendo convenciones del proyecto.
El cliente_id NUNCA viene del body — siempre se extrae del JWT.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class DireccionCreate(BaseModel):
    """Schema para crear una nueva dirección de entrega."""
    calle: str = Field(..., min_length=1, max_length=255, description="Nombre de la calle")
    numero: str = Field(..., min_length=1, max_length=20, description="Número de puerta (puede ser 'S/N', '1234 bis', etc.)")
    ciudad: str = Field(..., min_length=1, max_length=100, description="Ciudad")
    provincia: str = Field(..., min_length=1, max_length=100, description="Provincia")
    codigo_postal: str = Field(..., min_length=1, max_length=20, description="Código postal")
    piso: Optional[str] = Field(None, max_length=10, description="Piso (opcional)")
    departamento: Optional[str] = Field(None, max_length=10, description="Departamento/unidad (opcional)")
    referencia: Optional[str] = Field(None, max_length=500, description="Referencia adicional (opcional)")
    es_predeterminada: bool = Field(False, description="Marcar como dirección predeterminada")


class DireccionUpdate(BaseModel):
    """Schema para edición parcial de una dirección de entrega."""
    calle: Optional[str] = Field(None, min_length=1, max_length=255)
    numero: Optional[str] = Field(None, min_length=1, max_length=20)
    ciudad: Optional[str] = Field(None, min_length=1, max_length=100)
    provincia: Optional[str] = Field(None, min_length=1, max_length=100)
    codigo_postal: Optional[str] = Field(None, min_length=1, max_length=20)
    piso: Optional[str] = Field(None, max_length=10)
    departamento: Optional[str] = Field(None, max_length=10)
    referencia: Optional[str] = Field(None, max_length=500)
    es_predeterminada: Optional[bool] = None


class DireccionResponse(BaseModel):
    """Schema de respuesta para una dirección de entrega."""
    id: int
    cliente_id: int
    calle: str
    numero: str
    ciudad: str
    provincia: str
    codigo_postal: str
    piso: Optional[str]
    departamento: Optional[str]
    referencia: Optional[str]
    es_predeterminada: bool
    activo: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
