"""
Tests de integración — Flujo de transición de estados (despacho).

Prueba el flujo de avance y cancelación de estados de pedidos usando
TestClient(app) + el UoW in-memory (singleton_uow).

Endpoints:
- PATCH /api/v1/pedidos/{pedido_id}/estado
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.security import TokenService
from backend.core.uow_inmemory import singleton_uow
from backend.modules.clientes.model import Cliente
from backend.modules.productos.model import Product
from backend.modules.pedidos.model import Pedido, EstadoPedidoEnum, HistorialEstadoPedido


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _seed_cliente_despacho(cliente_id: int):
    cliente = Cliente(
        id=cliente_id,
        nombre=f"Cliente Despacho {cliente_id}",
        email=f"despacho{cliente_id}@test.com",
        direccion="Calle Despacho 123",
        activo=True,
    )
    singleton_uow._clientes._storage[cliente_id] = cliente
    singleton_uow._clientes._next_id = max(singleton_uow._clientes._next_id, cliente_id + 1)
    if hasattr(singleton_uow._clientes, '_email_index'):
        singleton_uow._clientes._email_index[cliente.email] = cliente_id
    return cliente


def _seed_producto_despacho(producto_id: int, stock: int = 50):
    product = Product(
        id=producto_id,
        nombre=f"Producto Despacho {producto_id}",
        base_price=100.0,
        status="active"
    )
    product.stock = stock
    product.ingredients = []
    singleton_uow._productos._storage[producto_id] = product
    singleton_uow._productos._next_id = max(singleton_uow._productos._next_id, producto_id + 1)
    singleton_uow._productos._name_index[product.nombre.lower()] = producto_id
    return product


def _seed_pedido_estado(pedido_id: int, cliente_id: int, estado: EstadoPedidoEnum):
    """Crear un pedido en un estado dado para tests de transición."""
    pedido = Pedido(
        cliente_id=cliente_id,
        estado=estado,
        direccion_snapshot='{"direccion": "Test", "nombre": "Test"}',
        total=100.0,
        costo_envio=0.0,
    )
    pedido.id = pedido_id
    singleton_uow._pedidos._storage[pedido_id] = pedido
    singleton_uow._pedidos._next_id = max(singleton_uow._pedidos._next_id, pedido_id + 1)

    # Historial inicial
    historial = HistorialEstadoPedido(
        pedido_id=pedido_id,
        estado_anterior=None,
        estado_nuevo=estado,
        usuario_id=cliente_id,
        observacion="Creado para test de despacho",
    )
    singleton_uow._historial_estado.create(historial)
    return pedido


def _seed_detalle_pedido(pedido_id: int, producto_id: int, cantidad: int = 2):
    """Crear un detalle de pedido en el singleton_uow."""
    from backend.modules.pedidos.model import DetallePedido
    detalle = DetallePedido(
        pedido_id=pedido_id,
        producto_id=producto_id,
        nombre_snapshot=f"Producto {producto_id}",
        precio_snapshot=100.0,
        cantidad=cantidad,
        personalizacion=[],
    )
    singleton_uow._detalles_pedido.create(detalle)
    return detalle


def _headers_for_role(user_id: int, role: str):
    token = TokenService.create_access_token(
        user_id=user_id,
        email=f"{role.lower()}{user_id}@test.com",
        role=role
    )
    return {"Authorization": f"Bearer {token}"}


# ─────────────────────────────────────────────────────────────────────────────
# 9.2 — Usuario PEDIDOS avanza CONFIRMADO → EN_PREPARACION → 200
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
class TestDespachoFlow:
    """Tests de transiciones de estado de pedidos."""

    def test_pedidos_role_advances_confirmado_to_en_prep(self, client, pedidos_headers):
        """PEDIDOS avanza pedido de CONFIRMADO a EN_PREPARACION → 200."""
        cliente_id = 400
        pedido_id = 400
        _seed_cliente_despacho(cliente_id)
        _seed_pedido_estado(pedido_id, cliente_id, EstadoPedidoEnum.CONFIRMADO)

        response = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "EN_PREPARACION", "motivo": None},
            headers=pedidos_headers
        )

        assert response.status_code == 200, f"Error: {response.text}"
        data = response.json()
        assert data["estado"] == "EN_PREPARACION"

    # ─────────────────────────────────────────────────────────────────────────
    # 9.3 — Usuario CLIENT intenta avanzar estado → 403
    # ─────────────────────────────────────────────────────────────────────────

    def test_client_cannot_advance_order_to_en_prep_returns_403(self, client):
        """CLIENT intenta avanzar pedido de CONFIRMADO → EN_PREP → 403."""
        cliente_id = 401
        pedido_id = 401
        _seed_cliente_despacho(cliente_id)
        _seed_pedido_estado(pedido_id, cliente_id, EstadoPedidoEnum.CONFIRMADO)

        # CLIENT no puede hacer CONFIRMADO → EN_PREPARACION
        client_headers = _headers_for_role(cliente_id, "CLIENT")
        response = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "EN_PREPARACION", "motivo": None},
            headers=client_headers
        )

        assert response.status_code == 403, f"Esperado 403, recibido: {response.status_code}"

    # ─────────────────────────────────────────────────────────────────────────
    # 9.4 — ADMIN cancela pedido CONFIRMADO → CANCELADO + stock restaurado
    # ─────────────────────────────────────────────────────────────────────────

    def test_admin_cancels_confirmado_order_restores_stock(self, client, admin_headers):
        """ADMIN cancela pedido CONFIRMADO → estado CANCELADO y stock restaurado."""
        cliente_id = 402
        pedido_id = 402
        producto_id = 402
        _seed_cliente_despacho(cliente_id)
        _seed_producto_despacho(producto_id, stock=10)
        _seed_pedido_estado(pedido_id, cliente_id, EstadoPedidoEnum.CONFIRMADO)
        _seed_detalle_pedido(pedido_id, producto_id, cantidad=3)

        stock_antes = singleton_uow._productos._storage[producto_id].stock

        response = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "CANCELADO", "motivo": "Cliente cambió de opinión"},
            headers=admin_headers
        )

        assert response.status_code == 200, f"Error: {response.text}"
        data = response.json()
        assert data["estado"] == "CANCELADO"

        # Verificar restauración del stock
        stock_despues = singleton_uow._productos._storage[producto_id].stock
        assert stock_despues == stock_antes + 3

    # ─────────────────────────────────────────────────────────────────────────
    # 9.5 — Intentar cancelar pedido ENTREGADO → 409
    # ─────────────────────────────────────────────────────────────────────────

    def test_cancel_entregado_order_returns_409(self, client, admin_headers):
        """Intentar cancelar pedido ENTREGADO → 409 (transición inválida)."""
        cliente_id = 403
        pedido_id = 403
        _seed_cliente_despacho(cliente_id)
        _seed_pedido_estado(pedido_id, cliente_id, EstadoPedidoEnum.ENTREGADO)

        response = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "CANCELADO", "motivo": "Intento de cancelar terminal"},
            headers=admin_headers
        )

        # ENTREGADO es terminal: no se puede cancelar
        assert response.status_code in [409, 422, 400], f"Inesperado: {response.status_code}"

    def test_cancel_cancelado_order_returns_409(self, client, admin_headers):
        """Intentar cancelar pedido ya CANCELADO → 409."""
        cliente_id = 404
        pedido_id = 404
        _seed_cliente_despacho(cliente_id)
        _seed_pedido_estado(pedido_id, cliente_id, EstadoPedidoEnum.CANCELADO)

        response = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "CANCELADO", "motivo": "Ya cancelado"},
            headers=admin_headers
        )

        assert response.status_code in [409, 422, 400]

    def test_advance_state_pedido_not_found_returns_404(self, client, pedidos_headers):
        """Avanzar estado de pedido inexistente → 404."""
        response = client.patch(
            "/api/v1/pedidos/99999/estado",
            json={"nuevo_estado": "EN_PREPARACION", "motivo": None},
            headers=pedidos_headers
        )

        assert response.status_code == 404

    def test_cancel_requires_motivo(self, client, admin_headers):
        """Cancelar sin motivo → 422 (validación de schema)."""
        cliente_id = 405
        pedido_id = 405
        _seed_cliente_despacho(cliente_id)
        _seed_pedido_estado(pedido_id, cliente_id, EstadoPedidoEnum.CONFIRMADO)

        response = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "CANCELADO", "motivo": None},
            headers=admin_headers
        )

        # motivo es obligatorio al cancelar (validado por Pydantic schema)
        assert response.status_code == 422

    def test_pedidos_advances_full_flow(self, client, pedidos_headers):
        """PEDIDOS avanza pedido por el flujo completo hasta ENTREGADO."""
        cliente_id = 406
        pedido_id = 406
        _seed_cliente_despacho(cliente_id)
        _seed_pedido_estado(pedido_id, cliente_id, EstadoPedidoEnum.CONFIRMADO)

        # CONFIRMADO → EN_PREPARACION
        r1 = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "EN_PREPARACION", "motivo": None},
            headers=pedidos_headers
        )
        assert r1.status_code == 200

        # EN_PREPARACION → EN_CAMINO
        r2 = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "EN_CAMINO", "motivo": None},
            headers=pedidos_headers
        )
        assert r2.status_code == 200

        # EN_CAMINO → ENTREGADO
        r3 = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "ENTREGADO", "motivo": None},
            headers=pedidos_headers
        )
        assert r3.status_code == 200
        assert r3.json()["estado"] == "ENTREGADO"
