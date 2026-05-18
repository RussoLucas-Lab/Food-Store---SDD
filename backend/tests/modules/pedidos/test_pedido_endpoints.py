"""
Tests de integración para endpoints de Pedidos.

Prueba los endpoints REST completos con el UoW real (in-memory).
Verifica que los routers mapeen correctamente excepciones a HTTP status.
"""

import pytest
import json
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.uow_inmemory import InMemoryUnitOfWork
import backend.modules.pedidos.router as pedidos_router_mod


@pytest.fixture
def client():
    """Fixture: TestClient para FastAPI."""
    return TestClient(app)


@pytest.fixture
def uow():
    """Fixture: Unit of Work real (in-memory)."""
    return InMemoryUnitOfWork()


@pytest.fixture
def client_headers():
    """Fixture: Headers con token de cliente válido."""
    from backend.core.security import TokenService
    token = TokenService.create_access_token(user_id=1, email="cliente@test.com", role="client")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client_headers_user2():
    """Fixture: Headers con token de cliente 2 (para probar 403)."""
    from backend.core.security import TokenService
    token = TokenService.create_access_token(user_id=2, email="cliente2@test.com", role="client")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def reset_pedidos_uow():
    """Reset del UoW singleton de pedidos antes y después de cada test."""
    def _reset():
        uow = pedidos_router_mod.uow
        # Reset repos de pedidos
        if hasattr(uow, '_pedidos'):
            uow._pedidos._storage.clear()
            uow._pedidos._next_id = 1
        if hasattr(uow, '_detalles_pedido'):
            uow._detalles_pedido._storage.clear()
            uow._detalles_pedido._next_id = 1
        if hasattr(uow, '_historial_estado'):
            uow._historial_estado._storage.clear()
            uow._historial_estado._next_id = 1
        # Reset repos de clientes (para precargar datos de test)
        if hasattr(uow, '_clientes'):
            uow._clientes._storage.clear()
            uow._clientes._next_id = 1
            uow._clientes._email_index.clear()
        # Reset repos de productos
        if hasattr(uow, '_productos'):
            uow._productos._storage.clear()
            uow._productos._next_id = 1
        uow.committed = False

    _reset()
    yield
    _reset()


def _seed_cliente_and_producto(uow_instance=None):
    """
    Precarga un cliente (id=1) y un producto (id=1) en el UoW singleton de pedidos.
    Retorna (cliente, producto).
    """
    if uow_instance is None:
        uow_instance = pedidos_router_mod.uow

    from backend.modules.clientes.model import Cliente
    from backend.modules.productos.model import Product
    from datetime import datetime

    # Crear cliente con id=1 (coincide con el user_id del token)
    cliente = Cliente(
        id=1,
        nombre="Test Cliente",
        email="cliente@test.com",
        direccion="Av. San Martín 1234",
        telefono="+54 11 1234 5678",
        activo=True,
        user_id=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    uow_instance._clientes._storage[1] = cliente
    uow_instance._clientes._next_id = 2
    uow_instance._clientes._email_index["cliente@test.com"] = 1

    # Crear producto simple
    product = Product(
        id=1,
        nombre="Pizza Margherita",
        base_price=150.0,
        descripcion="Pizza clásica",
        status="active",
    )
    # Agregar stock manualmente (el modelo Product no tiene campo stock directamente)
    product.stock = 100.0
    uow_instance._productos._storage[1] = product
    uow_instance._productos._next_id = 2

    return cliente, product


VALID_CART = {
    "items": [
        {
            "producto_id": 1,
            "cantidad": 2,
            "personalizacion": {"excluidos": []}
        }
    ],
    "direccion_id": 10
}


class TestCreateOrderEndpoint:
    """Tests para POST /api/v1/pedidos"""

    def test_post_pedidos_valid_returns_201(self, client, client_headers):
        """9.3.1: POST /api/v1/pedidos con carrito válido → 201."""
        _seed_cliente_and_producto()

        response = client.post(
            "/api/v1/pedidos",
            json=VALID_CART,
            headers=client_headers,
        )

        assert response.status_code == 201, response.json()
        data = response.json()
        assert data["estado"] == "PENDIENTE"
        assert data["cliente_id"] == 1
        assert data["total"] == 300.0  # 2 × 150.0

    def test_post_pedidos_no_auth_returns_401(self, client):
        """9.3.2: POST /api/v1/pedidos sin autenticación → 401."""
        response = client.post("/api/v1/pedidos", json=VALID_CART)
        assert response.status_code == 401

    def test_post_pedidos_empty_items_returns_400_or_422(self, client, client_headers):
        """9.3.3: POST /api/v1/pedidos con carrito vacío → 400 o 422."""
        _seed_cliente_and_producto()

        response = client.post(
            "/api/v1/pedidos",
            json={"items": [], "direccion_id": 10},
            headers=client_headers,
        )
        # Pydantic valida min_items=1 → 422; o el service lanza CartEmptyError → 400
        assert response.status_code in [400, 422], response.json()


class TestListOrdersEndpoint:
    """Tests para GET /api/v1/pedidos"""

    def test_get_pedidos_returns_own_orders_only(self, client, client_headers):
        """9.3.4: GET /api/v1/pedidos solo retorna pedidos del cliente autenticado → 200."""
        _seed_cliente_and_producto()

        # Crear un pedido primero
        client.post("/api/v1/pedidos", json=VALID_CART, headers=client_headers)

        response = client.get("/api/v1/pedidos", headers=client_headers)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # Todos los pedidos pertenecen al cliente_id=1
        for pedido in data:
            assert pedido["cliente_id"] == 1

    def test_get_pedidos_no_auth_returns_401(self, client):
        """GET /api/v1/pedidos sin autenticación → 401."""
        response = client.get("/api/v1/pedidos")
        assert response.status_code == 401


class TestGetOrderDetailEndpoint:
    """Tests para GET /api/v1/pedidos/{id}"""

    def test_get_pedido_detail_own_returns_200(self, client, client_headers):
        """9.3.5: GET /api/v1/pedidos/{id} del pedido propio → 200 con detalles e historial."""
        _seed_cliente_and_producto()

        # Crear pedido primero
        create_response = client.post("/api/v1/pedidos", json=VALID_CART, headers=client_headers)
        assert create_response.status_code == 201
        pedido_id = create_response.json()["id"]

        response = client.get(f"/api/v1/pedidos/{pedido_id}", headers=client_headers)

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pedido_id
        assert "detalles" in data
        assert "historial" in data
        assert len(data["detalles"]) == 1
        assert len(data["historial"]) == 1
        assert data["historial"][0]["estado_nuevo"] == "PENDIENTE"
        assert data["historial"][0]["estado_anterior"] is None

    def test_get_pedido_detail_other_client_returns_403(self, client, client_headers, client_headers_user2):
        """9.3.6: GET /api/v1/pedidos/{id} del pedido ajeno → 403."""
        _seed_cliente_and_producto()

        # Crear pedido con cliente 1
        create_response = client.post("/api/v1/pedidos", json=VALID_CART, headers=client_headers)
        assert create_response.status_code == 201
        pedido_id = create_response.json()["id"]

        # Intentar acceder con cliente 2
        response = client.get(f"/api/v1/pedidos/{pedido_id}", headers=client_headers_user2)
        assert response.status_code == 403

    def test_get_pedido_detail_not_found_returns_404(self, client, client_headers):
        """9.3.7: GET /api/v1/pedidos/{id} inexistente → 404."""
        response = client.get("/api/v1/pedidos/9999", headers=client_headers)
        assert response.status_code == 404
