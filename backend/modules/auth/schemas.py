"""
Pydantic schemas para autenticación.
Validación de entrada/salida para endpoints auth.
"""

from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
import re
from backend.core.security import PasswordService

class RegisterRequest(BaseModel):
    """Request para registro de usuario"""
    email: EmailStr
    password: str
    nombre: Optional[str] = None

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        errors = PasswordService.validate_password_strength(v)
        if errors:
            raise ValueError("; ".join(errors))
        return v

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "nombre": "Juan"
        }
    })


class LoginRequest(BaseModel):
    """Request para login"""
    email: EmailStr
    password: str

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "email": "user@example.com",
            "password": "SecurePass123!"
        }
    })


class RefreshRequest(BaseModel):
    """Request para refresh token"""
    refresh_token: str

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
    })


class TokenResponse(BaseModel):
    """Response con tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # segundos

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "token_type": "Bearer",
            "expires_in": 900
        }
    })


class UserOut(BaseModel):
    """Response con datos públicos de usuario (sin password_hash)"""
    id: int
    email: str
    nombre: Optional[str] = None
    role: str  # "admin" | "customer"
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "user@example.com",
                "nombre": "user",
                "role": "customer",
                "is_active": True,
                "created_at": "2026-05-06T10:00:00",
                "updated_at": "2026-05-06T10:00:00"
            }
        }
    )


class UserCreate(BaseModel):
    """Schema para crear usuario (admin)"""
    email: EmailStr
    password: str
    role: str = "customer"

    @field_validator('role')
    @classmethod
    def validate_role(cls, v: str) -> str:
        if v not in ["admin", "customer"]:
            raise ValueError("Role debe ser 'admin' o 'customer'")
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        errors = PasswordService.validate_password_strength(v)
        if errors:
            raise ValueError("; ".join(errors))
        return v


class ErrorResponse(BaseModel):
    """Response genérica de error"""
    error: str
    detail: Optional[str] = None

    model_config = ConfigDict(json_schema_extra={
        "example": {
            "error": "Invalid credentials",
            "detail": "Email o contraseña incorrectos"
        }
    })
