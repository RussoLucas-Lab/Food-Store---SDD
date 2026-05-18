"""
Tests de integración para:
- Login con cuenta desactivada → HTTP 403
- Login con cuenta activa → HTTP 200
- Login con cuenta reactivada → HTTP 200
- RBAC ampliado: ADMIN accede a catálogo y pedidos
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
    """Fixture: headers con token de admin real creado en el sistema."""
    # Registrar un admin real para que tenga ID en el sistema
    reg = client.post("/auth/register", json={
        "email": "sysadmin@test.com",
        "password": "SysAdmin1234!"
    })
    admin_id = reg.json().get("id", 9999)
    # Crear token con el ID real del admin
    token = TokenService.create_access_token(
        user_id=admin_id, email="sysadmin@test.com", role="ADMIN"
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers_cased():
    """Admin token con role ADMIN (para rutas que esperan 'ADMIN')."""
    token = TokenService.create_access_token(user_id=99, email="adminlow@test.com", role="ADMIN")
    return {"Authorization": f"Bearer {token}"}


class TestLoginCuentaDesactivada:
    """Login rechaza usuarios inactivos con HTTP 403."""

    def test_cuenta_activa_permite_login(self, client):
        # Registrar usuario activo
        client.post("/auth/register", json={
            "email": "active_user@test.com",
            "password": "Active1234!"
        })
        response = client.post("/auth/login", json={
            "email": "active_user@test.com",
            "password": "Active1234!"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_cuenta_desactivada_retorna_403(self, client, admin_headers):
        # Registrar usuario
        reg = client.post("/auth/register", json={
            "email": "inactive_login@test.com",
            "password": "Inactive1234!"
        })
        user_id = reg.json()["id"]

        # Desactivar la cuenta
        client.patch(
            f"/api/v1/admin/usuarios/{user_id}/activo",
            json={"activo": False},
            headers=admin_headers
        )

        # Intentar login
        response = client.post("/auth/login", json={
            "email": "inactive_login@test.com",
            "password": "Inactive1234!"
        })
        assert response.status_code == 403
        assert "access_token" not in response.json()

    def test_cuenta_reactivada_permite_login(self, client, admin_headers):
        # Registrar, desactivar y reactivar
        reg = client.post("/auth/register", json={
            "email": "reactiv@test.com",
            "password": "Reactiv1234!"
        })
        user_id = reg.json()["id"]

        client.patch(
            f"/api/v1/admin/usuarios/{user_id}/activo",
            json={"activo": False},
            headers=admin_headers
        )
        client.patch(
            f"/api/v1/admin/usuarios/{user_id}/activo",
            json={"activo": True},
            headers=admin_headers
        )

        response = client.post("/auth/login", json={
            "email": "reactiv@test.com",
            "password": "Reactiv1234!"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()


class TestRBACAmpliado:
    """ADMIN accede a endpoints de catálogo y pedidos."""

    def test_admin_puede_crear_categoria(self, client, admin_headers_cased):
        response = client.post(
            "/categorias",
            json={"nombre": "CatAdmin", "descripcion": "test"},
            headers=admin_headers_cased
        )
        assert response.status_code == 201

    def test_admin_puede_listar_pedidos_gestion(self, client, admin_headers_cased):
        response = client.get(
            "/api/v1/pedidos/gestion",
            headers=admin_headers_cased
        )
        assert response.status_code == 200
