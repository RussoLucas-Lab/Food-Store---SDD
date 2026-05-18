"""
Tests para Pydantic schemas de auth
"""

import pytest
from pydantic import ValidationError
from backend.modules.auth.schemas import (
    RegisterRequest, LoginRequest, RefreshRequest, TokenResponse, UserOut, UserCreate
)


class TestAuthSchemas:

    def test_register_request_valid(self):
        """RegisterRequest válido"""
        req = RegisterRequest(
            email="newuser@example.com",
            password="SecurePass123!"
        )
        assert req.email == "newuser@example.com"
        assert req.password == "SecurePass123!"

    def test_register_request_invalid_email(self):
        """RegisterRequest con email inválido"""
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="invalid-email",
                password="SecurePass123!"
            )

    def test_register_request_weak_password(self):
        """RegisterRequest con contraseña débil"""
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="user@example.com",
                password="weak"  # No cumple requisitos
            )

    def test_register_request_missing_special_char(self):
        """RegisterRequest sin carácter especial"""
        with pytest.raises(ValidationError):
            RegisterRequest(
                email="user@example.com",
                password="SecurePass123"  # Sin especial
            )

    def test_login_request_valid(self):
        """LoginRequest válido"""
        req = LoginRequest(
            email="user@example.com",
            password="SecurePass123!"
        )
        assert req.email == "user@example.com"

    def test_login_request_invalid_email(self):
        """LoginRequest con email inválido"""
        with pytest.raises(ValidationError):
            LoginRequest(
                email="not-an-email",
                password="SecurePass123!"
            )

    def test_refresh_request_valid(self):
        """RefreshRequest válido"""
        req = RefreshRequest(refresh_token="some.jwt.token")
        assert req.refresh_token == "some.jwt.token"

    def test_token_response_valid(self):
        """TokenResponse válido"""
        resp = TokenResponse(
            access_token="access.jwt.token",
            refresh_token="refresh.jwt.token",
            expires_in=900
        )
        assert resp.token_type == "Bearer"
        assert resp.expires_in == 900

    def test_user_out_valid(self):
        """UserOut válido sin password_hash"""
        from datetime import datetime
        now = datetime.utcnow()
        user = UserOut(
            id=1,
            email="user@example.com",
            role="customer",
            is_active=True,
            created_at=now,
            updated_at=now
        )
        assert user.id == 1
        assert not hasattr(user, 'password_hash')

    def test_user_create_valid(self):
        """UserCreate válido"""
        uc = UserCreate(
            email="newadmin@example.com",
            password="AdminPass123!",
            role="admin"
        )
        assert uc.role == "admin"

    def test_user_create_invalid_role(self):
        """UserCreate con rol inválido"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="user@example.com",
                password="SecurePass123!",
                role="superadmin"  # Inválido
            )

    def test_user_create_weak_password(self):
        """UserCreate con contraseña débil"""
        with pytest.raises(ValidationError):
            UserCreate(
                email="user@example.com",
                password="weak"  # Débil
            )
