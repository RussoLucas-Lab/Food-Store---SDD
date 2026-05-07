"""
Servicio de tokens JWT para autenticación.
Genera, valida y decodifica JWT access + refresh tokens.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / '.env', override=True)

class TokenService:
    """Servicio para operaciones JWT"""
    
    # Cargar configuración desde Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', 15))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', 7))
    
    # Store de refresh tokens en memoria {token: {user_id, exp}}
    _refresh_token_store: Dict[str, Dict] = {}
    
    @classmethod
    def create_access_token(
        cls,
        user_id: int,
        email: str,
        role: str,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crear JWT access token.
        
        Args:
            user_id: ID del usuario
            email: Email del usuario
            role: Rol del usuario (admin | customer)
            expires_delta: Duración custom del token
            
        Returns:
            JWT access token como string
        """
        if expires_delta is None:
            expires_delta = timedelta(minutes=cls.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": str(user_id),  # subject (user_id)
            "email": email,
            "role": role,
            "exp": expire,  # expiration time
            "iat": datetime.utcnow(),  # issued at
            "type": "access"
        }
        
        encoded_jwt = jwt.encode(
            payload,
            cls.SECRET_KEY,
            algorithm=cls.ALGORITHM
        )
        
        return encoded_jwt
    
    @classmethod
    def create_refresh_token(
        cls,
        user_id: int,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Crear JWT refresh token.
        
        Args:
            user_id: ID del usuario
            expires_delta: Duración custom del token
            
        Returns:
            JWT refresh token como string
        """
        if expires_delta is None:
            expires_delta = timedelta(days=cls.REFRESH_TOKEN_EXPIRE_DAYS)
        
        expire = datetime.utcnow() + expires_delta
        
        payload = {
            "sub": str(user_id),
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        encoded_jwt = jwt.encode(
            payload,
            cls.SECRET_KEY,
            algorithm=cls.ALGORITHM
        )
        
        # Guardar token en store para validación posterior
        cls._refresh_token_store[encoded_jwt] = {
            "user_id": user_id,
            "exp": expire
        }
        
        return encoded_jwt
    
    @classmethod
    def decode_token(cls, token: str) -> Dict:
        """
        Decodificar y validar JWT.
        
        Args:
            token: JWT token a decodificar
            
        Returns:
            Dict con los claims del token
            
        Raises:
            JWTError si el token es inválido o está expirado
        """
        try:
            payload = jwt.decode(
                token,
                cls.SECRET_KEY,
                algorithms=[cls.ALGORITHM]
            )
            return payload
        except JWTError as e:
            raise ValueError(f"Token inválido o expirado: {str(e)}")
    
    @classmethod
    def validate_token(cls, token: str) -> bool:
        """
        Validar que un token sea válido.
        
        Args:
            token: JWT token a validar
            
        Returns:
            True si válido, False si no
        """
        try:
            cls.decode_token(token)
            return True
        except (JWTError, ValueError):
            return False
    
    @classmethod
    def validate_refresh_token(cls, token: str) -> bool:
        """
        Validar que un refresh token sea válido y no haya sido revocado.
        
        Args:
            token: Refresh token a validar
            
        Returns:
            True si válido y no revocado, False si no
        """
        # Verificar que está en el store (no fue revocado)
        if token not in cls._refresh_token_store:
            return False
        
        # Verificar que no está expirado
        try:
            payload = cls.decode_token(token)
            if payload.get("type") != "refresh":
                return False
            return True
        except (JWTError, ValueError):
            return False
    
    @classmethod
    def revoke_refresh_token(cls, token: str) -> bool:
        """
        Revocar un refresh token (logout).
        
        Args:
            token: Refresh token a revocar
            
        Returns:
            True si fue revocado, False si no existía
        """
        if token in cls._refresh_token_store:
            del cls._refresh_token_store[token]
            return True
        return False
    
    @classmethod
    def get_user_id_from_token(cls, token: str) -> Optional[int]:
        """
        Extraer user_id del token.
        
        Args:
            token: JWT token
            
        Returns:
            user_id si es válido, None si no
        """
        try:
            payload = cls.decode_token(token)
            user_id = payload.get("sub")
            return int(user_id) if user_id else None
        except (JWTError, ValueError):
            return None


# Instancia global
token_service = TokenService()
