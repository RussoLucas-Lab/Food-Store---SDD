"""
Tests unitarios para PagoService.create_payment.

Casos cubiertos:
- Caso exitoso: pedido válido + PENDIENTE → crea pago y retorna PagoResponse
- Pedido no PENDIENTE → lanza PedidoNotPendiente
- Pedido no encontrado / no pertenece al cliente → lanza PedidoNotFound
- Pago ya existente (idempotencia) → retorna pago existente sin crear nuevo
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from backend.modules.pagos.service import PagoService
from backend.modules.pagos.model import Pago
from backend.modules.pagos.schemas import PagoCreateDTO, PagoResponse
from backend.modules.pagos.exceptions import (
    PedidoNotPendiente,
    PedidoNotFound,
)
from backend.modules.pedidos.model import Pedido, EstadoPedidoEnum


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_pedido(
    id: int,
    cliente_id: int,
    estado: EstadoPedidoEnum = EstadoPedidoEnum.PENDIENTE,
    total: float = 500.0,
) -> Pedido:
    """Crea un Pedido de prueba."""
    pedido = Pedido(cliente_id=cliente_id, total=total, estado=estado)
    pedido.id = id
    return pedido


def _make_pago(id: int, pedido_id: int, mp_status: str = "pending") -> Pago:
    """Crea un Pago de prueba."""
    pago = Pago(
        pedido_id=pedido_id,
        external_reference="ext-ref-uuid",
        idempotency_key="idempotency-uuid",
        mp_payment_id="mp-12345",
        mp_status=mp_status,
    )
    pago.id = id
    pago.creado_en = datetime.utcnow()
    return pago


def _make_dto(pedido_id: int = 1) -> PagoCreateDTO:
    """Crea un PagoCreateDTO válido."""
    return PagoCreateDTO(
        pedido_id=pedido_id,
        token="card_token_abc",
        installments=1,
        payment_method_id="visa",
    )


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_uow():
    """Mock Unit of Work con repositorios de pagos y pedidos."""
    uow = Mock()
    uow.pedidos = Mock()
    uow.pagos = Mock()
    uow.commit = Mock()
    uow.rollback = Mock()
    return uow


@pytest.fixture
def service(mock_uow):
    """PagoService con mock UoW."""
    return PagoService(mock_uow)


# ── Tests: create_payment ─────────────────────────────────────────────────────

class TestCreatePayment:
    """Tests para PagoService.create_payment()"""

    def test_create_payment_success(self, service, mock_uow):
        """
        Caso exitoso: pedido existente en PENDIENTE perteneciente al cliente →
        crea pago, llama SDK MP, persiste Pago, hace commit, retorna PagoResponse.
        """
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.PENDIENTE, total=500.0)
        dto = _make_dto(pedido_id=1)

        mock_uow.pedidos.get_by_id.return_value = pedido
        mock_uow.pagos.get_by_pedido_id.return_value = None  # Sin pago previo

        pago_creado = _make_pago(1, pedido_id=1, mp_status="pending")

        def pagos_create(p):
            p.id = 1
            p.creado_en = datetime.utcnow()
            return p
        mock_uow.pagos.create.side_effect = pagos_create

        # Parchear SDK de MP para que no falle (retorna pending)
        with patch.object(service, '_call_mercadopago_sdk', return_value={"id": None, "status": "pending"}):
            result = service.create_payment(cliente_id=5, dto=dto)

        assert isinstance(result, PagoResponse)
        assert result.pedido_id == 1
        assert result.mp_status == "pending"
        mock_uow.pagos.create.assert_called_once()
        mock_uow.commit.assert_called_once()

    def test_create_payment_pedido_not_found(self, service, mock_uow):
        """
        Pedido no existe → lanza PedidoNotFound.
        """
        mock_uow.pedidos.get_by_id.return_value = None
        dto = _make_dto(pedido_id=999)

        with pytest.raises(PedidoNotFound):
            service.create_payment(cliente_id=5, dto=dto)

        mock_uow.commit.assert_not_called()

    def test_create_payment_pedido_belongs_to_other_client(self, service, mock_uow):
        """
        Pedido existe pero pertenece a otro cliente → lanza PedidoNotFound
        (no revelar que el pedido existe — seguridad).
        """
        pedido = _make_pedido(1, cliente_id=99, estado=EstadoPedidoEnum.PENDIENTE)
        mock_uow.pedidos.get_by_id.return_value = pedido
        dto = _make_dto(pedido_id=1)

        with pytest.raises(PedidoNotFound):
            service.create_payment(cliente_id=5, dto=dto)  # cliente_id diferente al del pedido

        mock_uow.commit.assert_not_called()

    def test_create_payment_pedido_not_pendiente(self, service, mock_uow):
        """
        Pedido existe y pertenece al cliente pero NO está en PENDIENTE →
        lanza PedidoNotPendiente.
        """
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.CONFIRMADO)
        mock_uow.pedidos.get_by_id.return_value = pedido
        dto = _make_dto(pedido_id=1)

        with pytest.raises(PedidoNotPendiente):
            service.create_payment(cliente_id=5, dto=dto)

        mock_uow.commit.assert_not_called()
        mock_uow.pagos.create.assert_not_called()

    def test_create_payment_pedido_cancelado_raises_not_pendiente(self, service, mock_uow):
        """
        Pedido CANCELADO → también lanza PedidoNotPendiente.
        """
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.CANCELADO)
        mock_uow.pedidos.get_by_id.return_value = pedido
        dto = _make_dto(pedido_id=1)

        with pytest.raises(PedidoNotPendiente):
            service.create_payment(cliente_id=5, dto=dto)

    def test_create_payment_idempotency_returns_existing(self, service, mock_uow):
        """
        Ya existe un pago para el pedido → retorna el pago existente sin crear uno nuevo.
        Garantiza idempotencia: el mismo pedido no genera dos pagos.
        """
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.PENDIENTE)
        pago_existente = _make_pago(10, pedido_id=1, mp_status="pending")

        mock_uow.pedidos.get_by_id.return_value = pedido
        mock_uow.pagos.get_by_pedido_id.return_value = pago_existente
        dto = _make_dto(pedido_id=1)

        result = service.create_payment(cliente_id=5, dto=dto)

        # Retorna el existente — no crea uno nuevo
        assert result.id == 10
        assert result.pedido_id == 1
        mock_uow.pagos.create.assert_not_called()
        mock_uow.commit.assert_not_called()

    def test_create_payment_calls_uow_commit(self, service, mock_uow):
        """
        En caso exitoso, el service llama uow.commit() exactamente una vez.
        El service NO hace session.commit() directamente.
        """
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.PENDIENTE, total=200.0)
        mock_uow.pedidos.get_by_id.return_value = pedido
        mock_uow.pagos.get_by_pedido_id.return_value = None

        def pagos_create(p):
            p.id = 1
            p.creado_en = datetime.utcnow()
            return p
        mock_uow.pagos.create.side_effect = pagos_create

        with patch.object(service, '_call_mercadopago_sdk', return_value={"id": None, "status": "pending"}):
            service.create_payment(cliente_id=5, dto=_make_dto(pedido_id=1))

        mock_uow.commit.assert_called_once()
