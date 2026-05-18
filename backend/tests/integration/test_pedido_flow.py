"""
Tests de integración — Flujo de pedidos.

Prueba el flujo completo de creación y consulta de pedidos usando
TestClient(app) con el UoW in-memory.

Notas importantes:
- El PedidoService usa `singleton_uow` (compartido con auth, pagos, admin)
- Los tests deben precargar datos directamente en el singleton_uow para
  simular el estado necesario (productos, clientes)
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.security import TokenService
from backend.core.uow_inmemory import singleton_uow
from backend.modules.clientes.model import Cliente
from backend.modules.productos.model import Product


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _seed_cliente(cliente_id: int, nombre: str = "Cliente Test", direccion: str = "Av. Test 123"):
    """Insertar un cliente directamente en el singleton_uow para las pruebas."""
    cliente = Cliente(
        id=cliente_id,
        nombre=nombre,
        email=f"cliente{cliente_id}@test.com",
        direccion=direccion,
        telefono="+54 11 1234 5678",
        activo=True,
    )
    # Insertar directamente en el storage del repo
    singleton_uow._clientes._storage[cliente_id] = cliente
    singleton_uow._clientes._next_id = max(
        singleton_uow._clientes._next_id, cliente_id + 1
    )
    # El repo de clientes puede tener un _email_index — verificar si existe
    if hasattr(singleton_uow._clientes, '_email_index'):
        singleton_uow._clientes._email_index[cliente.email] = cliente_id
    return cliente


def _seed_producto(producto_id: int, nombre: str = "Producto Test", precio: float = 100.0, stock: int = 50):
    """Insertar un producto directamente en el singleton_uow."""
    product = Product(
        id=producto_id,
        nombre=nombre,
        base_price=precio,
        descripcion="Producto para tests",
        status="active"
    )
    product.stock = stock
    product.ingredients = []
    singleton_uow._productos._storage[producto_id] = product
    singleton_uow._productos._next_id = max(
        singleton_uow._productos._next_id, producto_id + 1
    )
    singleton_uow._productos._name_index[nombre.lower()] = producto_id
    return product


def _headers_for_user(user_id: int, role: str = "CLIENT"):
    token = TokenService.create_access_token(
        user_id=user_id,
        email=f"user{user_id}@test.com",
        role=role
    )
    return {"Authorization": f"Bearer {token}"}


# ─────────────────────────────────────────────────────────────────────────────
# 7.2 — Cliente crea pedido con producto disponible → 201, estado PENDIENTE
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
class TestPedidoCreation:
    """Tests de creación de pedidos."""

    def test_client_creates_order_returns_201_pendiente(self, client):
        """Cliente autenticado crea pedido con producto disponible → 201, PENDIENTE."""
        cliente_id = 100
        producto_id = 200
        _seed_cliente(cliente_id)
        _seed_producto(producto_id, stock=50)

        headers = _headers_for_user(cliente_id, role="client")

        response = client.post(
            "/api/v1/pedidos",
            json={
                "items": [
                    {
                        "producto_id": producto_id,
                        "cantidad": 2,
                        "personalizacion": {"excluidos": []}
                    }
                ],
                "direccion_id": cliente_id
            },
            headers=headers
        )

        assert response.status_code == 201, f"Esperado 201, recibido {response.status_code}: {response.text}"
        data = response.json()
        assert data["estado"] == "PENDIENTE"
        assert data["cliente_id"] == cliente_id

    def test_client_creates_order_calculates_total(self, client):
        """Cliente crea pedido → total calculado correctamente."""
        cliente_id = 101
        producto_id = 201
        _seed_cliente(cliente_id)
        _seed_producto(producto_id, precio=150.0, stock=10)

        headers = _headers_for_user(cliente_id, role="client")

        response = client.post(
            "/api/v1/pedidos",
            json={
                "items": [
                    {
                        "producto_id": producto_id,
                        "cantidad": 3,
                        "personalizacion": {"excluidos": []}
                    }
                ],
                "direccion_id": cliente_id
            },
            headers=headers
        )

        assert response.status_code == 201
        data = response.json()
        assert data["total"] == 450.0  # 3 x 150.0

    def test_unauthenticated_cannot_create_order_returns_401(self, client):
        """Sin token → 401."""
        response = client.post(
            "/api/v1/pedidos",
            json={
                "items": [{"producto_id": 1, "cantidad": 1, "personalizacion": {"excluidos": []}}],
                "direccion_id": 1
            }
        )

        assert response.status_code == 401

    # ─────────────────────────────────────────────────────────────────────────
    # 7.3 — Cliente crea pedido con cantidad mayor al stock → 400
    # ─────────────────────────────────────────────────────────────────────────

    def test_order_with_insufficient_stock_returns_400(self, client):
        """Cliente crea pedido con cantidad mayor al stock → 400."""
        cliente_id = 102
        producto_id = 202
        _seed_cliente(cliente_id)
        _seed_producto(producto_id, stock=2)  # Solo 2 en stock

        headers = _headers_for_user(cliente_id, role="client")

        response = client.post(
            "/api/v1/pedidos",
            json={
                "items": [
                    {
                        "producto_id": producto_id,
                        "cantidad": 10,  # Más de lo disponible
                        "personalizacion": {"excluidos": []}
                    }
                ],
                "direccion_id": cliente_id
            },
            headers=headers
        )

        assert response.status_code == 400

    def test_order_nonexistent_product_returns_400(self, client):
        """Pedido con producto inexistente → 400."""
        cliente_id = 103
        _seed_cliente(cliente_id)

        headers = _headers_for_user(cliente_id, role="client")

        response = client.post(
            "/api/v1/pedidos",
            json={
                "items": [
                    {
                        "producto_id": 99999,
                        "cantidad": 1,
                        "personalizacion": {"excluidos": []}
                    }
                ],
                "direccion_id": cliente_id
            },
            headers=headers
        )

        assert response.status_code in [400, 404]

    def test_empty_cart_returns_400(self, client):
        """Carrito vacío → 422 (validación Pydantic)."""
        cliente_id = 104
        _seed_cliente(cliente_id)

        headers = _headers_for_user(cliente_id, role="client")

        response = client.post(
            "/api/v1/pedidos",
            json={"items": [], "direccion_id": cliente_id},
            headers=headers
        )

        assert response.status_code in [400, 422]


# ─────────────────────────────────────────────────────────────────────────────
# 7.4 — GET /pedidos retorna solo los pedidos del cliente autenticado
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
class TestPedidoList:
    """Tests de listado de pedidos."""

    def test_list_orders_returns_only_own_orders(self, client):
        """GET /api/v1/pedidos retorna solo los pedidos del cliente autenticado."""
        # Crear dos clientes con pedidos separados
        c1_id = 110
        c2_id = 111
        p1_id = 210
        p2_id = 211

        _seed_cliente(c1_id, nombre="Cliente A")
        _seed_cliente(c2_id, nombre="Cliente B")
        _seed_producto(p1_id, nombre="Producto A", stock=20)
        _seed_producto(p2_id, nombre="Producto B", stock=20)

        headers_c1 = _headers_for_user(c1_id, role="client")
        headers_c2 = _headers_for_user(c2_id, role="client")

        # C1 crea un pedido
        client.post(
            "/api/v1/pedidos",
            json={"items": [{"producto_id": p1_id, "cantidad": 1, "personalizacion": {"excluidos": []}}],
                  "direccion_id": c1_id},
            headers=headers_c1
        )

        # C2 crea un pedido
        client.post(
            "/api/v1/pedidos",
            json={"items": [{"producto_id": p2_id, "cantidad": 1, "personalizacion": {"excluidos": []}}],
                  "direccion_id": c2_id},
            headers=headers_c2
        )

        # C1 solo debe ver sus propios pedidos
        list_resp = client.get("/api/v1/pedidos", headers=headers_c1)

        assert list_resp.status_code == 200
        pedidos = list_resp.json()
        for pedido in pedidos:
            assert pedido["cliente_id"] == c1_id

    def test_list_orders_unauthenticated_returns_401(self, client):
        """GET /api/v1/pedidos sin token → 401."""
        response = client.get("/api/v1/pedidos")

        assert response.status_code == 401
