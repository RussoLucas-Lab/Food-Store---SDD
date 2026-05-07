"""
Middleware y decoradores para autenticación JWT.
"""

from fastapi import Depends, HTTPException, status, Request
from functools import wraps
from typing import Callable, Optional
from backend.services.token_service import TokenService


class CurrentUser:
    """Objeto que contiene info del usuario autenticado"""
    def __init__(self, user_id: int, email: str, role: str):
        self.user_id = user_id
        self.email = email
        self.role = role
    
    def __repr__(self):
        return f"<CurrentUser id={self.user_id} email={self.email} role={self.role}>"


def extract_token_from_header(authorization: Optional[str] = None) -> Optional[str]:
    """
    Extraer JWT del Authorization header.
    
    Espera formato: "Bearer <token>"
    
    Args:
        authorization: Header Authorization
        
    Returns:
        Token si es válido, None si no
    """
    if not authorization:
        return None
    
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    return parts[1]


def verify_jwt_token(token: str) -> CurrentUser:
    """
    Verificar JWT y retornar CurrentUser.
    
    Args:
        token: JWT token
        
    Returns:
        CurrentUser con info del token
        
    Raises:
        HTTPException si token es inválido
    """
    try:
        payload = TokenService.decode_token(token)
        
        user_id = int(payload.get("sub"))
        email = payload.get("email")
        role = payload.get("role")
        
        if not all([user_id, email, role]):
            raise ValueError("Missing required claims")
        
        return CurrentUser(user_id=user_id, email=email, role=role)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )


def get_current_user(authorization: Optional[str] = None) -> CurrentUser:
    """
    Dependency para obtener usuario autenticado.
    
    Uso en endpoints:
    ```
    @router.get("/protected")
    async def protected_route(current_user: CurrentUser = Depends(get_current_user)):
        ...
    ```
    
    Args:
        authorization: Header Authorization
        
    Returns:
        CurrentUser autenticado
        
    Raises:
        HTTPException 401 si token es inválido o no está presente
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing"
        )
    
    token = extract_token_from_header(authorization)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    return verify_jwt_token(token)


def require_role(*allowed_roles: str, allow_customer: bool = False):
    """
    Dependency inyectable para validar roles en endpoints FastAPI.
    
    Uso:
    ```
    @router.post("/admin-only")
    def admin_endpoint(user_id: int = Depends(require_role("admin"))):
        ...
    
    @router.get("/public")
    def public_endpoint(user_id: int = Depends(require_role(allow_customer=True))):
        # user_id puede ser None si es público
        ...
    ```
    
    Args:
        *allowed_roles: Roles permitidos (e.g., "admin", "customer")
        allow_customer: Si True, permite acceso sin autenticación (para GET públicos)
    
    Returns:
        Dependency que retorna user_id o None
    """
    if not allowed_roles and not allow_customer:
        allowed_roles = ("admin", "customer")
    
    def dependency(authorization: Optional[str] = None) -> Optional[int]:
        # Si allow_customer=True, permitir sin token
        if allow_customer and not authorization:
            return None
        
        # Sino, requerir autenticación
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header missing"
            )
        
        token = extract_token_from_header(authorization)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format"
            )
        
        current_user = verify_jwt_token(token)
        
        # Validar rol si se especificó
        if allowed_roles and current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(allowed_roles)}"
            )
        
        return current_user.user_id
    
    return dependency


class JWTMiddleware:
    """
    Middleware para validar JWT en requests.
    
    Extrae token del Authorization header y valida firma/expiration.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        # Extraer token si está presente
        auth_header = request.headers.get("authorization")
        
        if auth_header:
            token = extract_token_from_header(auth_header)
            if token and TokenService.validate_token(token):
                try:
                    user = verify_jwt_token(token)
                    # Guardar en request.state para acceso posterior
                    request.state.current_user = user
                except HTTPException:
                    pass  # Token inválido, seguir sin usuario
        
        response = await call_next(request)
        return response
