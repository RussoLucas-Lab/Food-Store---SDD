"""
Tests para auth endpoints
"""

import pytest
from fastapi.testclient import TestClient
from datetime import timedelta

from fastapi import FastAPI
from backend.modules.auth.router import router as auth_router
from backend.core.security import TokenService


@pytest.fixture
def client():
    """Provide a fresh test client for each test"""
    app = FastAPI()
    app.include_router(auth_router)
    return TestClient(app)


class TestAuthEndpoints:

    def test_register_success(self, client):
        """Registro exitoso"""
        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePass123!"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["role"] == "customer"
        assert "password_hash" not in data

    def test_register_duplicate_email(self, client):
        """Registro con email duplicado"""
        # Primero registro
        client.post(
            "/auth/register",
            json={
                "email": "dup@example.com",
                "password": "SecurePass123!"
            }
        )

        # Segundo intento con mismo email
        response = client.post(
            "/auth/register",
            json={
                "email": "dup@example.com",
                "password": "DifferentPass456!"
            }
        )

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]

    def test_register_weak_password(self, client):
        """Registro con contraseña débil"""
        response = client.post(
            "/auth/register",
            json={
                "email": "user@example.com",
                "password": "weak"
            }
        )

        assert response.status_code == 422  # Validation error

    def test_login_success(self, client):
        """Login exitoso"""
        email = "logintest@example.com"
        password = "LoginPass123!"

        # Registrar
        client.post(
            "/auth/register",
            json={"email": email, "password": password}
        )

        # Login
        response = client.post(
            "/auth/login",
            json={"email": email, "password": password}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"
        assert data["expires_in"] > 0

    def test_login_wrong_password(self, client):
        """Login con contraseña incorrecta"""
        email = "wrongpwd@example.com"

        # Registrar
        client.post(
            "/auth/register",
            json={"email": email, "password": "CorrectPass123!"}
        )

        # Intentar login con contraseña incorrecta
        response = client.post(
            "/auth/login",
            json={"email": email, "password": "WrongPass456!"}
        )

        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """Login con usuario que no existe"""
        response = client.post(
            "/auth/login",
            json={"email": "nonexistent@example.com", "password": "Pass123!"}
        )

        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_get_me_success(self, client):
        """GET /me con token válido"""
        email = "metest@example.com"
        password = "MePass123!"

        # Registrar
        client.post(
            "/auth/register",
            json={"email": email, "password": password}
        )

        # Login
        login_resp = client.post(
            "/auth/login",
            json={"email": email, "password": password}
        )
        token = login_resp.json()["access_token"]

        # GET /me
        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert "password_hash" not in data

    def test_get_me_missing_token(self, client):
        """GET /me sin token"""
        response = client.get("/auth/me")

        assert response.status_code == 401

    def test_get_me_invalid_token(self, client):
        """GET /me con token inválido"""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token"}
        )

        assert response.status_code == 401

    def test_refresh_token_success(self, client):
        """Refresh token exitoso"""
        email = "refresh@example.com"
        password = "RefreshPass123!"

        # Registrar y login
        client.post(
            "/auth/register",
            json={"email": email, "password": password}
        )

        login_resp = client.post(
            "/auth/login",
            json={"email": email, "password": password}
        )
        refresh_token = login_resp.json()["refresh_token"]

        # Refresh
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": refresh_token}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["refresh_token"] == refresh_token

    def test_refresh_token_invalid(self, client):
        """Refresh con token inválido"""
        response = client.post(
            "/auth/refresh",
            json={"refresh_token": "invalid.token"}
        )

        assert response.status_code == 401

    def test_logout_success(self, client):
        """Logout exitoso"""
        email = "logout@example.com"
        password = "LogoutPass123!"

        # Registrar y login
        client.post(
            "/auth/register",
            json={"email": email, "password": password}
        )

        login_resp = client.post(
            "/auth/login",
            json={"email": email, "password": password}
        )
        token = login_resp.json()["access_token"]

        # Logout
        response = client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        assert "Logged out" in response.json()["message"]

    def test_logout_missing_token(self, client):
        """Logout sin token"""
        response = client.post("/auth/logout")
        assert response.status_code == 401
