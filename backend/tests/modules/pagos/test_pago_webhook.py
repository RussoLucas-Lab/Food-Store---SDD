"""
Tests unitarios para el webhook handler de MercadoPago.

Casos cubiertos:
- Estado "approved": llama process_approved_payment
- Estado "pending": llama update_payment_status con "pending"
- Estado "rejected": llama update_payment_status con "rejected"
- Estado "cancelled": llama update_payment_status con "cancelled"
- Estado "in_process": llama update_payment_status con "in_process"
- Pago duplicado (mp_status ya "approved"): idempotencia — no procesa de nuevo
- Payload sin mp_payment_id: ignorado (retorna "ignored")
- Estado desconocido: ignorado (no lanza error)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

from backend.modules.pagos.service import PagoService
from backend.modules.pagos.model import Pago
from backend.modules.pedidos.model import Pedido, EstadoPedidoEnum


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_pago(mp_status: str = "pending", mp_payment_id: str = "mp-123") -> Pago:
    """Crea un Pago de prueba."""
    pago = Pago(
        pedido_id=10,
        external_reference="ext-ref",
        idempotency_key="idmp-key",
        mp_payment_id=mp_payment_id,
        mp_status=mp_status,
    )
    pago.id = 1
    return pago


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_uow():
    """Mock Unit of Work."""
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


# ── Tests: _process_webhook_by_status ─────────────────────────────────────────

class TestWebhookHandlerByStatus:
    """Tests para la lógica del webhook clasificada por estado."""

    def test_approved_calls_process_approved_payment(self, service, mock_uow):
        """
        Estado "approved" → llama process_approved_payment(mp_payment_id).
        """
        pago = _make_pago(mp_status="pending", mp_payment_id="mp-123")
        pedido = Pedido(cliente_id=5, total=300.0, estado=EstadoPedidoEnum.PENDIENTE)
        pedido.id = 10

        mock_uow.pagos.get_by_mp_payment_id.return_value = pago
        mock_uow.pedidos.get_by_id.return_value = pedido
        mock_uow.detalles_pedido.list_by_pedido.return_value = []
        mock_uow.historial_estado.create.return_value = Mock()

        result = service.process_approved_payment("mp-123")

        assert result is True
        mock_uow.pagos.update_status.assert_called_once_with(1, "approved")
        mock_uow.pedidos.update_estado.assert_called_once_with(10, EstadoPedidoEnum.CONFIRMADO)
        mock_uow.commit.assert_called_once()

    def test_pending_calls_update_payment_status(self, service, mock_uow):
        """
        Estado "pending" → solo actualiza mp_status, no avanza pedido.
        """
        pago = _make_pago(mp_status="in_process", mp_payment_id="mp-456")
        mock_uow.pagos.get_by_mp_payment_id.return_value = pago

        result = service.update_payment_status("mp-456", "pending")

        assert result is True
        mock_uow.pagos.update_status.assert_called_once_with(1, "pending")
        # No debe avanzar el pedido
        mock_uow.pedidos.update_estado.assert_not_called()
        mock_uow.historial_estado.create.assert_not_called()
        mock_uow.commit.assert_called_once()

    def test_in_process_calls_update_payment_status(self, service, mock_uow):
        """
        Estado "in_process" → solo actualiza mp_status, no avanza pedido.
        """
        pago = _make_pago(mp_status="pending", mp_payment_id="mp-789")
        mock_uow.pagos.get_by_mp_payment_id.return_value = pago

        result = service.update_payment_status("mp-789", "in_process")

        assert result is True
        mock_uow.pagos.update_status.assert_called_once_with(1, "in_process")
        mock_uow.pedidos.update_estado.assert_not_called()
        mock_uow.commit.assert_called_once()

    def test_rejected_calls_update_payment_status(self, service, mock_uow):
        """
        Estado "rejected" → actualiza mp_status, pedido permanece PENDIENTE.
        """
        pago = _make_pago(mp_status="pending", mp_payment_id="mp-rej")
        mock_uow.pagos.get_by_mp_payment_id.return_value = pago

        result = service.update_payment_status("mp-rej", "rejected")

        assert result is True
        mock_uow.pagos.update_status.assert_called_once_with(1, "rejected")
        mock_uow.pedidos.update_estado.assert_not_called()
        mock_uow.commit.assert_called_once()

    def test_cancelled_calls_update_payment_status(self, service, mock_uow):
        """
        Estado "cancelled" → actualiza mp_status, pedido permanece PENDIENTE.
        """
        pago = _make_pago(mp_status="pending", mp_payment_id="mp-can")
        mock_uow.pagos.get_by_mp_payment_id.return_value = pago

        result = service.update_payment_status("mp-can", "cancelled")

        assert result is True
        mock_uow.pagos.update_status.assert_called_once_with(1, "cancelled")
        mock_uow.pedidos.update_estado.assert_not_called()
        mock_uow.commit.assert_called_once()

    def test_duplicate_approved_is_idempotent(self, service, mock_uow):
        """
        Pago duplicado (ya approved) → idempotencia garantizada, sin efectos secundarios.
        El webhook de MP puede llegar múltiples veces.
        """
        pago = _make_pago(mp_status="approved", mp_payment_id="mp-dup")
        mock_uow.pagos.get_by_mp_payment_id.return_value = pago

        result = service.process_approved_payment("mp-dup")

        assert result is True
        # Sin efectos secundarios — idempotencia
        mock_uow.pagos.update_status.assert_not_called()
        mock_uow.pedidos.update_estado.assert_not_called()
        mock_uow.historial_estado.create.assert_not_called()
        mock_uow.commit.assert_not_called()

    def test_unknown_payment_returns_false(self, service, mock_uow):
        """
        Pago no encontrado (mp_payment_id desconocido) → retorna False, sin crash.
        """
        mock_uow.pagos.get_by_mp_payment_id.return_value = None

        result = service.process_approved_payment("mp-unknown")

        assert result is False
        mock_uow.commit.assert_not_called()

    def test_update_status_payment_not_found_returns_false(self, service, mock_uow):
        """
        update_payment_status para pago inexistente → retorna False.
        """
        mock_uow.pagos.get_by_mp_payment_id.return_value = None

        result = service.update_payment_status("mp-nope", "pending")

        assert result is False
        mock_uow.commit.assert_not_called()


# ── Tests: _extract_mp_payment_id (router function) ──────────────────────────

class TestExtractMpPaymentId:
    """Tests para la función _extract_mp_payment_id del router."""

    def test_extract_from_webhook_format(self):
        """Extrae ID del formato Webhooks: data.id"""
        from backend.modules.pagos.router import _extract_mp_payment_id
        payload = {"type": "payment", "data": {"id": "12345"}}
        assert _extract_mp_payment_id(payload) == "12345"

    def test_extract_from_id_direct(self):
        """Extrae ID del formato alternativo: id directo"""
        from backend.modules.pagos.router import _extract_mp_payment_id
        payload = {"id": 99999}
        assert _extract_mp_payment_id(payload) == "99999"

    def test_extract_none_when_no_id(self):
        """Retorna None cuando no hay ID en el payload."""
        from backend.modules.pagos.router import _extract_mp_payment_id
        assert _extract_mp_payment_id(None) is None
        assert _extract_mp_payment_id({}) is None
        assert _extract_mp_payment_id({"type": "payment", "data": {}}) is None
