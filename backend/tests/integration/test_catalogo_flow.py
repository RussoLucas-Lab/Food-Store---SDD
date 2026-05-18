"""
Tests de integración — Flujo de catálogo.

Prueba el flujo completo de creación y consulta de productos, categorías
e ingredientes usando TestClient(app) con el UoW in-memory.

Nota de arquitectura:
Cada módulo (categorias, ingredientes, productos) usa su propia instancia de
InMemoryUnitOfWork. Para crear productos via HTTP, se deben sembrar categorías
e ingredientes directamente en el UoW del router de productos.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from backend.main import app
from backend.modules.categorias.model import Categoria
from backend.modules.ingredientes.model import Ingrediente


# ─────────────────────────────────────────────────────────────────────────────
# Helpers — seed directo en el UoW del router de productos
# ─────────────────────────────────────────────────────────────────────────────

def _seed_in_prod_uow(cat_nombre: str, ing_nombre: str):
    """Seed categoría e ingrediente en el UoW del router de productos."""
    import backend.modules.productos.router as prod_router_mod
    prod_uow = prod_router_mod.uow

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

    ing_id = prod_uow._ingredientes._next_id
    ing = Ingrediente(
        id=ing_id,
        nombre=ing_nombre,
        unidad_medida="gramos",
        cantidad_stock=200,
        cantidad_minima=10,
        cantidad_reservada=0,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    prod_uow._ingredientes._storage[ing_id] = ing
    prod_uow._ingredientes._next_id += 1
    prod_uow._ingredientes._name_index[ing_nombre.lower()] = ing_id

    return cat_id, ing_id


def _create_producto(client, admin_headers, cat_id, ing_id, nombre, precio=150.0):
    return client.post(
        "/productos",
        json={
            "nombre": nombre,
            "base_price": precio,
            "descripcion": "Producto de prueba",
            "categories": [cat_id],
            "ingredients": [{"ingredient_id": ing_id, "quantity_required": 1.0}]
        },
        headers=admin_headers
    )


# ─────────────────────────────────────────────────────────────────────────────
# 6.2 — GET /productos sin auth retorna 200
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
class TestCatalogoPublicAccess:
    """Tests de acceso público al catálogo."""

    def test_get_productos_no_auth_returns_200(self, client):
        """GET /productos sin autenticación → 200 con lista."""
        response = client.get("/productos")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_get_categorias_no_auth_returns_200(self, client):
        """GET /categorias sin autenticación → 200."""
        response = client.get("/categorias")

        assert response.status_code == 200

    def test_get_ingredientes_no_auth_returns_200(self, client):
        """GET /ingredientes sin autenticación → 200."""
        response = client.get("/ingredientes")

        assert response.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# 6.3 — POST /productos como ADMIN → 201 y aparece en GET
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
class TestCatalogoAdminFlow:
    """Tests del flujo de gestión del catálogo como ADMIN."""

    def test_admin_create_product_appears_in_list(self, client, admin_headers):
        """ADMIN crea producto → aparece en GET /productos."""
        cat_id, ing_id = _seed_in_prod_uow("Pizzas Integration", "Mozzarella Integration")

        create_resp = _create_producto(
            client, admin_headers, cat_id, ing_id, "Pizza Integración"
        )

        assert create_resp.status_code == 201
        product_id = create_resp.json()["id"]

        # Verificar que aparece en la lista
        list_resp = client.get("/productos")

        assert list_resp.status_code == 200
        items = list_resp.json()["items"]
        ids = [p["id"] for p in items]
        assert product_id in ids

    def test_admin_create_product_returns_correct_data(self, client, admin_headers):
        """ADMIN crea producto → respuesta tiene datos correctos."""
        cat_id, ing_id = _seed_in_prod_uow("Pastas Int", "Pasta Int")

        response = _create_producto(
            client, admin_headers, cat_id, ing_id, "Tallarines Integración", precio=200.0
        )

        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Tallarines Integración"
        assert data["base_price"] == 200.0
        assert data["status"] == "active"

    def test_admin_can_retrieve_product_by_id(self, client, admin_headers):
        """ADMIN crea producto → GET /{id} retorna detalles correctos."""
        cat_id, ing_id = _seed_in_prod_uow("Ensaladas Int", "Lechuga Int")

        create_resp = _create_producto(
            client, admin_headers, cat_id, ing_id, "Ensalada César Int"
        )
        product_id = create_resp.json()["id"]

        get_resp = client.get(f"/productos/{product_id}")

        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == product_id
        assert get_resp.json()["nombre"] == "Ensalada César Int"

    # ─────────────────────────────────────────────────────────────────────────
    # 6.4 — POST /productos como CLIENT retorna 403
    # ─────────────────────────────────────────────────────────────────────────

    def test_client_cannot_create_product_returns_403(self, client, client_headers):
        """POST /productos como CLIENT → 403."""
        response = client.post(
            "/productos",
            json={
                "nombre": "Producto Prohibido",
                "base_price": 100.0,
                "categories": [1],
                "ingredients": [{"ingredient_id": 1, "quantity_required": 1.0}]
            },
            headers=client_headers
        )

        assert response.status_code == 403

    def test_unauthenticated_cannot_create_product(self, client):
        """POST /productos sin token → 401."""
        response = client.post(
            "/productos",
            json={
                "nombre": "Producto Sin Token",
                "base_price": 100.0,
                "categories": [1],
                "ingredients": [{"ingredient_id": 1, "quantity_required": 1.0}]
            }
        )

        assert response.status_code in [401, 403]


@pytest.mark.integration
class TestCategoriaFlow:
    """Tests del flujo completo de categorías."""

    def test_admin_create_category_appears_in_list(self, client, admin_headers):
        """ADMIN crea categoría → aparece en GET /categorias."""
        create_resp = client.post(
            "/categorias",
            json={"nombre": "Bebidas Int", "descripcion": "Bebidas"},
            headers=admin_headers
        )

        assert create_resp.status_code == 201
        cat_id = create_resp.json()["id"]

        list_resp = client.get("/categorias")

        assert list_resp.status_code == 200
        items = list_resp.json()["items"]
        ids = [c["id"] for c in items]
        assert cat_id in ids

    def test_admin_delete_category_removes_from_list(self, client, admin_headers):
        """ADMIN elimina categoría → desaparece del listado."""
        create_resp = client.post(
            "/categorias",
            json={"nombre": "Postres Delete", "descripcion": "desc"},
            headers=admin_headers
        )
        cat_id = create_resp.json()["id"]

        del_resp = client.delete(f"/categorias/{cat_id}", headers=admin_headers)

        assert del_resp.status_code == 204

        # Ya no debe aparecer en el listado
        list_resp = client.get("/categorias")
        items = list_resp.json()["items"]
        ids = [c["id"] for c in items]
        assert cat_id not in ids
