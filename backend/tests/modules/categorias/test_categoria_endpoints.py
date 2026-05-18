"""
Tests de integración para endpoints de Categorías.

Migrado desde backend/tests/test_categoria_endpoints.py.
Prueba los endpoints REST completos con el UoW real (in-memory).
Verifica que los routers mapeen correctamente excepciones a HTTP status.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.uow_inmemory import InMemoryUnitOfWork


@pytest.fixture
def client():
    """Fixture: TestClient para FastAPI"""
    return TestClient(app)


@pytest.fixture
def uow():
    """Fixture: Unit of Work real (in-memory)"""
    return InMemoryUnitOfWork()


@pytest.fixture
def admin_headers():
    """Fixture: Headers con token admin válido (JWT real)"""
    from backend.core.security import TokenService
    token = TokenService.create_access_token(user_id=1, email="admin@test.com", role="admin")
    return {"Authorization": f"Bearer {token}"}


class TestCreateCategoriaEndpoint:
    """Tests para POST /categorias"""

    def test_post_categorias_valid(self, client, admin_headers):
        """POST /categorias con datos válidos → 201"""
        response = client.post(
            "/categorias",
            json={"nombre": "Frutas", "descripcion": "Frutas frescas"},
            headers=admin_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Frutas"
        assert data["is_active"] is True

    def test_post_categorias_duplicate_name(self, client, admin_headers):
        """POST /categorias con nombre duplicado → 409 Conflict"""
        client.post(
            "/categorias",
            json={"nombre": "Frutas", "descripcion": "desc"},
            headers=admin_headers
        )

        response = client.post(
            "/categorias",
            json={"nombre": "Frutas", "descripcion": "otra"},
            headers=admin_headers
        )

        assert response.status_code == 409
        assert "ya existe" in response.json()["detail"]

    def test_post_categorias_empty_name(self, client, admin_headers):
        """POST /categorias con nombre vacío → 400/422"""
        response = client.post(
            "/categorias",
            json={"nombre": "", "descripcion": "desc"},
            headers=admin_headers
        )

        # Pydantic catches min_length=1 at schema level → 422,
        # or service catches empty string → 400
        assert response.status_code in [400, 422]

    def test_post_categorias_no_auth(self, client):
        """POST /categorias sin autenticación → 403 Forbidden"""
        response = client.post(
            "/categorias",
            json={"nombre": "Frutas", "descripcion": "desc"}
        )

        assert response.status_code in [401, 403]


class TestListCategoriasEndpoint:
    """Tests para GET /categorias"""

    def test_get_categorias_list(self, client):
        """GET /categorias → 200 con lista"""
        response = client.get("/categorias")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data

    def test_get_categorias_pagination(self, client, admin_headers):
        """GET /categorias?skip=0&limit=10 respeta paginación"""
        for i in range(3):
            client.post(
                "/categorias",
                json={"nombre": f"Cat{i}", "descripcion": f"desc{i}"},
                headers=admin_headers
            )

        response = client.get("/categorias?skip=0&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 2


class TestGetCategoriaEndpoint:
    """Tests para GET /categorias/{id}"""

    def test_get_categoria_valid(self, client, admin_headers):
        """GET /categorias/{id} válido → 200 con DTO"""
        create_resp = client.post(
            "/categorias",
            json={"nombre": "Frutas", "descripcion": "desc"},
            headers=admin_headers
        )
        cat_id = create_resp.json()["id"]

        response = client.get(f"/categorias/{cat_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == cat_id
        assert data["nombre"] == "Frutas"

    def test_get_categoria_not_found(self, client):
        """GET /categorias/{id} no existe → 404 Not Found"""
        response = client.get("/categorias/9999")

        assert response.status_code == 404


class TestUpdateCategoriaEndpoint:
    """Tests para PUT /categorias/{id}"""

    def test_put_categoria_valid(self, client, admin_headers):
        """PUT /categorias/{id} válido → 200 actualizado"""
        create_resp = client.post(
            "/categorias",
            json={"nombre": "Frutas", "descripcion": "original"},
            headers=admin_headers
        )
        cat_id = create_resp.json()["id"]

        response = client.put(
            f"/categorias/{cat_id}",
            json={"nombre": "Frutas Cítricas", "descripcion": "updated"},
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Frutas Cítricas"

    def test_put_categoria_not_found(self, client, admin_headers):
        """PUT /categorias/{id} no existe → 404"""
        response = client.put(
            "/categorias/9999",
            json={"nombre": "NewName"},
            headers=admin_headers
        )

        assert response.status_code == 404

    def test_put_categoria_duplicate_name(self, client, admin_headers):
        """PUT /categorias/{id} nombre duplicado → 409"""
        resp1 = client.post(
            "/categorias",
            json={"nombre": "Frutas", "descripcion": "desc"},
            headers=admin_headers
        )
        cat1_id = resp1.json()["id"]

        client.post(
            "/categorias",
            json={"nombre": "Verduras", "descripcion": "desc"},
            headers=admin_headers
        )

        response = client.put(
            f"/categorias/{cat1_id}",
            json={"nombre": "Verduras"},
            headers=admin_headers
        )

        assert response.status_code == 409


class TestDeleteCategoriaEndpoint:
    """Tests para DELETE /categorias/{id}"""

    def test_delete_categoria_not_in_use(self, client, admin_headers):
        """DELETE /categorias/{id} no en uso → 204"""
        create_resp = client.post(
            "/categorias",
            json={"nombre": "Frutas", "descripcion": "desc"},
            headers=admin_headers
        )
        cat_id = create_resp.json()["id"]

        response = client.delete(
            f"/categorias/{cat_id}",
            headers=admin_headers
        )

        assert response.status_code == 204

    def test_delete_categoria_not_found(self, client, admin_headers):
        """DELETE /categorias/{id} no existe → 404"""
        response = client.delete(
            "/categorias/9999",
            headers=admin_headers
        )

        assert response.status_code == 404

    def test_delete_categoria_no_auth(self, client, admin_headers):
        """DELETE /categorias/{id} sin admin → 403"""
        create_resp = client.post(
            "/categorias",
            json={"nombre": "Frutas", "descripcion": "desc"},
            headers=admin_headers
        )
        cat_id = create_resp.json()["id"]

        response = client.delete(f"/categorias/{cat_id}")

        assert response.status_code in [401, 403]
