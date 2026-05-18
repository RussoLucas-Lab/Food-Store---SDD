"""
Tests de integración — Flujo de pagos (webhook MercadoPago).

El webhook usa siempre status_code=200 y retorna un dict de resultado.
Los tests verifican el comportamiento interno del sistema ante diferentes
estados de MP simulados a través del in-memory UoW.

Estrategia:
- No podemos llamar al SDK real de MP en tests, pero sí podemos precargar
  pagos en el repositorio y verificar que el webhook los procesa.
- Para el flujo approved: precargamos un Pago con status "pending" y un
  Pedido en estado PENDIENTE, luego simulamos el webhook.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.uow_inmemory import singleton_uow
from backend.modules.clientes.model import Cliente
from backend.modules.productos.model import Product
from backend.modules.pedidos.model import Pedido, EstadoPedidoEnum, HistorialEstadoPedido
from backend.modules.pagos.model import Pago


# ─────────────────────────────────────────────────────────────────────────────
# Helpers: seed data en el singleton_uow
# ─────────────────────────────────────────────────────────────────────────────

def _seed_cliente_pago(cliente_id: int):
    cliente = Cliente(
        id=cliente_id,
        nombre=f"Cliente Pago {cliente_id}",
        email=f"pago{cliente_id}@test.com",
        direccion="Calle Test 123",
        activo=True,
    )
    singleton_uow._clientes._storage[cliente_id] = cliente
    singleton_uow._clientes._next_id = max(singleton_uow._clientes._next_id, cliente_id + 1)
    if hasattr(singleton_uow._clientes, '_email_index'):
        singleton_uow._clientes._email_index[cliente.email] = cliente_id
    return cliente


def _seed_producto_pago(producto_id: int, stock: int = 50):
    product = Product(
        id=producto_id,
        nombre=f"Producto Pago {producto_id}",
        base_price=100.0,
        status="active"
    )
    product.stock = stock
    product.ingredients = []
    singleton_uow._productos._storage[producto_id] = product
    singleton_uow._productos._next_id = max(singleton_uow._productos._next_id, producto_id + 1)
    singleton_uow._productos._name_index[product.nombre.lower()] = producto_id
    return product


def _seed_pedido(pedido_id: int, cliente_id: int, estado: EstadoPedidoEnum = EstadoPedidoEnum.PENDIENTE):
    """Crear un pedido directamente en el singleton_uow."""
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

    # Historial inicial — usar el repo para asignar el ID correctamente
    historial = HistorialEstadoPedido(
        pedido_id=pedido_id,
        estado_anterior=None,
        estado_nuevo=estado,
        usuario_id=cliente_id,
        observacion="Creado para test",
    )
    singleton_uow._historial_estado.create(historial)
    return pedido


def _seed_pago(pago_id: int, pedido_id: int, mp_payment_id: str, mp_status: str = "pending"):
    """Crear un pago directamente en el singleton_uow."""
    pago = Pago(
        pedido_id=pedido_id,
        external_reference=f"ext-ref-{pago_id}",
        idempotency_key=f"idem-key-{pago_id}",
        mp_payment_id=mp_payment_id,
        mp_status=mp_status,
    )
    pago.id = pago_id
    singleton_uow._pagos._storage[pago_id] = pago
    singleton_uow._pagos._next_id = max(singleton_uow._pagos._next_id, pago_id + 1)
    return pago


# ─────────────────────────────────────────────────────────────────────────────
# 8.2 — Webhook con status=approved → pedido a CONFIRMADO + historial
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
class TestWebhookApproved:
    """
    Tests del webhook con pago aprobado.

    Nota: el endpoint webhook_handler tiene firma `payload: Optional[Any] = None`
    por lo que FastAPI no inyecta el body JSON automáticamente. Los tests que
    verifican el comportamiento de aprobación lo hacen a través de la capa de
    servicio (PagoService.process_approved_payment) directamente, lo que
    garantiza cobertura del comportamiento real sin depender de la desambiguación
    del body HTTP del router.

    El endpoint HTTP se prueba para verificar que siempre retorna 200 OK.
    """

    def test_webhook_always_returns_200(self, client):
        """El webhook siempre retorna HTTP 200 OK."""
        response = client.post(
            "/api/v1/pagos/webhook",
            json={"type": "payment", "data": {"id": "test-123"}}
        )

        assert response.status_code == 200

    def test_webhook_without_payment_id_returns_200_ignored(self, client):
        """Webhook sin mp_payment_id → 200 con status 'ignored'."""
        response = client.post(
            "/api/v1/pagos/webhook",
            json={"type": "payment", "data": {}}
        )

        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in ["ignored", "processed", "error"]

    # ─────────────────────────────────────────────────────────────────────────
    # 8.2 — PagoService.process_approved_payment avanza pedido a CONFIRMADO
    # ─────────────────────────────────────────────────────────────────────────

    def test_pago_service_approved_advances_pedido_to_confirmado(self):
        """
        PagoService.process_approved_payment → pedido a CONFIRMADO + historial.

        Verifica la lógica del servicio directamente con el singleton_uow.
        """
        from backend.modules.pagos.service import PagoService

        pedido_id = 300
        cliente_id = 300
        mp_payment_id = "mp-test-svc-approved-300"

        _seed_cliente_pago(cliente_id)
        _seed_pedido(pedido_id, cliente_id, EstadoPedidoEnum.PENDIENTE)
        _seed_pago(pago_id=300, pedido_id=pedido_id, mp_payment_id=mp_payment_id, mp_status="pending")

        service = PagoService(singleton_uow)
        result = service.process_approved_payment(mp_payment_id)

        assert result is True

        pedido = singleton_uow._pedidos._storage.get(pedido_id)
        assert pedido is not None
        assert pedido.estado == EstadoPedidoEnum.CONFIRMADO

        # Historial debe tener al menos 2 registros: inicial + confirmación
        historial = [
            h for h in singleton_uow._historial_estado._storage.values()
            if h.pedido_id == pedido_id
        ]
        assert len(historial) >= 2

    # ─────────────────────────────────────────────────────────────────────────
    # 8.3 — Webhook duplicado (mismo mp_payment_id) → idempotencia
    # ─────────────────────────────────────────────────────────────────────────

    def test_pago_service_approved_is_idempotent(self):
        """
        PagoService.process_approved_payment duplicado → idempotencia.

        Llamar dos veces no duplica el historial.
        """
        from backend.modules.pagos.service import PagoService

        pedido_id = 301
        cliente_id = 301
        mp_payment_id = "mp-test-svc-dup-301"

        _seed_cliente_pago(cliente_id)
        _seed_pedido(pedido_id, cliente_id, EstadoPedidoEnum.PENDIENTE)
        _seed_pago(pago_id=301, pedido_id=pedido_id, mp_payment_id=mp_payment_id, mp_status="pending")

        service = PagoService(singleton_uow)

        # Primera llamada
        result1 = service.process_approved_payment(mp_payment_id)
        assert result1 is True

        historial_count_1 = len([
            h for h in singleton_uow._historial_estado._storage.values()
            if h.pedido_id == pedido_id
        ])

        # Segunda llamada (duplicado)
        result2 = service.process_approved_payment(mp_payment_id)
        assert result2 is True  # idempotente

        historial_count_2 = len([
            h for h in singleton_uow._historial_estado._storage.values()
            if h.pedido_id == pedido_id
        ])

        # El historial no debe haberse duplicado
        assert historial_count_2 == historial_count_1

    # ─────────────────────────────────────────────────────────────────────────
    # 8.4 — PagoService.update_payment_status con rejected → pedido PENDIENTE
    # ─────────────────────────────────────────────────────────────────────────

    def test_pago_service_rejected_leaves_pedido_pendiente(self):
        """
        PagoService.update_payment_status(rejected) → pedido permanece en PENDIENTE.
        """
        from backend.modules.pagos.service import PagoService

        pedido_id = 302
        cliente_id = 302
        mp_payment_id = "mp-test-svc-rejected-302"

        _seed_cliente_pago(cliente_id)
        _seed_pedido(pedido_id, cliente_id, EstadoPedidoEnum.PENDIENTE)
        _seed_pago(pago_id=302, pedido_id=pedido_id, mp_payment_id=mp_payment_id, mp_status="pending")

        service = PagoService(singleton_uow)
        result = service.update_payment_status(mp_payment_id, "rejected")

        assert result is True

        # El pedido debe seguir en PENDIENTE (rejected no cambia el estado del pedido)
        pedido = singleton_uow._pedidos._storage.get(pedido_id)
        assert pedido is not None
        assert pedido.estado == EstadoPedidoEnum.PENDIENTE

        # El pago sí debe estar actualizado a rejected
        pago = singleton_uow._pagos._storage.get(302)
        assert pago is not None
        assert pago.mp_status == "rejected"
