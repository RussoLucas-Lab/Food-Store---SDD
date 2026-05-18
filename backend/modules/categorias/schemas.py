"""
Pydantic schemas para Categoría.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
import re


class CategoriaCreateRequest(BaseModel):
    """Schema para crear nueva categoría"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre de la categoría")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción opcional")

    @field_validator('nombre')
    @classmethod
    def sanitize_nombre(cls, v):
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-\.]+$', v):
            raise ValueError('nombre contiene caracteres no permitidos')
        return v

    @field_validator('descripcion')
    @classmethod
    def sanitize_descripcion(cls, v):
        if v is None:
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('descripción excede 500 caracteres')
        return v


class CategoriaUpdateRequest(BaseModel):
    """Schema para actualizar categoría"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nuevo nombre (opcional)")
    descripcion: Optional[str] = Field(None, max_length=500, description="Nueva descripción (opcional)")

    @field_validator('nombre')
    @classmethod
    def sanitize_nombre(cls, v):
        if v is None:
            return v
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-\.]+$', v):
            raise ValueError('nombre contiene caracteres no permitidos')
        return v

    @field_validator('descripcion')
    @classmethod
    def sanitize_descripcion(cls, v):
        if v is None:
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('descripción excede 500 caracteres')
        return v


class CategoriaResponse(BaseModel):
    """Schema de respuesta para una categoría"""
    id: int
    nombre: str
    descripcion: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CategoriaListResponse(BaseModel):
    """Schema de respuesta para listado de categorías"""
    items: List[CategoriaResponse]
    total: int = Field(..., description="Total de categorías")
    skip: int = Field(..., description="Número de registros saltados")
    limit: int = Field(..., description="Límite de registros")

    class Config:
        from_attributes = True
