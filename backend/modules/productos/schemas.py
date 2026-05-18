"""
Pydantic schemas para Producto.
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List
import re


class ProductIngredientInput(BaseModel):
    """Schema para especificar un ingrediente en la composición de un producto"""
    ingredient_id: int = Field(..., gt=0, description="ID del ingrediente")
    quantity_required: float = Field(..., gt=0, description="Cantidad requerida del ingrediente")


class ProductIngredientResponse(BaseModel):
    """Schema de respuesta para un ingrediente en la composición"""
    id: int
    ingredient_id: int
    quantity_required: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductCreateRequest(BaseModel):
    """Schema para crear nuevo producto"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del producto")
    base_price: float = Field(..., gt=0, description="Precio base del producto (> 0)")
    descripcion: Optional[str] = Field(None, max_length=500, description="Descripción opcional")
    categories: List[int] = Field(..., min_length=1, description="Lista de IDs de categorías (mín 1)")
    ingredients: List[ProductIngredientInput] = Field(..., min_length=1, description="Lista de ingredientes con cantidades (mín 1)")

    @field_validator('nombre')
    @classmethod
    def sanitize_nombre(cls, v):
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-\.,&()]+$', v):
            raise ValueError('nombre contiene caracteres no permitidos')
        return v

    @field_validator('base_price')
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('base_price debe ser > 0')
        return round(float(v), 2)

    @field_validator('descripcion')
    @classmethod
    def sanitize_descripcion(cls, v):
        if v is None:
            return v
        v = v.strip()
        if len(v) > 500:
            raise ValueError('descripción excede 500 caracteres')
        return v


class ProductUpdateRequest(BaseModel):
    """Schema para actualizar producto"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100, description="Nuevo nombre (opcional)")
    base_price: Optional[float] = Field(None, gt=0, description="Nuevo precio (opcional)")
    descripcion: Optional[str] = Field(None, max_length=500, description="Nueva descripción (opcional)")
    categories: Optional[List[int]] = Field(None, min_length=1, description="Nuevas categorías (opcional, mín 1)")
    ingredients: Optional[List[ProductIngredientInput]] = Field(None, min_length=1, description="Nuevos ingredientes (opcional, mín 1)")

    @field_validator('nombre')
    @classmethod
    def sanitize_nombre(cls, v):
        if v is None:
            return v
        v = v.strip()
        if not re.match(r'^[a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s\-\.,&()]+$', v):
            raise ValueError('nombre contiene caracteres no permitidos')
        return v

    @field_validator('base_price')
    @classmethod
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('base_price debe ser > 0')
        if v is not None:
            return round(float(v), 2)
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


class CategoryInfo(BaseModel):
    """Schema para información de categoría en respuesta de producto"""
    id: int
    nombre: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True


class ProductResponse(BaseModel):
    """Schema de respuesta para un producto (listado)"""
    id: int
    nombre: str
    descripcion: str
    base_price: float
    status: str
    stock_disponible: int = Field(description="Stock disponible calculado (entero)")
    created_at: datetime
    updated_at: datetime
    # Campos normalizados para el frontend
    precio: float = 0.0
    disponible: bool = False
    stock: int = 0
    imagen_url: Optional[str] = None

    class Config:
        from_attributes = True


class ProductDetailResponse(BaseModel):
    """Schema de respuesta para detalle completo de un producto"""
    id: int
    nombre: str
    descripcion: str
    base_price: float
    status: str
    categories: List[CategoryInfo] = Field(description="Categorías del producto")
    ingredients: List[ProductIngredientResponse] = Field(description="Ingredientes del producto")
    stock_disponible: int = Field(description="Stock disponible calculado (entero)")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductStockUpdateRequest(BaseModel):
    """Schema para actualizar stock manual de un producto"""
    stock: int = Field(..., ge=0, description="Nuevo valor de stock (>= 0)")


class ProductStockResponse(BaseModel):
    """Schema de respuesta para consulta de stock disponible"""
    product_id: int
    nombre: str
    stock_disponible: int = Field(description="Unidades disponibles del producto")
    calculado_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema de respuesta para listado de productos"""
    items: List[ProductResponse]
    total: int = Field(..., description="Total de productos")
    skip: int = Field(..., description="Número de registros saltados")
    limit: int = Field(..., description="Límite de registros")

    class Config:
        from_attributes = True
