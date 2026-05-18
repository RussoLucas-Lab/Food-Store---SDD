"""
Tests de integración para endpoints de Cliente.

Migrado desde backend/tests/test_cliente_endpoints.py.
Prueba los endpoints HTTP completos: validación, auth, mappeo de errores a HTTP.

Usa el test_uow provisto por el fixture autouse override_get_uow (conftest.py).
Los datos se pre-populan directamente en el repositorio en memoria en lugar de
usar patch sobre atributos de módulo que ya no existen (post-refactor DI).
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """Fixture: TestClient para FastAPI"""
    return TestClient(app)


@pytest.fixture
def mock_admin_token():
    """Token JWT real con rol ADMIN"""
    from backend.core.security import TokenService
    token = TokenService.create_access_token(user_id=1, email="admin@test.com", role="admin")
    return f"Bearer {token}"


@pytest.fixture
def mock_user_token():
    """Token JWT real con rol customer"""
    from backend.core.security import TokenService
    token = TokenService.create_access_token(user_id=2, email="user@test.com", role="customer")
    return f"Bearer {token}"


class TestCreateCliente:
    """Tests para POST /clientes"""

    def test_create_cliente_admin_success(self, client, mock_admin_token, override_get_uow):
        """ADMIN crea cliente exitosamente → 201"""
        response = client.post(
            "/clientes",
            json={
                "nombre": "Juan Perez",
                "email": "juan@example.com",
                "telefono": "555-1234",
                "direccion": "Calle 123, Apt 4"
            },
            headers={"Authorization": mock_admin_token}
        )

        assert response.status_code == 201
        assert response.json()["email"] == "juan@example.com"

    def test_create_cliente_duplicate_email(self, client, mock_admin_token, override_get_uow):
        """Email duplicado → 409"""
        # Pre-populate repo con el email que queremos duplicar
        override_get_uow.clientes.create(
            nombre="Existing User",
            email="juan@example.com",
            direccion="Calle Existente 1"
        )

        response = client.post(
            "/clientes",
            json={
                "nombre": "Juan Perez",
                "email": "juan@example.com",
                "telefono": "555-1234",
                "direccion": "Calle 123, Apt 4"
            },
            headers={"Authorization": mock_admin_token}
        )

        assert response.status_code == 409

    def test_create_cliente_invalid_email(self, client, mock_admin_token):
        """Email inválido → 422"""
        response = client.post(
            "/clientes",
            json={
                "nombre": "Juan Perez",
                "email": "not-an-email",
                "telefono": "555-1234",
                "direccion": "Calle 123, Apt 4"
            },
            headers={"Authorization": mock_admin_token}
        )

        assert response.status_code == 422  # Validation error

    def test_create_cliente_user_forbidden(self, client, mock_user_token):
        """USER (rol 'customer') intenta crear → 403 (rechazado por middleware)"""
        response = client.post(
            "/clientes",
            json={
                "nombre": "Juan Perez",
                "email": "juan@example.com",
                "telefono": "555-1234",
                "direccion": "Calle 123, Apt 4"
            },
            headers={"Authorization": mock_user_token}
        )

        assert response.status_code == 403


class TestGetClienteList:
    """Tests para GET /clientes"""

    def test_list_clientes_admin(self, client, mock_admin_token, override_get_uow):
        """ADMIN obtiene lista completa → 200"""
        override_get_uow.clientes.create(
            nombre="Cliente Uno",
            email="cliente1@example.com",
            direccion="Address 1"
        )

        response = client.get(
            "/clientes",
            headers={"Authorization": mock_admin_token}
        )

        assert response.status_code == 200
        assert "items" in response.json()

    def test_list_clientes_pagination(self, client, mock_admin_token, override_get_uow):
        """Paginación funciona → 200 con skip/limit"""
        override_get_uow.clientes.create(
            nombre="Cliente Uno",
            email="cliente1@example.com",
            direccion="Address 1"
        )

        response = client.get(
            "/clientes?skip=0&limit=10",
            headers={"Authorization": mock_admin_token}
        )

        assert response.status_code == 200
        assert "items" in response.json()


class TestGetCliente:
    """Tests para GET /clientes/{id}"""

    def test_get_cliente_admin(self, client, mock_admin_token, override_get_uow):
        """ADMIN obtiene cliente → 200"""
        override_get_uow.clientes.create(
            nombre="Juan Perez",
            email="juan@example.com",
            direccion="Calle 123"
        )

        # user_role=ADMIN so the service allows viewing any client
        response = client.get(
            "/clientes/1?user_role=ADMIN",
            headers={"Authorization": mock_admin_token}
        )

        assert response.status_code == 200
        assert response.json()["id"] == 1

    def test_get_cliente_not_found(self, client, mock_admin_token):
        """Cliente no existe → 404"""
        # user_role=ADMIN so the service skips the ownership check and raises 404
        response = client.get(
            "/clientes/999?user_role=ADMIN",
            headers={"Authorization": mock_admin_token}
        )

        assert response.status_code == 404


class TestUpdateCliente:
    """Tests para PATCH /clientes/{id}"""

    def test_update_cliente_admin(self, client, mock_admin_token, override_get_uow):
        """ADMIN actualiza cliente → 200"""
        override_get_uow.clientes.create(
            nombre="Juan Perez",
            email="juan@example.com",
            direccion="Calle 123"
        )

        response = client.patch(
            "/clientes/1",
            json={"nombre": "Juan Updated"},
            headers={"Authorization": mock_admin_token}
        )

        assert response.status_code == 200
        assert response.json()["nombre"] == "Juan Updated"

    def test_update_cliente_duplicate_email(self, client, mock_admin_token, override_get_uow):
        """Email duplicado → 409"""
        override_get_uow.clientes.create(
            nombre="Cliente Uno",
            email="juan@example.com",
            direccion="Address 1"
        )
        override_get_uow.clientes.create(
            nombre="Cliente Dos",
            email="taken@example.com",
            direccion="Address 2"
        )

        response = client.patch(
            "/clientes/1",
            json={"email": "taken@example.com"},
            headers={"Authorization": mock_admin_token}
        )

        assert response.status_code == 409


class TestDeleteCliente:
    """Tests para DELETE /clientes/{id}"""

    def test_delete_cliente_admin(self, client, mock_admin_token, override_get_uow):
        """ADMIN soft-deleta cliente → 204"""
        override_get_uow.clientes.create(
            nombre="Juan Perez",
            email="juan@example.com",
            direccion="Calle 123"
        )

        response = client.delete(
            "/clientes/1",
            headers={"Authorization": mock_admin_token}
        )

        assert response.status_code == 204

    def test_delete_cliente_user_forbidden(self, client, mock_user_token):
        """USER (rol 'customer') intenta eliminar → 403 (rechazado por middleware)"""
        response = client.delete(
            "/clientes/1",
            headers={"Authorization": mock_user_token}
        )

        assert response.status_code == 403


class TestSearchClientes:
    """Tests para GET /clientes/search"""

    def test_search_clientes_admin(self, client, mock_admin_token, override_get_uow):
        """ADMIN busca clientes → 200"""
        override_get_uow.clientes.create(
            nombre="Juan Perez",
            email="juan@example.com",
            direccion="Calle 123"
        )

        response = client.get(
            "/clientes/search?q=Juan",
            headers={"Authorization": mock_admin_token}
        )

        assert response.status_code == 200
        assert len(response.json()["items"]) == 1

    def test_search_clientes_empty_query(self, client, mock_admin_token):
        """Búsqueda vacía → 422"""
        response = client.get(
            "/clientes/search",
            headers={"Authorization": mock_admin_token}
        )

        assert response.status_code == 422  # Validation error (q is required)


class TestReactivateCliente:
    """Tests para PATCH /clientes/{id}/reactivar"""

    def test_reactivate_cliente_admin(self, client, mock_admin_token, override_get_uow):
        """ADMIN reactiva cliente → 200"""
        # Crear y luego soft-delete para que esté inactivo
        override_get_uow.clientes.create(
            nombre="Juan Perez",
            email="juan@example.com",
            direccion="Calle 123"
        )
        override_get_uow.clientes.soft_delete(1)

        response = client.patch(
            "/clientes/1/reactivar",
            headers={"Authorization": mock_admin_token}
        )

        assert response.status_code == 200
        assert response.json()["activo"] is True

    def test_reactivate_cliente_user_forbidden(self, client, mock_user_token):
        """USER (rol 'customer') intenta reactivar → 403 (rechazado por middleware)"""
        response = client.patch(
            "/clientes/1/reactivar",
            headers={"Authorization": mock_user_token}
        )

        assert response.status_code == 403
