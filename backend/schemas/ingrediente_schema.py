"""
Pydantic schemas para Ingrediente.

Define los contratos de entrada y salida para operaciones CRUD de ingredientes,
incluyendo enums para unidades de medida.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
from enum import Enum
import re


class UnidadMedidaEnum(str, Enum):
    """Unidades de medida disponibles"""
    GRAMOS = "gramos"
    LITROS = "litros"
    UNIDADES = "unidades"
    KILOS = "kilos"
    MILILITROS = "mililitros"


class IngredienteCreateRequest(BaseModel):
    """Schema para crear nuevo ingrediente"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del ingrediente")
    unidad_medida: UnidadMedidaEnum = Field(..., description="Unidad de medida")
    cantidad_stock: int = Field(..., ge=0, description="Cantidad inicial en stock")
    cantidad_minima: int = Field(..., ge=0, description="Cantidad mínima antes de alerta")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción opcional")
    categoria_id: Optional[int] = Field(None, description="ID de categoría relacionada")
    
    @field_validator('nombre')
    @classmethod
    def sanitize_nombre(cls, v):
        """Validar y sanitizar nombre"""
        v = v.strip()
        
        # Rechazar caracteres peligrosos (SQL injection, XSS)
        if not re.match(r'^[a-zA-Z0-9áéíóúñÁÉÍÓÚÑ\s\-\.]+$', v):
            raise ValueError('nombre contiene caracteres no permitidos')
        
        return v
    
    @field_validator('descripcion')
    @classmethod
    def sanitize_descripcion(cls, v):
        """Validar y sanitizar descripción"""
        if v is None:
            return v
        
        v = v.strip()
        if len(v) > 500:
            raise ValueError('descripción excede 500 caracteres')
        
        return v
    
    @field_validator('cantidad_minima')
    @classmethod
    def validate_minima(cls, v, info):
        """Validar que cantidad_minima sea razonable"""
        if v < 0:
            raise ValueError('cantidad_minima no puede ser negativa')
        return v


class IngredienteUpdateRequest(BaseModel):
    """Schema para actualizar ingrediente"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nuevo nombre (opcional)")
    descripcion: Optional[str] = Field(None, max_length=500, description="Nueva descripción (opcional)")
    cantidad_stock: Optional[int] = Field(None, ge=0, description="Nuevo stock (opcional)")
    cantidad_minima: Optional[int] = Field(None, ge=0, description="Nueva cantidad mínima (opcional)")
    
    @field_validator('nombre')
    @classmethod
    def sanitize_nombre(cls, v):
        """Validar y sanitizar nombre"""
        if v is None:
            return v
        
        v = v.strip()
        
        if not re.match(r'^[a-zA-Z0-9áéíóúñÁÉÍÓÚÑ\s\-\.]+$', v):
            raise ValueError('nombre contiene caracteres no permitidos')
        
        return v
    
    @field_validator('descripcion')
    @classmethod
    def sanitize_descripcion(cls, v):
        """Validar y sanitizar descripción"""
        if v is None:
            return v
        
        v = v.strip()
        if len(v) > 500:
            raise ValueError('descripción excede 500 caracteres')
        
        return v


class IngredienteResponse(BaseModel):
    """Schema de respuesta para ingrediente"""
    id: int
    nombre: str
    descripcion: str
    unidad_medida: str
    cantidad_stock: int
    cantidad_minima: int
    cantidad_reservada: int
    stock_disponible: int
    alerta_stock_bajo: bool
    categoria_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class IngredienteListResponse(BaseModel):
    """Schema de respuesta para listado de ingredientes"""
    ingredientes: List[IngredienteResponse]
    total: int
    skip: int
    limit: int
    
    class Config:
        from_attributes = True


class StockHistoryResponse(BaseModel):
    """Schema de respuesta para historial de stock"""
    id: int
    ingrediente_id: int
    admin_id: int
    cantidad_anterior: int
    cantidad_nueva: int
    motivo: str
    created_at: datetime
    
    class Config:
        from_attributes = True
