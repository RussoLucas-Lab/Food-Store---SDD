"""
Rutas de autenticación.
Endpoints: /auth/register, /auth/login, /auth/refresh, /auth/me, /auth/logout
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import timedelta
from typing import Optional

from .schemas import (
    RegisterRequest, LoginRequest, RefreshRequest, TokenResponse, UserOut, ErrorResponse
)
from .model import RoleEnum
from backend.core.security import PasswordService, TokenService
from backend.core.deps import get_uow
from backend.core.uow_postgresql import PostgreSQLUnitOfWork

# Configurar router con prefix
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Limiter para rate limiting
limiter = Limiter(key_func=get_remote_address)


# ============================================================================
# HELPERS
# ============================================================================

def get_current_user_id_from_token(authorization: Optional[str] = None) -> int:
    """
    Extraer user_id del JWT en Authorization header.

    Raises:
        HTTPException si token es inválido o no está presente
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    token = parts[1]

    try:
        user_id = TokenService.get_user_id_from_token(token)
        if user_id is None:
            raise ValueError("Cannot extract user_id")
        return user_id
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, uow: PostgreSQLUnitOfWork = Depends(get_uow)) -> TokenResponse:
    """
    Registrar nuevo usuario y devolver tokens (auto-login).
    """
    existing = uow.usuarios.find_by_email(req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    password_hash = PasswordService.hash_password(req.password)

    try:
        usuario = uow.usuarios.create(
            email=req.email,
            password_hash=password_hash,
            role=RoleEnum.CUSTOMER,
            nombre=req.nombre,
        )
        uow.commit()

        access_token = TokenService.create_access_token(
            user_id=usuario.id,
            email=usuario.email,
            role=usuario.role.value
        )
        refresh_token = TokenService.create_refresh_token(user_id=usuario.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
            expires_in=TokenService.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/15 minutes")
async def login(req: LoginRequest, request: Request, uow: PostgreSQLUnitOfWork = Depends(get_uow)) -> TokenResponse:
    """
    Login y obtener tokens JWT.
    """
    usuario = uow.usuarios.find_by_email(req.email)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not PasswordService.verify_password(req.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account disabled"
        )

    access_token = TokenService.create_access_token(
        user_id=usuario.id,
        email=usuario.email,
        role=usuario.role.value
    )

    refresh_token = TokenService.create_refresh_token(user_id=usuario.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="Bearer",
        expires_in=TokenService.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(req: RefreshRequest, uow: PostgreSQLUnitOfWork = Depends(get_uow)) -> TokenResponse:
    """
    Obtener nuevo access_token usando refresh_token.
    """
    if not TokenService.validate_refresh_token(req.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    try:
        payload = TokenService.decode_token(req.refresh_token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    usuario = uow.usuarios.find_by_id(user_id)
    if not usuario or not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    access_token = TokenService.create_access_token(
        user_id=usuario.id,
        email=usuario.email,
        role=usuario.role.value
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=req.refresh_token,
        token_type="Bearer",
        expires_in=TokenService.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserOut)
async def get_current_user(authorization: Optional[str] = Header(None), uow: PostgreSQLUnitOfWork = Depends(get_uow)) -> UserOut:
    """
    Obtener perfil del usuario autenticado.
    """
    user_id = get_current_user_id_from_token(authorization)

    usuario = uow.usuarios.find_by_id(user_id)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserOut(
        id=usuario.id,
        email=usuario.email,
        nombre=usuario.nombre,
        role=usuario.role.value,
        is_active=usuario.is_active,
        created_at=usuario.created_at,
        updated_at=usuario.updated_at
    )


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """
    Logout: revocar refresh_token.
    """
    user_id = get_current_user_id_from_token(authorization)

    return {
        "message": "Logged out successfully",
        "status": "ok"
    }
