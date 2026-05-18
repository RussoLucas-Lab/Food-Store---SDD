"""
Tests de endpoints para el módulo productos.

Prueba los endpoints REST completos con el UoW real (in-memory).
Verifica que los routers mapeen correctamente las respuestas HTTP.
"""

import pytest
from unittest.mock import Mock
from fastapi.testclient import TestClient
from backend.main import app


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """Fixture: TestClient para FastAPI."""
    return TestClient(app)


@pytest.fixture
def admin_headers():
    """Fixture: Headers con token admin válido."""
    from backend.core.security import TokenService
    token = TokenService.create_access_token(user_id=1, email="admin@test.com", role="admin")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client_headers():
    """Fixture: Headers con token de cliente."""
    from backend.core.security import TokenService
    token = TokenService.create_access_token(user_id=2, email="user@test.com", role="client")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def seed_productos_uow():
    """
    Precargar categoría e ingrediente en el UoW del router de productos.

    El router de productos tiene su propia InMemoryUnitOfWork independiente
    de las de categorías e ingredientes. Se necesita seedear directamente.
    """
    import backend.modules.productos.router as prod_router_mod
    from backend.modules.categorias.model import Categoria
    from backend.modules.ingredientes.model import Ingrediente
    from datetime import datetime

    prod_uow = prod_router_mod.uow

    # Crear categoría de prueba en el UoW de productos
    cat = Categoria(
        id=1,
        nombre="Test Cat Seeded",
        descripcion="desc",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    prod_uow._categorias._storage[1] = cat
    prod_uow._categorias._next_id = 2
    prod_uow._categorias._name_index["test cat seeded"] = 1

    # Crear ingrediente de prueba en el UoW de productos
    ing = Ingrediente(
        id=1,
        nombre="Test Ing Seeded",
        unidad_medida="gramos",
        cantidad_stock=100,
        cantidad_minima=10,
        cantidad_reservada=0,
        descripcion="",
        categoria_id=None,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    prod_uow._ingredientes._storage[1] = ing
    prod_uow._ingredientes._next_id = 2
    prod_uow._ingredientes._name_index["test ing seeded"] = 1

    yield

    # cleanup es gestionado por el autouse reset_all_repos del conftest global


def _seed_cat_ing_in_prod_uow(cat_nombre: str, ing_nombre: str):
    """Seed categoría e ingrediente directamente en el UoW del router de productos."""
    import backend.modules.productos.router as prod_router_mod
    from backend.modules.categorias.model import Categoria
    from backend.modules.ingredientes.model import Ingrediente
    from datetime import datetime

    prod_uow = prod_router_mod.uow

    # Categoría
    cat_id = prod_uow._categorias._next_id
    cat = Categoria(
        id=cat_id,
        nombre=cat_nombre,
        descripcion="desc",
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    prod_uow._categorias._storage[cat_id] = cat
    prod_uow._categorias._next_id += 1
    prod_uow._categorias._name_index[cat_nombre.lower()] = cat_id

    # Ingrediente
    ing_id = prod_uow._ingredientes._next_id
    ing = Ingrediente(
        id=ing_id,
        nombre=ing_nombre,
        unidad_medida="gramos",
        cantidad_stock=100,
        cantidad_minima=10,
        cantidad_reservada=0,
        descripcion="",
        categoria_id=None,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    prod_uow._ingredientes._storage[ing_id] = ing
    prod_uow._ingredientes._next_id += 1
    prod_uow._ingredientes._name_index[ing_nombre.lower()] = ing_id

    return cat_id, ing_id


def _create_producto(client, admin_headers, cat_id, ing_id, nombre="Test Producto"):
    """Helper: crear un producto y retornar el response."""
    return client.post(
        "/productos",
        json={
            "nombre": nombre,
            "base_price": 100.0,
            "descripcion": "desc",
            "categories": [cat_id],
            "ingredients": [{"ingredient_id": ing_id, "quantity_required": 1.0}]
        },
        headers=admin_headers
    )


# ─────────────────────────────────────────────────────────────────────────────
# 3.2 — GET /productos sin auth retorna 200
# ─────────────────────────────────────────────────────────────────────────────

class TestListProductosEndpoint:
    """Tests para GET /productos"""

    def test_get_productos_no_auth_returns_200(self, client):
        """GET /productos sin autenticación → 200 con lista."""
        response = client.get("/productos")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data

    def test_get_productos_empty_list(self, client):
        """GET /productos sin datos → 200 con items vacíos."""
        response = client.get("/productos")

        assert response.status_code == 200
        assert response.json()["items"] == []


# ─────────────────────────────────────────────────────────────────────────────
# 3.3 — GET /productos/{id} con id existente retorna 200
# 3.4 — GET /productos/{id} con id inexistente retorna 404
# ─────────────────────────────────────────────────────────────────────────────

class TestGetProductoEndpoint:
    """Tests para GET /productos/{id}"""

    def test_get_producto_existing_returns_200(self, client, admin_headers):
        """GET /productos/{id} con producto existente → 200."""
        cat_id, ing_id = _seed_cat_ing_in_prod_uow("Pizzas", "Harina")
        create_resp = _create_producto(client, admin_headers, cat_id, ing_id, "Pizza Test")

        assert create_resp.status_code == 201
        product_id = create_resp.json()["id"]

        response = client.get(f"/productos/{product_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["nombre"] == "Pizza Test"

    def test_get_producto_not_found_returns_404(self, client):
        """GET /productos/{id} con ID inexistente → 404."""
        response = client.get("/productos/9999")

        assert response.status_code == 404

    def test_get_producto_returns_detail_fields(self, client, admin_headers):
        """GET /productos/{id} retorna campos completos."""
        cat_id, ing_id = _seed_cat_ing_in_prod_uow("Hamburguesas", "Pan")
        create_resp = _create_producto(client, admin_headers, cat_id, ing_id, "Hamburguesa")

        assert create_resp.status_code == 201
        product_id = create_resp.json()["id"]

        response = client.get(f"/productos/{product_id}")

        assert response.status_code == 200
        data = response.json()
        # Verificar campos obligatorios del detalle
        assert "id" in data
        assert "nombre" in data
        assert "base_price" in data
        assert "status" in data
        assert "stock_disponible" in data


# ─────────────────────────────────────────────────────────────────────────────
# 3.5 — POST /productos sin token retorna 401 o 403
# 3.6 — POST /productos con token ADMIN y payload válido retorna 201
# ─────────────────────────────────────────────────────────────────────────────

class TestCreateProductoEndpoint:
    """Tests para POST /productos"""

    def test_post_producto_no_auth_returns_401_or_403(self, client):
        """POST /productos sin autenticación → 401 o 403."""
        response = client.post(
            "/productos",
            json={
                "nombre": "Pizza Sin Auth",
                "base_price": 100.0,
                "categories": [1],
                "ingredients": [{"ingredient_id": 1, "quantity_required": 1.0}]
            }
        )

        assert response.status_code in [401, 403]

    def test_post_producto_admin_valid_payload_returns_201(self, client, admin_headers):
        """POST /productos con admin token y payload válido → 201."""
        cat_id, ing_id = _seed_cat_ing_in_prod_uow("Pastas", "Pasta")

        response = _create_producto(client, admin_headers, cat_id, ing_id, "Tallarines")

        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Tallarines"
        assert data["base_price"] == 100.0
        assert data["status"] == "active"

    def test_post_producto_client_role_returns_403(self, client, client_headers):
        """POST /productos con token CLIENT → 403."""
        response = client.post(
            "/productos",
            json={
                "nombre": "Producto Prohibido",
                "base_price": 50.0,
                "categories": [1],
                "ingredients": [{"ingredient_id": 1, "quantity_required": 1.0}]
            },
            headers=client_headers
        )

        assert response.status_code == 403

    def test_post_producto_nonexistent_category_returns_400(self, client, admin_headers):
        """POST /productos con categoría inexistente → 400."""
        # Solo seedear ingrediente, categoría 99999 no existe
        _, ing_id = _seed_cat_ing_in_prod_uow("Cat Para Ing Only", "Ingrediente X")

        response = client.post(
            "/productos",
            json={
                "nombre": "Producto Bad Cat",
                "base_price": 50.0,
                "categories": [99999],
                "ingredients": [{"ingredient_id": ing_id, "quantity_required": 1.0}]
            },
            headers=admin_headers
        )

        assert response.status_code == 400

    def test_post_producto_duplicate_name_returns_409(self, client, admin_headers):
        """POST /productos con nombre duplicado → 409."""
        cat_id, ing_id = _seed_cat_ing_in_prod_uow("Sushi Cat", "Arroz Ing")

        _create_producto(client, admin_headers, cat_id, ing_id, "Sushi Especial")

        response = _create_producto(client, admin_headers, cat_id, ing_id, "Sushi Especial")

        assert response.status_code == 409
