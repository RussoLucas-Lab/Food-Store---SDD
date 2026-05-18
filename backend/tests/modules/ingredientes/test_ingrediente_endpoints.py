"""
Tests de integración para endpoints de Ingredientes.

Migrado y consolidado desde:
- tests/test_ingrediente_endpoints.py (sin auth)
- backend/tests/test_ingrediente_endpoints.py (con auth completo)

Verifica que los endpoints REST funcionen correctamente con UoW real.
"""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.main import app as main_app
from backend.modules.ingredientes.router import router as ingredientes_router
from backend.modules.ingredientes.repository import InMemoryIngredienteRepository


@pytest.fixture
def client():
    """Fixture: TestClient para FastAPI (app completa)"""
    return TestClient(main_app)


@pytest.fixture
def admin_headers():
    """Fixture: Headers con token admin (JWT real)"""
    from backend.core.security import TokenService
    token = TokenService.create_access_token(user_id=1, email="admin@test.com", role="admin")
    return {"Authorization": f"Bearer {token}"}


# --- Tests con app completa (con auth) ---

class TestCreateIngredienteEndpoint:
    """Tests para POST /ingredientes"""

    def test_post_ingredientes_valid(self, client, admin_headers):
        """POST /ingredientes válido → 201"""
        response = client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "gramos",
                "cantidad_stock": 100,
                "cantidad_minima": 10,
                "descripcion": "Harina blanca"
            },
            headers=admin_headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Harina"
        assert data["unidad_medida"] == "gramos"

    def test_post_ingredientes_duplicate(self, client, admin_headers):
        """POST /ingredientes nombre duplicado → 409"""
        client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "gramos",
                "cantidad_stock": 100,
                "cantidad_minima": 10
            },
            headers=admin_headers
        )

        response = client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "litros",
                "cantidad_stock": 50,
                "cantidad_minima": 5
            },
            headers=admin_headers
        )

        assert response.status_code == 409

    def test_post_ingredientes_invalid_unidad(self, client, admin_headers):
        """POST /ingredientes unidad inválida → 422 (Pydantic enum validation)"""
        response = client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "toneladas",
                "cantidad_stock": 100,
                "cantidad_minima": 10
            },
            headers=admin_headers
        )

        # Pydantic catches invalid enum at schema level → 422
        assert response.status_code in [400, 422]

    def test_post_ingredientes_negative_stock(self, client, admin_headers):
        """POST /ingredientes stock negativo → 422 (Pydantic ge=0 validation)"""
        response = client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "gramos",
                "cantidad_stock": -50,
                "cantidad_minima": 10
            },
            headers=admin_headers
        )

        # Pydantic catches negative stock at schema level → 422
        assert response.status_code in [400, 422]


class TestListIngredientesEndpoint:
    """Tests para GET /ingredientes"""

    def test_get_ingredientes_list(self, client):
        """GET /ingredientes → 200"""
        response = client.get("/ingredientes")

        assert response.status_code == 200
        data = response.json()
        assert "ingredientes" in data or "items" in data

    def test_get_ingredientes_with_filters(self, client, admin_headers):
        """GET /ingredientes con filtros"""
        client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "gramos",
                "cantidad_stock": 100,
                "cantidad_minima": 10
            },
            headers=admin_headers
        )

        response = client.get("/ingredientes?unidad_medida=gramos")

        assert response.status_code == 200


class TestGetIngredienteEndpoint:
    """Tests para GET /ingredientes/{id}"""

    def test_get_ingrediente_valid(self, client, admin_headers):
        """GET /ingredientes/{id} válido → 200"""
        create_resp = client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "gramos",
                "cantidad_stock": 100,
                "cantidad_minima": 10
            },
            headers=admin_headers
        )
        ing_id = create_resp.json()["id"]

        response = client.get(f"/ingredientes/{ing_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ing_id

    def test_get_ingrediente_not_found(self, client):
        """GET /ingredientes/{id} no existe → 404"""
        response = client.get("/ingredientes/9999")

        assert response.status_code == 404


class TestUpdateIngredienteEndpoint:
    """Tests para PUT /ingredientes/{id}"""

    def test_put_ingrediente_valid(self, client, admin_headers):
        """PUT /ingredientes/{id} válido → 200"""
        create_resp = client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "gramos",
                "cantidad_stock": 100,
                "cantidad_minima": 10
            },
            headers=admin_headers
        )
        ing_id = create_resp.json()["id"]

        response = client.put(
            f"/ingredientes/{ing_id}",
            json={"cantidad_stock": 200},
            headers=admin_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["cantidad_stock"] == 200

    def test_put_ingrediente_not_found(self, client, admin_headers):
        """PUT /ingredientes/{id} no existe → 404"""
        response = client.put(
            "/ingredientes/9999",
            json={"cantidad_stock": 200},
            headers=admin_headers
        )

        assert response.status_code == 404


class TestDeleteIngredienteEndpoint:
    """Tests para DELETE /ingredientes/{id}"""

    def test_delete_ingrediente_valid(self, client, admin_headers):
        """DELETE /ingredientes/{id} → 204"""
        create_resp = client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "gramos",
                "cantidad_stock": 100,
                "cantidad_minima": 10
            },
            headers=admin_headers
        )
        ing_id = create_resp.json()["id"]

        response = client.delete(
            f"/ingredientes/{ing_id}",
            headers=admin_headers
        )

        assert response.status_code == 204

    def test_delete_ingrediente_not_found(self, client, admin_headers):
        """DELETE /ingredientes/{id} no existe → 404"""
        response = client.delete(
            "/ingredientes/9999",
            headers=admin_headers
        )

        assert response.status_code == 404


# --- Tests básicos sin auth complejo ---

@pytest.fixture
def simple_app():
    """App simple sin auth middleware"""
    app = FastAPI()
    app.include_router(ingredientes_router)
    return app


@pytest.fixture
def simple_client(simple_app):
    """Test client simple"""
    return TestClient(simple_app)


class TestIngredientesEndpointsBasic:
    """Test basic endpoint functionality without complex auth"""

    def test_list_empty(self, simple_client):
        """GET /ingredientes returns empty list"""
        response = simple_client.get("/ingredientes")
        assert response.status_code == 200
        data = response.json()
        assert len(data["ingredientes"]) == 0
        assert data["total"] == 0

    def test_search_empty(self, simple_client):
        """GET /ingredientes/buscar with no ingredientes"""
        response = simple_client.get("/ingredientes/buscar?q=test")
        assert response.status_code == 200
        data = response.json()
        assert len(data["ingredientes"]) == 0

    def test_search_missing_query(self, simple_client):
        """GET /ingredientes/buscar without q parameter fails"""
        response = simple_client.get("/ingredientes/buscar")
        assert response.status_code == 422  # Validation error

    def test_get_not_found(self, simple_client):
        """GET /ingredientes/{id} for non-existent returns 404"""
        response = simple_client.get("/ingredientes/999")
        assert response.status_code == 404

    def test_list_response_structure(self, simple_client):
        """GET /ingredientes response has required fields"""
        response = simple_client.get("/ingredientes")
        data = response.json()

        assert "ingredientes" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data

    def test_pagination_skip_limit(self, simple_client):
        """Test skip and limit parameters"""
        response = simple_client.get("/ingredientes?skip=0&limit=50")
        assert response.status_code == 200
        data = response.json()
        assert data["skip"] == 0
        assert data["limit"] == 50

    def test_pagination_default_values(self, simple_client):
        """Test default pagination values"""
        response = simple_client.get("/ingredientes")
        data = response.json()
        assert data["skip"] == 0
        assert data["limit"] == 20
