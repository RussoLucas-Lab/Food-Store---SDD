"""
Rutas de autenticación.
Endpoints: /auth/register, /auth/login, /auth/refresh, /auth/me, /auth/logout
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import timedelta

from backend.schemas.auth_schema import (
    RegisterRequest, LoginRequest, RefreshRequest, TokenResponse, UserOut, ErrorResponse
)
from backend.services.password_service import PasswordService
from backend.services.token_service import TokenService
from repositories.usuario_repository import InMemoryUsuarioRepository
from models.usuario import RoleEnum

# Configurar router con prefix
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Limiter para rate limiting
limiter = Limiter(key_func=get_remote_address)

# Repository (por ahora en memoria, después se inyectará desde UoW)
usuario_repo = InMemoryUsuarioRepository()


# ============================================================================
# HELPERS
# ============================================================================

def get_current_user_id_from_token(authorization: str | None = None) -> int:
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
    
    # Esperar formato "Bearer <token>"
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

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest) -> UserOut:
    """
    Registrar nuevo usuario.
    
    - **email**: Correo único
    - **password**: Contraseña (mín 8 chars, mayús, dígito, especial)
    
    Returns: Usuario creado sin password_hash
    """
    # Validar email único
    existing = usuario_repo.find_by_email(req.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash contraseña
    password_hash = PasswordService.hash_password(req.password)
    
    # Crear usuario (rol por defecto: customer)
    try:
        usuario = usuario_repo.create(
            email=req.email,
            password_hash=password_hash,
            role=RoleEnum.CUSTOMER
        )
        
        # Retornar sin password_hash
        return UserOut(
            id=usuario.id,
            email=usuario.email,
            nombre=usuario.nombre,
            role=usuario.role.value,
            is_active=usuario.is_active,
            created_at=usuario.created_at,
            updated_at=usuario.updated_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/15 minutes")  # Rate limiting: 5 intentos / 15 min
async def login(req: LoginRequest, request: Request) -> TokenResponse:
    """
    Login y obtener tokens JWT.
    
    Rate limit: 5 intentos por 15 minutos por IP
    
    Returns: access_token, refresh_token, expires_in
    """
    # Buscar usuario por email
    usuario = usuario_repo.find_by_email(req.email)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Validar contraseña
    if not PasswordService.verify_password(req.password, usuario.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Validar que usuario está activo
    if not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account disabled"
        )
    
    # Generar tokens
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
        expires_in=TokenService.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # en segundos
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(req: RefreshRequest) -> TokenResponse:
    """
    Obtener nuevo access_token usando refresh_token.
    
    Returns: Nuevo access_token con misma duración
    """
    # Validar refresh token
    if not TokenService.validate_refresh_token(req.refresh_token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Extraer user_id del token
    try:
        payload = TokenService.decode_token(req.refresh_token)
        user_id = int(payload.get("sub"))
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Obtener usuario y generar nuevo access_token
    usuario = usuario_repo.find_by_id(user_id)
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
        refresh_token=req.refresh_token,  # Reutilizar mismo refresh_token
        token_type="Bearer",
        expires_in=TokenService.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.get("/me", response_model=UserOut)
async def get_current_user(authorization: str | None = Header(None)) -> UserOut:
    """
    Obtener perfil del usuario autenticado.
    
    Requiere: Authorization: Bearer <access_token>
    
    Returns: Datos del usuario actual
    """
    user_id = get_current_user_id_from_token(authorization)
    
    usuario = usuario_repo.find_by_id(user_id)
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
async def logout(authorization: str | None = Header(None)):
    """
    Logout: revocar refresh_token.
    
    Requiere: Authorization: Bearer <access_token>
    
    Returns: Mensaje de éxito
    """
    user_id = get_current_user_id_from_token(authorization)
    
    # El logout se realiza simplemente descartando el token en el cliente.
    # Opcionalmente, si queremos revocar refresh tokens:
    # TokenService.revoke_refresh_token(refresh_token)
    
    return {
        "message": "Logged out successfully",
        "status": "ok"
    }
