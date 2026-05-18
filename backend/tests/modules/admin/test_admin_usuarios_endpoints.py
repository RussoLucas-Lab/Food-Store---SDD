"""
Tests de integración para endpoints de gestión de usuarios del admin.

Verifica:
- Listado paginado sin contraseñas
- Edición de datos/roles
- Activación/desactivación
- HTTP 403 para no-ADMIN
- HTTP 404 usuario inexistente
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.security import TokenService


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_headers(client):
    """Fixture: headers con token de admin real (con ID real en el sistema)."""
    reg = client.post("/auth/register", json={
        "email": "sysadmin_u@test.com",
        "password": "SysAdmin1234!"
    })
    admin_id = reg.json().get("id", 9999)
    token = TokenService.create_access_token(
        user_id=admin_id, email="sysadmin_u@test.com", role="ADMIN"
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client_headers():
    token = TokenService.create_access_token(user_id=2, email="client@test.com", role="customer")
    return {"Authorization": f"Bearer {token}"}


class TestListadoUsuarios:
    """Tests para GET /api/v1/admin/usuarios"""

    def test_admin_lista_usuarios(self, client, admin_headers):
        response = client.get("/api/v1/admin/usuarios", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data

    def test_respuesta_no_contiene_passwords(self, client, admin_headers):
        # Crear usuario primero
        client.post("/auth/register", json={"email": "test_user@test.com", "password": "Test1234!"})
        response = client.get("/api/v1/admin/usuarios", headers=admin_headers)
        assert response.status_code == 200
        for item in response.json()["items"]:
            assert "password_hash" not in item
            assert "password" not in item

    def test_no_admin_retorna_403(self, client, client_headers):
        response = client.get("/api/v1/admin/usuarios", headers=client_headers)
        assert response.status_code == 403

    def test_sin_token_retorna_401(self, client):
        response = client.get("/api/v1/admin/usuarios")
        assert response.status_code == 401

    def test_paginacion_funciona(self, client, admin_headers):
        response = client.get("/api/v1/admin/usuarios?page=1&size=5", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 5


class TestEditarUsuario:
    """Tests para PATCH /api/v1/admin/usuarios/{id}"""

    def test_usuario_inexistente_retorna_404(self, client, admin_headers):
        response = client.patch(
            "/api/v1/admin/usuarios/99999",
            json={"nombre": "nuevo nombre"},
            headers=admin_headers
        )
        assert response.status_code == 404

    def test_rol_invalido_retorna_422(self, client, admin_headers):
        # Crear un usuario
        reg = client.post("/auth/register", json={"email": "editme@test.com", "password": "Test1234!"})
        user_id = reg.json()["id"]
        response = client.patch(
            f"/api/v1/admin/usuarios/{user_id}",
            json={"role": "SUPERADMIN"},
            headers=admin_headers
        )
        assert response.status_code == 422

    def test_no_admin_retorna_403(self, client, client_headers):
        response = client.patch(
            "/api/v1/admin/usuarios/1",
            json={"nombre": "test"},
            headers=client_headers
        )
        assert response.status_code == 403


class TestToggleActivo:
    """Tests para PATCH /api/v1/admin/usuarios/{id}/activo"""

    def test_usuario_inexistente_retorna_404(self, client, admin_headers):
        response = client.patch(
            "/api/v1/admin/usuarios/99999/activo",
            json={"activo": False},
            headers=admin_headers
        )
        assert response.status_code == 404

    def test_no_admin_retorna_403(self, client, client_headers):
        response = client.patch(
            "/api/v1/admin/usuarios/1/activo",
            json={"activo": False},
            headers=client_headers
        )
        assert response.status_code == 403

    def test_activar_usuario_inactivo(self, client, admin_headers):
        # Registrar usuario y obtener ID
        reg = client.post("/auth/register", json={"email": "toggleme@test.com", "password": "Test1234!"})
        user_id = reg.json()["id"]
        # Desactivar: habrá al menos un admin en el sistema, así que esto debe funcionar
        # para el usuario customer
        response = client.patch(
            f"/api/v1/admin/usuarios/{user_id}/activo",
            json={"activo": False},
            headers=admin_headers
        )
        # El usuario registrado con /auth/register tiene rol "customer" — puede desactivarse
        assert response.status_code == 200
        assert response.json()["is_active"] is False
