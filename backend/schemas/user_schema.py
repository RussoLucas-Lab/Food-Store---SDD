"""
Schemas de usuario para otras operaciones.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    """Base schema con campos comunes"""
    email: EmailStr
    nombre: Optional[str] = None
    role: str = "customer"


class UserUpdate(BaseModel):
    """Schema para actualizar usuario"""
    email: Optional[EmailStr] = None
    nombre: Optional[str] = None
    is_active: Optional[bool] = None


class UserListResponse(BaseModel):
    """Response para listar usuarios"""
    id: int
    email: str
    nombre: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
