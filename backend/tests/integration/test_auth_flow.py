"""
Tests de integración — Flujo de autenticación.

Prueba el flujo completo de registro, login y acceso a endpoints protegidos
usando TestClient(app) con el UoW in-memory.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.mark.integration
class TestAuthFlow:
    """Flujo de autenticación de punta a punta."""

    # ─────────────────────────────────────────────────────────────────────────
    # 5.2 — POST /auth/register con datos válidos → 201
    # ─────────────────────────────────────────────────────────────────────────

    def test_register_valid_user_returns_201(self, client):
        """POST /auth/register con datos válidos → 201 + user data."""
        response = client.post(
            "/auth/register",
            json={
                "email": "nuevo@foodstore.com",
                "password": "SecurePass1!"
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "nuevo@foodstore.com"
        assert "id" in data
        assert "role" in data

    def test_register_duplicate_email_returns_400(self, client):
        """POST /auth/register con email duplicado → 400."""
        payload = {"email": "dup@foodstore.com", "password": "SecurePass1!"}
        client.post("/auth/register", json=payload)

        response = client.post("/auth/register", json=payload)

        assert response.status_code == 400

    def test_register_weak_password_returns_422(self, client):
        """POST /auth/register con contraseña débil → 422."""
        response = client.post(
            "/auth/register",
            json={"email": "user@foodstore.com", "password": "weak"}
        )

        assert response.status_code == 422

    # ─────────────────────────────────────────────────────────────────────────
    # 5.3 — POST /auth/login con credenciales válidas → access_token + refresh_token
    # ─────────────────────────────────────────────────────────────────────────

    def test_login_valid_credentials_returns_tokens(self, client):
        """POST /auth/login con credenciales válidas → access_token y refresh_token."""
        # Registrar usuario primero
        client.post(
            "/auth/register",
            json={"email": "login@foodstore.com", "password": "SecurePass1!"}
        )

        response = client.post(
            "/auth/login",
            json={"email": "login@foodstore.com", "password": "SecurePass1!"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "Bearer"

    def test_login_wrong_password_returns_401(self, client):
        """POST /auth/login con contraseña incorrecta → 401."""
        client.post(
            "/auth/register",
            json={"email": "badpass@foodstore.com", "password": "SecurePass1!"}
        )

        response = client.post(
            "/auth/login",
            json={"email": "badpass@foodstore.com", "password": "WrongPass1!"}
        )

        assert response.status_code == 401

    def test_login_nonexistent_email_returns_401(self, client):
        """POST /auth/login con email inexistente → 401."""
        response = client.post(
            "/auth/login",
            json={"email": "noexiste@foodstore.com", "password": "SecurePass1!"}
        )

        assert response.status_code == 401

    # ─────────────────────────────────────────────────────────────────────────
    # 5.4 — endpoint protegido sin Authorization header → 401
    # ─────────────────────────────────────────────────────────────────────────

    def test_protected_endpoint_no_auth_returns_401(self, client):
        """GET /auth/me sin token → 401."""
        response = client.get("/auth/me")

        assert response.status_code == 401

    # ─────────────────────────────────────────────────────────────────────────
    # 5.5 — endpoint protegido con Bearer token válido → 200
    # ─────────────────────────────────────────────────────────────────────────

    def test_protected_endpoint_with_valid_token_returns_200(self, client):
        """GET /auth/me con token válido → 200."""
        # Registrar y loguear
        client.post(
            "/auth/register",
            json={"email": "protected@foodstore.com", "password": "SecurePass1!"}
        )
        login_resp = client.post(
            "/auth/login",
            json={"email": "protected@foodstore.com", "password": "SecurePass1!"}
        )
        access_token = login_resp.json()["access_token"]

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "protected@foodstore.com"

    def test_protected_endpoint_with_invalid_token_returns_401(self, client):
        """GET /auth/me con token inválido → 401."""
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer token.invalido.xyz"}
        )

        assert response.status_code == 401
