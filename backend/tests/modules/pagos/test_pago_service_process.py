"""
Tests unitarios para PagoService.process_approved_payment.

Casos cubiertos:
- Idempotencia: si mp_status ya es "approved", retorna True sin efecto
- Transición atómica: actualiza Pago, Pedido, stock y HistorialEstadoPedido en una UoW
- Pago no encontrado: retorna False
- Historial: inserta exactamente un registro append-only con usuario_id=None
- Stock: decrementa correctamente para cada DetallePedido
"""

import pytest
from unittest.mock import Mock, call
from datetime import datetime

from backend.modules.pagos.service import PagoService
from backend.modules.pagos.model import Pago
from backend.modules.pedidos.model import Pedido, DetallePedido, HistorialEstadoPedido, EstadoPedidoEnum


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_pago(id: int, pedido_id: int, mp_payment_id: str = "mp-123", mp_status: str = "pending") -> Pago:
    """Crea un Pago de prueba."""
    pago = Pago(
        pedido_id=pedido_id,
        external_reference="ext-ref",
        idempotency_key="idmp-key",
        mp_payment_id=mp_payment_id,
        mp_status=mp_status,
    )
    pago.id = id
    pago.creado_en = datetime.utcnow()
    return pago


def _make_pedido(id: int, cliente_id: int = 5, estado: EstadoPedidoEnum = EstadoPedidoEnum.PENDIENTE) -> Pedido:
    """Crea un Pedido de prueba."""
    pedido = Pedido(cliente_id=cliente_id, total=300.0, estado=estado)
    pedido.id = id
    return pedido


def _make_detalle(id: int, pedido_id: int, producto_id: int, cantidad: int) -> DetallePedido:
    """Crea un DetallePedido de prueba."""
    d = DetallePedido(
        pedido_id=pedido_id,
        producto_id=producto_id,
        nombre_snapshot="Producto Test",
        cantidad=cantidad,
        precio_snapshot=100.0,
    )
    d.id = id
    return d


def _make_producto_mock(id: int, stock: int) -> Mock:
    """Crea un mock de Producto con stock."""
    p = Mock()
    p.id = id
    p.stock = stock
    return p


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_uow():
    """Mock Unit of Work completo para tests de process_approved_payment."""
    uow = Mock()
    uow.pagos = Mock()
    uow.pedidos = Mock()
    uow.detalles_pedido = Mock()
    uow.historial_estado = Mock()
    uow.productos = Mock()
    uow.commit = Mock()
    uow.rollback = Mock()
    return uow


@pytest.fixture
def service(mock_uow):
    """PagoService con mock UoW."""
    return PagoService(mock_uow)


# ── Tests: process_approved_payment ──────────────────────────────────────────

class TestProcessApprovedPayment:
    """Tests para PagoService.process_approved_payment()"""

    def test_payment_not_found_returns_false(self, service, mock_uow):
        """
        Si el pago no existe en BD, retorna False (pago desconocido → ignorar).
        """
        mock_uow.pagos.get_by_mp_payment_id.return_value = None

        result = service.process_approved_payment("mp-unknown-999")

        assert result is False
        mock_uow.commit.assert_not_called()

    def test_already_approved_is_idempotent(self, service, mock_uow):
        """
        Si el pago ya tiene mp_status="approved", retorna True sin ningún efecto adicional.
        Idempotencia: el webhook puede llegar múltiples veces.
        """
        pago = _make_pago(1, pedido_id=10, mp_status="approved")
        mock_uow.pagos.get_by_mp_payment_id.return_value = pago

        result = service.process_approved_payment("mp-123")

        assert result is True
        # Sin efectos secundarios
        mock_uow.pagos.update_status.assert_not_called()
        mock_uow.pedidos.update_estado.assert_not_called()
        mock_uow.historial_estado.create.assert_not_called()
        mock_uow.commit.assert_not_called()

    def test_atomic_transition_updates_pago_status(self, service, mock_uow):
        """
        Transición atómica: actualiza Pago.mp_status a "approved".
        """
        pago = _make_pago(1, pedido_id=10, mp_status="pending")
        pedido = _make_pedido(10, estado=EstadoPedidoEnum.PENDIENTE)

        mock_uow.pagos.get_by_mp_payment_id.return_value = pago
        mock_uow.pedidos.get_by_id.return_value = pedido
        mock_uow.detalles_pedido.list_by_pedido.return_value = []

        def historial_create(h):
            h.id = 99
            return h
        mock_uow.historial_estado.create.side_effect = historial_create

        result = service.process_approved_payment("mp-123")

        assert result is True
        mock_uow.pagos.update_status.assert_called_once_with(1, "approved")

    def test_atomic_transition_updates_pedido_estado(self, service, mock_uow):
        """
        Transición atómica: avanza el pedido a CONFIRMADO.
        """
        pago = _make_pago(1, pedido_id=10, mp_status="pending")
        pedido = _make_pedido(10, estado=EstadoPedidoEnum.PENDIENTE)

        mock_uow.pagos.get_by_mp_payment_id.return_value = pago
        mock_uow.pedidos.get_by_id.return_value = pedido
        mock_uow.detalles_pedido.list_by_pedido.return_value = []
        mock_uow.historial_estado.create.return_value = Mock()

        result = service.process_approved_payment("mp-123")

        assert result is True
        mock_uow.pedidos.update_estado.assert_called_once_with(10, EstadoPedidoEnum.CONFIRMADO)

    def test_atomic_transition_decrements_stock(self, service, mock_uow):
        """
        Transición atómica: decrementa stock de cada producto en DetallePedido.
        """
        pago = _make_pago(1, pedido_id=10, mp_status="pending")
        pedido = _make_pedido(10, estado=EstadoPedidoEnum.PENDIENTE)
        detalle1 = _make_detalle(1, pedido_id=10, producto_id=100, cantidad=3)
        detalle2 = _make_detalle(2, pedido_id=10, producto_id=200, cantidad=1)

        producto1 = _make_producto_mock(100, stock=10)
        producto2 = _make_producto_mock(200, stock=5)

        mock_uow.pagos.get_by_mp_payment_id.return_value = pago
        mock_uow.pedidos.get_by_id.return_value = pedido
        mock_uow.detalles_pedido.list_by_pedido.return_value = [detalle1, detalle2]
        mock_uow.productos.find_by_id.side_effect = lambda pid: (
            producto1 if pid == 100 else producto2
        )
        mock_uow.historial_estado.create.return_value = Mock()

        service.process_approved_payment("mp-123")

        # Stock decrementado correctamente
        assert producto1.stock == 7   # 10 - 3
        assert producto2.stock == 4   # 5 - 1

    def test_atomic_transition_creates_historial_entry(self, service, mock_uow):
        """
        Transición atómica: inserta exactamente un registro en HistorialEstadoPedido.
        Append-only: usuario_id=None (transición automática por sistema).
        """
        pago = _make_pago(1, pedido_id=10, mp_status="pending")
        pedido = _make_pedido(10, estado=EstadoPedidoEnum.PENDIENTE)

        mock_uow.pagos.get_by_mp_payment_id.return_value = pago
        mock_uow.pedidos.get_by_id.return_value = pedido
        mock_uow.detalles_pedido.list_by_pedido.return_value = []

        historial_creados = []

        def historial_create(h):
            h.id = 1
            historial_creados.append(h)
            return h
        mock_uow.historial_estado.create.side_effect = historial_create

        service.process_approved_payment("mp-123")

        assert len(historial_creados) == 1
        assert historial_creados[0].estado_nuevo == EstadoPedidoEnum.CONFIRMADO
        assert historial_creados[0].estado_anterior == EstadoPedidoEnum.PENDIENTE
        assert historial_creados[0].usuario_id is None  # Sistema, no usuario

    def test_atomic_transition_calls_commit(self, service, mock_uow):
        """
        Transición atómica: llama uow.commit() exactamente una vez.
        """
        pago = _make_pago(1, pedido_id=10, mp_status="pending")
        pedido = _make_pedido(10, estado=EstadoPedidoEnum.PENDIENTE)

        mock_uow.pagos.get_by_mp_payment_id.return_value = pago
        mock_uow.pedidos.get_by_id.return_value = pedido
        mock_uow.detalles_pedido.list_by_pedido.return_value = []
        mock_uow.historial_estado.create.return_value = Mock()

        service.process_approved_payment("mp-123")

        mock_uow.commit.assert_called_once()

    def test_stock_does_not_go_negative(self, service, mock_uow):
        """
        Si el stock es menor que la cantidad pedida, no va a negativo (se trunca en 0).
        """
        pago = _make_pago(1, pedido_id=10, mp_status="pending")
        pedido = _make_pedido(10, estado=EstadoPedidoEnum.PENDIENTE)
        detalle = _make_detalle(1, pedido_id=10, producto_id=100, cantidad=50)
        producto = _make_producto_mock(100, stock=3)  # Menos stock del pedido

        mock_uow.pagos.get_by_mp_payment_id.return_value = pago
        mock_uow.pedidos.get_by_id.return_value = pedido
        mock_uow.detalles_pedido.list_by_pedido.return_value = [detalle]
        mock_uow.productos.find_by_id.return_value = producto
        mock_uow.historial_estado.create.return_value = Mock()

        service.process_approved_payment("mp-123")

        assert producto.stock == 0  # max(0, 3 - 50) = 0
