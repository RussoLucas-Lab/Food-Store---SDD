"""
Servicios de seguridad transversales: contraseñas y tokens JWT.

Fusiona PasswordService (bcrypt) y TokenService (JWT) en un único módulo
de seguridad centralizado en backend/core/.
"""

import bcrypt
import re
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / '.env', override=True)


# ============================================================================
# PasswordService
# ============================================================================

class PasswordService:
    """Servicio para operaciones de contraseña segura"""

    # Requisitos de complejidad
    MIN_LENGTH = 8
    REQUIRE_UPPER = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = "!@#$%^&*"

    @staticmethod
    def hash_password(plaintext: str) -> str:
        """
        Hashear contraseña con bcrypt.

        Args:
            plaintext: Contraseña en texto plano

        Returns:
            Hash bcrypt de la contraseña (string)

        Nota: Nunca loguear plaintext
        """
        pwd_bytes = plaintext.encode('utf-8')
        hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
        return hashed.decode('utf-8')

    @staticmethod
    def verify_password(plaintext: str, hash_value: str) -> bool:
        """
        Verificar contraseña contra hash.

        Args:
            plaintext: Contraseña en texto plano a verificar
            hash_value: Hash bcrypt guardado (string)

        Returns:
            True si coincide, False si no

        Nota: No loguear plaintext
        """
        pwd_bytes = plaintext.encode('utf-8')
        hash_bytes = hash_value.encode('utf-8') if isinstance(hash_value, str) else hash_value
        return bcrypt.checkpw(pwd_bytes, hash_bytes)

    @staticmethod
    def validate_password_strength(password: str) -> List[str]:
        """
        Validar fortaleza de contraseña.

        Args:
            password: Contraseña a validar

        Returns:
            Lista vacía si válida, lista de errores si inválida

        Requisitos:
            - Mínimo 8 caracteres
            - Al menos 1 mayúscula
            - Al menos 1 dígito
            - Al menos 1 carácter especial (!@#$%^&*)
        """
        errors = []

        if len(password) < PasswordService.MIN_LENGTH:
            errors.append(f"Password debe tener al menos {PasswordService.MIN_LENGTH} caracteres")

        if PasswordService.REQUIRE_UPPER and not re.search(r'[A-Z]', password):
            errors.append("Password debe contener al menos una mayúscula (A-Z)")

        if PasswordService.REQUIRE_DIGIT and not re.search(r'[0-9]', password):
            errors.append("Password debe contener al menos un dígito (0-9)")

        if PasswordService.REQUIRE_SPECIAL:
            special_pattern = f"[{re.escape(PasswordService.SPECIAL_CHARS)}]"
            if not re.search(special_pattern, password):
                errors.append(f"Password debe contener al menos un carácter especial ({PasswordService.SPECIAL_CHARS})")

        return errors


# Instancia global del servicio
password_service = PasswordService()


# ============================================================================
# TokenService
# ============================================================================

class TokenService:
    """Servicio para operaciones JWT"""

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
            "sub": str(user_id),
            "email": email,
            "role": role,
            "exp": expire,
            "iat": datetime.utcnow(),
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
        if token not in cls._refresh_token_store:
            return False

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
