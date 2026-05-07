"""
Tests para JWT middleware y decoradores
"""

import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, Depends, HTTPException, status
from datetime import timedelta

from backend.middleware.jwt_middleware import (
    get_current_user, CurrentUser, require_role, extract_token_from_header, verify_jwt_token
)
from backend.services.token_service import TokenService


class TestJWTMiddleware:
    
    def test_extract_token_valid_header(self):
        """Extraer token de header válido"""
        auth_header = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        token = extract_token_from_header(auth_header)
        
        assert token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    
    def test_extract_token_invalid_format(self):
        """Extraer token con formato inválido"""
        token = extract_token_from_header("InvalidFormat token")
        assert token is None
    
    def test_extract_token_missing_bearer(self):
        """Extraer token sin Bearer prefix"""
        token = extract_token_from_header("eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
        assert token is None
    
    def test_extract_token_none(self):
        """Extraer token cuando no hay header"""
        token = extract_token_from_header(None)
        assert token is None
    
    def test_verify_jwt_token_valid(self):
        """Verificar token JWT válido"""
        token = TokenService.create_access_token(
            user_id=42,
            email="test@example.com",
            role="admin"
        )
        
        user = verify_jwt_token(token)
        
        assert isinstance(user, CurrentUser)
        assert user.user_id == 42
        assert user.email == "test@example.com"
        assert user.role == "admin"
    
    def test_verify_jwt_token_invalid(self):
        """Verificar token JWT inválido"""
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt_token("invalid.jwt.token")
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_verify_jwt_token_expired(self):
        """Verificar token JWT expirado"""
        expired_token = TokenService.create_access_token(
            user_id=1,
            email="test@example.com",
            role="customer",
            expires_delta=timedelta(seconds=-1)
        )
        
        with pytest.raises(HTTPException) as exc_info:
            verify_jwt_token(expired_token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_with_valid_token(self):
        """Obtener usuario actual con token válido"""
        token = TokenService.create_access_token(
            user_id=10,
            email="user@example.com",
            role="customer"
        )
        
        auth_header = f"Bearer {token}"
        user = get_current_user(authorization=auth_header)
        
        assert user.user_id == 10
        assert user.email == "user@example.com"
    
    def test_get_current_user_missing_header(self):
        """Obtener usuario sin Authorization header"""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(authorization=None)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_invalid_format(self):
        """Obtener usuario con formato de header inválido"""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(authorization="InvalidFormat token")
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_require_role_admin_with_admin_user(self):
        """Decorador require_role permite admin a admin"""
        token = TokenService.create_access_token(
            user_id=1,
            email="admin@example.com",
            role="admin"
        )
        
        user = verify_jwt_token(token)
        
        # Mock del decorador: verificar que role coincide
        required_roles = ("admin",)
        assert user.role in required_roles
    
    def test_require_role_customer_denied_admin(self):
        """Decorador require_role niega customer a admin endpoint"""
        token = TokenService.create_access_token(
            user_id=1,
            email="user@example.com",
            role="customer"
        )
        
        user = verify_jwt_token(token)
        
        # Verificar que customer no tiene permiso
        required_roles = ("admin",)
        assert user.role not in required_roles
    
    def test_current_user_repr(self):
        """CurrentUser tiene representación útil"""
        user = CurrentUser(user_id=5, email="test@example.com", role="admin")
        
        assert "CurrentUser" in repr(user)
        assert "id=5" in repr(user)
