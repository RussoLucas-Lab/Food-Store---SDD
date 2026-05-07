"""
Tests para token_service.py
"""

import pytest
from datetime import timedelta, datetime
from backend.services.token_service import TokenService
from jose import JWTError

class TestTokenService:
    
    def test_create_access_token(self):
        """Crear access token válido"""
        token = TokenService.create_access_token(
            user_id=1,
            email="user@example.com",
            role="customer"
        )
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token.split('.')) == 3  # JWT tiene 3 partes
    
    def test_create_refresh_token(self):
        """Crear refresh token válido"""
        token = TokenService.create_refresh_token(user_id=1)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token.split('.')) == 3
    
    def test_decode_valid_access_token(self):
        """Decodificar access token válido"""
        original_token = TokenService.create_access_token(
            user_id=123,
            email="test@example.com",
            role="admin"
        )
        
        payload = TokenService.decode_token(original_token)
        
        assert payload["sub"] == "123"
        assert payload["email"] == "test@example.com"
        assert payload["role"] == "admin"
        assert payload["type"] == "access"
    
    def test_decode_expired_token_raises_error(self):
        """Decodificar token expirado debe lanzar error"""
        # Crear token con expiración inmediata
        expired_token = TokenService.create_access_token(
            user_id=1,
            email="test@example.com",
            role="customer",
            expires_delta=timedelta(seconds=-1)  # Ya expirado
        )
        
        with pytest.raises(ValueError):
            TokenService.decode_token(expired_token)
    
    def test_decode_tampered_token_raises_error(self):
        """Decodificar token alterado debe lanzar error"""
        token = TokenService.create_access_token(
            user_id=1,
            email="test@example.com",
            role="customer"
        )
        
        # Alterar el token
        tampered = token[:-10] + "corrupted!"
        
        with pytest.raises(ValueError):
            TokenService.decode_token(tampered)
    
    def test_validate_token_valid(self):
        """Validar token válido"""
        token = TokenService.create_access_token(
            user_id=1,
            email="test@example.com",
            role="customer"
        )
        
        assert TokenService.validate_token(token) is True
    
    def test_validate_token_invalid(self):
        """Validar token inválido"""
        invalid_token = "not.a.jwt"
        
        assert TokenService.validate_token(invalid_token) is False
    
    def test_validate_refresh_token_valid(self):
        """Validar refresh token válido"""
        token = TokenService.create_refresh_token(user_id=1)
        
        assert TokenService.validate_refresh_token(token) is True
    
    def test_validate_refresh_token_after_revoke(self):
        """Refresh token revocado no debe validar"""
        token = TokenService.create_refresh_token(user_id=1)
        
        # Validar que es válido
        assert TokenService.validate_refresh_token(token) is True
        
        # Revocar (logout)
        TokenService.revoke_refresh_token(token)
        
        # Ahora no debe validar
        assert TokenService.validate_refresh_token(token) is False
    
    def test_get_user_id_from_token(self):
        """Extraer user_id del token"""
        token = TokenService.create_access_token(
            user_id=42,
            email="test@example.com",
            role="admin"
        )
        
        user_id = TokenService.get_user_id_from_token(token)
        assert user_id == 42
    
    def test_get_user_id_from_invalid_token(self):
        """Extraer user_id de token inválido retorna None"""
        user_id = TokenService.get_user_id_from_token("invalid.token.here")
        assert user_id is None
    
    def test_token_claims_contain_all_required_fields(self):
        """Access token debe contener todos los claims necesarios"""
        token = TokenService.create_access_token(
            user_id=1,
            email="user@example.com",
            role="customer"
        )
        
        payload = TokenService.decode_token(token)
        
        assert "sub" in payload
        assert "email" in payload
        assert "role" in payload
        assert "exp" in payload
        assert "iat" in payload
        assert "type" in payload
        assert payload["type"] == "access"
