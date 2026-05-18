"""
Tests unitarios para PedidoService.

Prueba toda la lógica de negocio sin dependencias de FastAPI.
Usa mocks del UoW y repositorios para aislar la lógica del servicio.
"""

import pytest
from unittest.mock import Mock
from datetime import datetime

from backend.modules.pedidos.service import PedidoService
from backend.modules.pedidos.model import (
    Pedido,
    DetallePedido,
    HistorialEstadoPedido,
    EstadoPedidoEnum,
)
from backend.modules.pedidos.schemas import CartCreateDTO, CartItemDTO, PersonalizacionDTO
from backend.modules.pedidos.exceptions import (
    CartEmptyError,
    StockInsufficient,
    PedidoNotFound,
    UnauthorizedPedidoAccess,
    DireccionNotFound,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_producto(id: int, nombre: str, base_price: float, stock: float = 100.0):
    """Crea un mock de Producto con atributos mínimos."""
    p = Mock()
    p.id = id
    p.nombre = nombre
    p.base_price = base_price
    p.stock = stock
    p.calculate_available_stock = Mock(return_value=stock)
    return p


def _make_cliente(id: int, nombre: str = "Cliente Test", direccion: str = "Calle 1234"):
    """Crea un mock de Cliente con atributos mínimos."""
    c = Mock()
    c.id = id
    c.nombre = nombre
    c.direccion = direccion
    c.telefono = "+54 11 1234 5678"
    c.to_dict = Mock(return_value={"id": id, "nombre": nombre, "direccion": direccion})
    return c


def _make_cart_dto(
    producto_id: int = 1,
    cantidad: int = 2,
    direccion_id: int = 10,
    excluidos: list = None,
) -> CartCreateDTO:
    """Construye un CartCreateDTO válido."""
    return CartCreateDTO(
        items=[
            CartItemDTO(
                producto_id=producto_id,
                cantidad=cantidad,
                personalizacion=PersonalizacionDTO(excluidos=excluidos or []),
            )
        ],
        direccion_id=direccion_id,
    )


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_uow():
    """Mock Unit of Work con repositorios de pedidos."""
    uow = Mock()
    uow.productos = Mock()
    uow.clientes = Mock()
    uow.pedidos = Mock()
    uow.detalles_pedido = Mock()
    uow.historial_estado = Mock()
    uow.commit = Mock()
    uow.rollback = Mock()
    return uow


@pytest.fixture
def service(mock_uow):
    """PedidoService con mock UoW."""
    return PedidoService(mock_uow)


@pytest.fixture
def valid_cart_dto():
    """CartCreateDTO válido con un ítem."""
    return _make_cart_dto(producto_id=1, cantidad=2, direccion_id=10)


# ── Tests: create_order ────────────────────────────────────────────────────────

class TestCreateOrder:
    """Tests para PedidoService.create_order()"""

    def test_create_order_valid_returns_pedido_pendiente(self, service, mock_uow, valid_cart_dto):
        """9.2.1: create_order con carrito válido → retorna pedido con estado PENDIENTE."""
        producto = _make_producto(1, "Pizza Margherita", 150.0, stock=10)
        cliente = _make_cliente(5)

        # Configurar repos mock
        mock_uow.productos.find_by_id.return_value = producto
        mock_uow.clientes.find_by_id.return_value = cliente

        # create del repo asigna ID y retorna el mismo objeto
        def pedido_create(p):
            p.id = 1
            return p
        mock_uow.pedidos.create.side_effect = pedido_create

        def detalle_create(d):
            d.id = 1
            return d
        mock_uow.detalles_pedido.create.side_effect = detalle_create

        def historial_create(h):
            h.id = 1
            return h
        mock_uow.historial_estado.create.side_effect = historial_create

        result = service.create_order(cliente_id=5, carrito_dto=valid_cart_dto)

        assert result["estado"] == EstadoPedidoEnum.PENDIENTE.value
        assert result["cliente_id"] == 5
        assert result["id"] == 1
        mock_uow.commit.assert_called_once()

    def test_create_order_empty_cart_raises_cart_empty_error(self, service, mock_uow):
        """9.2.2: create_order con carrito vacío → lanza CartEmptyError."""
        # CartCreateDTO con items vacío viola min_items=1, pero probamos la validación del service
        # directamente usando un mock del dto
        dto = Mock()
        dto.items = []
        with pytest.raises(CartEmptyError):
            service.create_order(cliente_id=1, carrito_dto=dto)

    def test_create_order_insufficient_stock_raises_stock_insufficient(self, service, mock_uow):
        """9.2.3: create_order con stock insuficiente → lanza StockInsufficient."""
        producto = _make_producto(1, "Pizza", 100.0, stock=1)
        mock_uow.productos.find_by_id.return_value = producto

        dto = _make_cart_dto(producto_id=1, cantidad=5)  # pide 5, solo hay 1

        with pytest.raises(StockInsufficient):
            service.create_order(cliente_id=1, carrito_dto=dto)

        mock_uow.commit.assert_not_called()

    def test_create_order_invalid_direction_raises_direccion_not_found(self, service, mock_uow):
        """9.2.4: create_order con cliente inexistente → lanza DireccionNotFound."""
        producto = _make_producto(1, "Pizza", 100.0, stock=10)
        mock_uow.productos.find_by_id.return_value = producto
        mock_uow.clientes.find_by_id.return_value = None  # Cliente no encontrado

        dto = _make_cart_dto(producto_id=1, cantidad=1, direccion_id=99)

        with pytest.raises(DireccionNotFound):
            service.create_order(cliente_id=1, carrito_dto=dto)

        mock_uow.commit.assert_not_called()

    def test_create_order_snapshots_are_immutable(self, service, mock_uow):
        """9.2.5: Los snapshots de precio y nombre no cambian si el producto se modifica después."""
        producto = _make_producto(1, "Pizza Original", 100.0, stock=10)
        cliente = _make_cliente(5)

        mock_uow.productos.find_by_id.return_value = producto
        mock_uow.clientes.find_by_id.return_value = cliente

        detalles_creados = []

        def pedido_create(p):
            p.id = 1
            return p
        mock_uow.pedidos.create.side_effect = pedido_create

        def detalle_create(d):
            d.id = 1
            detalles_creados.append(d)
            return d
        mock_uow.detalles_pedido.create.side_effect = detalle_create

        def historial_create(h):
            h.id = 1
            return h
        mock_uow.historial_estado.create.side_effect = historial_create

        dto = _make_cart_dto(producto_id=1, cantidad=1)
        service.create_order(cliente_id=5, carrito_dto=dto)

        # Simulamos que el producto cambió después
        producto.nombre = "Pizza Modificada"
        producto.base_price = 999.0

        # Los snapshots del detalle deben conservar los valores originales
        assert len(detalles_creados) == 1
        assert detalles_creados[0].nombre_snapshot == "Pizza Original"
        assert detalles_creados[0].precio_snapshot == 100.0

    def test_create_order_creates_initial_historial_estado_none(self, service, mock_uow):
        """9.2.9: El historial tiene exactamente un registro inicial con estado_anterior=None y estado_nuevo=PENDIENTE."""
        producto = _make_producto(1, "Pizza", 100.0, stock=10)
        cliente = _make_cliente(5)
        mock_uow.productos.find_by_id.return_value = producto
        mock_uow.clientes.find_by_id.return_value = cliente

        historial_creados = []

        def pedido_create(p):
            p.id = 1
            return p
        mock_uow.pedidos.create.side_effect = pedido_create

        def detalle_create(d):
            d.id = 1
            return d
        mock_uow.detalles_pedido.create.side_effect = detalle_create

        def historial_create(h):
            h.id = 1
            historial_creados.append(h)
            return h
        mock_uow.historial_estado.create.side_effect = historial_create

        dto = _make_cart_dto(producto_id=1, cantidad=1)
        service.create_order(cliente_id=5, carrito_dto=dto)

        assert len(historial_creados) == 1
        assert historial_creados[0].estado_anterior is None
        assert historial_creados[0].estado_nuevo == EstadoPedidoEnum.PENDIENTE


# ── Tests: list_orders ─────────────────────────────────────────────────────────

class TestListOrders:
    """Tests para PedidoService.list_orders()"""

    def test_list_orders_returns_only_own_orders(self, service, mock_uow):
        """9.2.6: list_orders solo retorna pedidos del cliente correcto."""
        pedido_cliente_5 = Pedido(cliente_id=5, total=100.0)
        pedido_cliente_5.id = 1

        mock_uow.pedidos.list_by_cliente.return_value = [pedido_cliente_5]

        result = service.list_orders(cliente_id=5)

        assert len(result) == 1
        assert result[0]["cliente_id"] == 5
        mock_uow.pedidos.list_by_cliente.assert_called_once_with(5, skip=0, limit=10)

    def test_list_orders_empty_when_no_orders(self, service, mock_uow):
        """list_orders retorna lista vacía cuando no hay pedidos."""
        mock_uow.pedidos.list_by_cliente.return_value = []

        result = service.list_orders(cliente_id=99)

        assert result == []


# ── Tests: get_order_detail ────────────────────────────────────────────────────

class TestGetOrderDetail:
    """Tests para PedidoService.get_order_detail()"""

    def test_get_order_detail_own_order(self, service, mock_uow):
        """get_order_detail retorna detalle completo del pedido propio."""
        import json
        pedido = Pedido(cliente_id=5, total=200.0)
        pedido.id = 10
        pedido.direccion_snapshot = json.dumps({"direccion": "Calle 123"})

        mock_uow.pedidos.get_by_id.return_value = pedido
        mock_uow.detalles_pedido.list_by_pedido.return_value = []
        mock_uow.historial_estado.list_by_pedido.return_value = []

        result = service.get_order_detail(pedido_id=10, cliente_id=5)

        assert result["id"] == 10
        assert result["cliente_id"] == 5
        assert "detalles" in result
        assert "historial" in result
        assert isinstance(result["direccion_snapshot"], dict)

    def test_get_order_detail_other_client_raises_unauthorized(self, service, mock_uow):
        """9.2.7: get_order_detail de pedido ajeno → lanza UnauthorizedPedidoAccess."""
        pedido = Pedido(cliente_id=5, total=200.0)
        pedido.id = 10
        mock_uow.pedidos.get_by_id.return_value = pedido

        with pytest.raises(UnauthorizedPedidoAccess):
            service.get_order_detail(pedido_id=10, cliente_id=99)  # cliente_id diferente

    def test_get_order_detail_not_found_raises_pedido_not_found(self, service, mock_uow):
        """9.2.8: get_order_detail de pedido inexistente → lanza PedidoNotFound."""
        mock_uow.pedidos.get_by_id.return_value = None

        with pytest.raises(PedidoNotFound):
            service.get_order_detail(pedido_id=999, cliente_id=5)
