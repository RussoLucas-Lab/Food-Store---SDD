"""
Pydantic schemas para Cliente.
"""

from pydantic import BaseModel, Field, field_validator, EmailStr
from datetime import datetime
from typing import Optional, List
import re


class ClienteCreateRequest(BaseModel):
    """Schema para crear nuevo cliente"""
    nombre: str = Field(..., min_length=1, max_length=255, description="Nombre del cliente")
    email: EmailStr = Field(..., description="Email del cliente (único)")
    direccion: str = Field(..., min_length=1, max_length=500, description="Dirección de entrega")
    telefono: Optional[str] = Field(None, max_length=20, description="Teléfono del cliente (opcional)")

    @field_validator('nombre')
    @classmethod
    def sanitize_nombre(cls, v):
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-\.]+$', v):
            raise ValueError('nombre contiene caracteres no permitidos')
        return v

    @field_validator('direccion')
    @classmethod
    def sanitize_direccion(cls, v):
        v = v.strip()
        if len(v) > 500:
            raise ValueError('dirección excede 500 caracteres')
        return v

    @field_validator('telefono')
    @classmethod
    def validate_telefono(cls, v):
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        if not re.match(r'^[\d\-\+\s\(\)]{7,20}$', v):
            raise ValueError('formato de teléfono inválido')
        return v


class ClienteUpdateRequest(BaseModel):
    """Schema para actualizar cliente"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=255, description="Nuevo nombre (opcional)")
    email: Optional[EmailStr] = Field(None, description="Nuevo email (opcional, debe ser único)")
    direccion: Optional[str] = Field(None, min_length=1, max_length=500, description="Nueva dirección (opcional)")
    telefono: Optional[str] = Field(None, max_length=20, description="Nuevo teléfono (opcional)")

    @field_validator('nombre')
    @classmethod
    def sanitize_nombre(cls, v):
        if v is None:
            return v
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-\.]+$', v):
            raise ValueError('nombre contiene caracteres no permitidos')
        return v

    @field_validator('direccion')
    @classmethod
    def sanitize_direccion(cls, v):
        if v is None:
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('dirección excede 500 caracteres')
        return v

    @field_validator('telefono')
    @classmethod
    def validate_telefono(cls, v):
        if v is None:
            return v
        v = v.strip()
        if not v:
            return None
        if not re.match(r'^[\d\-\+\s\(\)]{7,20}$', v):
            raise ValueError('formato de teléfono inválido')
        return v


class ClienteResponse(BaseModel):
    """Schema de respuesta para un cliente"""
    id: int
    nombre: str
    email: str
    telefono: Optional[str]
    direccion: str
    activo: bool
    user_id: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClienteListResponse(BaseModel):
    """Schema de respuesta para listado de clientes"""
    items: List[ClienteResponse]
    total: int = Field(..., description="Total de clientes")
    skip: int = Field(..., description="Número de registros saltados")
    limit: int = Field(..., description="Límite de registros")

    class Config:
        from_attributes = True


class ClienteSearchResponse(BaseModel):
    """Schema de respuesta para búsqueda de clientes"""
    items: List[ClienteResponse]
    query: str = Field(..., description="Búsqueda realizada")
    count: int = Field(..., description="Número de resultados")

    class Config:
        from_attributes = True
