"""
Tests unitarios para PedidoService — módulo despacho-pedidos.

Cubre:
- advance_estado: FSM válida, saltos/retrocesos rechazados, terminales, PENDIENTE→CONFIRMADO bloqueada
- Autorización por rol: CLIENT, PEDIDOS, ADMIN
- Restauración de stock al cancelar CONFIRMADO/EN_PREPARACION
- Motivo obligatorio al cancelar
- Registro append-only en historial
- list_gestion con filtros
- get_order_detail respetando el rol
"""

import pytest
import json
from unittest.mock import Mock
from datetime import datetime, date

from backend.modules.pedidos.service import PedidoService
from backend.modules.pedidos.model import (
    Pedido,
    DetallePedido,
    HistorialEstadoPedido,
    EstadoPedidoEnum,
)
from backend.modules.pedidos.exceptions import (
    PedidoNotFound,
    UnauthorizedPedidoAccess,
    TransicionInvalida,
    RolNoAutorizadoParaTransicion,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_pedido(id: int, cliente_id: int, estado: EstadoPedidoEnum) -> Pedido:
    p = Pedido(cliente_id=cliente_id, estado=estado, total=100.0)
    p.id = id
    return p


def _make_detalle(pedido_id: int, producto_id: int, cantidad: int) -> DetallePedido:
    d = DetallePedido(
        pedido_id=pedido_id,
        producto_id=producto_id,
        nombre_snapshot="Producto Test",
        cantidad=cantidad,
        precio_snapshot=50.0,
    )
    d.id = 1
    return d


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_uow():
    uow = Mock()
    uow.pedidos = Mock()
    uow.detalles_pedido = Mock()
    uow.historial_estado = Mock()
    uow.productos = Mock()
    uow.clientes = Mock()
    uow.commit = Mock()
    uow.rollback = Mock()
    return uow


@pytest.fixture
def service(mock_uow):
    return PedidoService(mock_uow)


def _setup_advance(mock_uow, pedido: Pedido, detalles=None):
    """Configura los mocks básicos para advance_estado."""
    mock_uow.pedidos.get_by_id.return_value = pedido
    mock_uow.detalles_pedido.list_by_pedido.return_value = detalles or []
    mock_uow.productos.restore_stock.return_value = True

    def update_estado_side_effect(pid, nuevo_estado):
        pedido.estado = nuevo_estado
        return pedido

    mock_uow.pedidos.update_estado.side_effect = update_estado_side_effect

    historial_creados = []

    def historial_create(h):
        h.id = len(historial_creados) + 1
        historial_creados.append(h)
        return h

    mock_uow.historial_estado.create.side_effect = historial_create
    return historial_creados


# ══════════════════════════════════════════════════════════════════════════════
# Task 10.1 — Tests de advance_estado: FSM válida
# ══════════════════════════════════════════════════════════════════════════════

class TestAdvanceEstadoFSM:
    """Tests de la FSM — transiciones válidas e inválidas."""

    def test_confirmado_a_en_preparacion_ok(self, service, mock_uow):
        """CONFIRMADO → EN_PREPARACION es válida para ADMIN."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.CONFIRMADO)
        _setup_advance(mock_uow, pedido)

        result = service.advance_estado(1, "EN_PREPARACION", usuario_id=10, rol="ADMIN")

        assert result["estado"] == EstadoPedidoEnum.EN_PREPARACION.value
        mock_uow.commit.assert_called_once()

    def test_en_preparacion_a_en_camino_ok(self, service, mock_uow):
        """EN_PREPARACION → EN_CAMINO es válida para PEDIDOS."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.EN_PREPARACION)
        _setup_advance(mock_uow, pedido)

        result = service.advance_estado(1, "EN_CAMINO", usuario_id=10, rol="PEDIDOS")

        assert result["estado"] == EstadoPedidoEnum.EN_CAMINO.value
        mock_uow.commit.assert_called_once()

    def test_en_camino_a_entregado_ok(self, service, mock_uow):
        """EN_CAMINO → ENTREGADO es válida para PEDIDOS."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.EN_CAMINO)
        _setup_advance(mock_uow, pedido)

        result = service.advance_estado(1, "ENTREGADO", usuario_id=10, rol="PEDIDOS")

        assert result["estado"] == EstadoPedidoEnum.ENTREGADO.value
        mock_uow.commit.assert_called_once()

    def test_salto_de_estado_rechazado(self, service, mock_uow):
        """CONFIRMADO → EN_CAMINO (salto) lanza TransicionInvalida (HTTP 409)."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.CONFIRMADO)
        mock_uow.pedidos.get_by_id.return_value = pedido

        with pytest.raises(TransicionInvalida):
            service.advance_estado(1, "EN_CAMINO", usuario_id=10, rol="ADMIN")

        mock_uow.commit.assert_not_called()

    def test_retroceso_de_estado_rechazado(self, service, mock_uow):
        """EN_CAMINO → EN_PREPARACION (retroceso) lanza TransicionInvalida."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.EN_CAMINO)
        mock_uow.pedidos.get_by_id.return_value = pedido

        with pytest.raises(TransicionInvalida):
            service.advance_estado(1, "EN_PREPARACION", usuario_id=10, rol="ADMIN")

        mock_uow.commit.assert_not_called()

    def test_estado_terminal_entregado_rechaza_transicion(self, service, mock_uow):
        """ENTREGADO (terminal) → cualquier estado lanza TransicionInvalida."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.ENTREGADO)
        mock_uow.pedidos.get_by_id.return_value = pedido

        with pytest.raises(TransicionInvalida):
            service.advance_estado(1, "CONFIRMADO", usuario_id=10, rol="ADMIN")

        mock_uow.commit.assert_not_called()

    def test_estado_terminal_cancelado_rechaza_transicion(self, service, mock_uow):
        """CANCELADO (terminal) → cualquier estado lanza TransicionInvalida."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.CANCELADO)
        mock_uow.pedidos.get_by_id.return_value = pedido

        with pytest.raises(TransicionInvalida):
            service.advance_estado(1, "PENDIENTE", usuario_id=10, rol="ADMIN")

        mock_uow.commit.assert_not_called()

    def test_pendiente_a_confirmado_rechazado(self, service, mock_uow):
        """PENDIENTE → CONFIRMADO (manual) lanza TransicionInvalida (D2: es exclusiva del sistema)."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.PENDIENTE)
        mock_uow.pedidos.get_by_id.return_value = pedido

        with pytest.raises(TransicionInvalida):
            service.advance_estado(1, "CONFIRMADO", usuario_id=10, rol="ADMIN")

        mock_uow.commit.assert_not_called()

    def test_pedido_no_encontrado_lanza_pedido_not_found(self, service, mock_uow):
        """Pedido inexistente → PedidoNotFound."""
        mock_uow.pedidos.get_by_id.return_value = None

        with pytest.raises(PedidoNotFound):
            service.advance_estado(999, "EN_PREPARACION", usuario_id=10, rol="ADMIN")


# ══════════════════════════════════════════════════════════════════════════════
# Task 10.2 — Tests de autorización por rol
# ══════════════════════════════════════════════════════════════════════════════

class TestAdvanceEstadoAutorizacion:
    """Tests de autorización rol→transición (D3)."""

    def test_client_no_puede_avanzar_confirmado(self, service, mock_uow):
        """CLIENT no puede avanzar CONFIRMADO → EN_PREPARACION."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.CONFIRMADO)
        mock_uow.pedidos.get_by_id.return_value = pedido

        with pytest.raises(RolNoAutorizadoParaTransicion):
            service.advance_estado(1, "EN_PREPARACION", usuario_id=5, rol="CLIENT")

        mock_uow.commit.assert_not_called()

    def test_pedidos_no_puede_cancelar_desde_en_preparacion(self, service, mock_uow):
        """PEDIDOS no puede cancelar desde EN_PREPARACION (solo ADMIN)."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.EN_PREPARACION)
        mock_uow.pedidos.get_by_id.return_value = pedido

        with pytest.raises(RolNoAutorizadoParaTransicion):
            service.advance_estado(
                1, "CANCELADO", usuario_id=10, rol="PEDIDOS", motivo="Cancelar"
            )

        mock_uow.commit.assert_not_called()

    def test_admin_puede_cancelar_desde_en_preparacion(self, service, mock_uow):
        """ADMIN puede cancelar desde EN_PREPARACION (RN-FS08)."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.EN_PREPARACION)
        detalles = [_make_detalle(1, producto_id=10, cantidad=2)]
        _setup_advance(mock_uow, pedido, detalles)

        result = service.advance_estado(
            1, "CANCELADO", usuario_id=1, rol="ADMIN", motivo="Error en el pedido"
        )

        assert result["estado"] == EstadoPedidoEnum.CANCELADO.value
        mock_uow.commit.assert_called_once()

    def test_client_puede_cancelar_pedido_pendiente_propio(self, service, mock_uow):
        """CLIENT puede cancelar su propio pedido en PENDIENTE."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.PENDIENTE)
        _setup_advance(mock_uow, pedido)

        result = service.advance_estado(
            1, "CANCELADO", usuario_id=5, rol="CLIENT", motivo="Ya no lo necesito"
        )

        assert result["estado"] == EstadoPedidoEnum.CANCELADO.value
        mock_uow.commit.assert_called_once()

    def test_client_no_puede_cancelar_pedido_ajeno(self, service, mock_uow):
        """CLIENT no puede cancelar un pedido de otro cliente (ownership check)."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.PENDIENTE)
        mock_uow.pedidos.get_by_id.return_value = pedido

        with pytest.raises(UnauthorizedPedidoAccess):
            service.advance_estado(
                1, "CANCELADO", usuario_id=99, rol="CLIENT", motivo="..."
            )

        mock_uow.commit.assert_not_called()


# ══════════════════════════════════════════════════════════════════════════════
# Task 10.3 — Tests de restauración de stock
# ══════════════════════════════════════════════════════════════════════════════

class TestRestauracionStock:
    """Tests de restauración de stock al cancelar (D5)."""

    def test_cancelar_confirmado_restaura_stock(self, service, mock_uow):
        """Cancelar CONFIRMADO → restore_stock llamado por cada detalle."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.CONFIRMADO)
        detalles = [
            _make_detalle(1, producto_id=10, cantidad=3),
            _make_detalle(1, producto_id=20, cantidad=1),
        ]
        _setup_advance(mock_uow, pedido, detalles)

        service.advance_estado(
            1, "CANCELADO", usuario_id=1, rol="ADMIN", motivo="Error en pedido"
        )

        # restore_stock debe llamarse por cada detalle
        assert mock_uow.productos.restore_stock.call_count == 2
        mock_uow.productos.restore_stock.assert_any_call(10, 3)
        mock_uow.productos.restore_stock.assert_any_call(20, 1)

    def test_cancelar_en_preparacion_restaura_stock(self, service, mock_uow):
        """Cancelar EN_PREPARACION → restore_stock llamado (ADMIN)."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.EN_PREPARACION)
        detalles = [_make_detalle(1, producto_id=10, cantidad=2)]
        _setup_advance(mock_uow, pedido, detalles)

        service.advance_estado(
            1, "CANCELADO", usuario_id=1, rol="ADMIN", motivo="Problema de stock"
        )

        mock_uow.productos.restore_stock.assert_called_once_with(10, 2)

    def test_cancelar_pendiente_no_restaura_stock(self, service, mock_uow):
        """Cancelar PENDIENTE → stock NO se restaura (nunca se decrementó)."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.PENDIENTE)
        _setup_advance(mock_uow, pedido)

        service.advance_estado(
            1, "CANCELADO", usuario_id=5, rol="CLIENT", motivo="Cambié de opinión"
        )

        mock_uow.productos.restore_stock.assert_not_called()


# ══════════════════════════════════════════════════════════════════════════════
# Task 10.4 — Tests de motivo obligatorio y registro append-only
# ══════════════════════════════════════════════════════════════════════════════

class TestMotivoYHistorial:
    """Tests de motivo obligatorio y registro append-only de historial."""

    def test_historial_se_inserta_en_cada_transicion(self, service, mock_uow):
        """Cada transición exitosa inserta exactamente 1 registro de historial."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.CONFIRMADO)
        historial_creados = _setup_advance(mock_uow, pedido)

        service.advance_estado(1, "EN_PREPARACION", usuario_id=10, rol="ADMIN")

        assert len(historial_creados) == 1
        h = historial_creados[0]
        assert h.estado_anterior == EstadoPedidoEnum.CONFIRMADO
        assert h.estado_nuevo == EstadoPedidoEnum.EN_PREPARACION
        assert h.usuario_id == 10

    def test_historial_contiene_motivo_al_cancelar(self, service, mock_uow):
        """Al cancelar, el historial lleva el motivo en observacion."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.PENDIENTE)
        historial_creados = _setup_advance(mock_uow, pedido)

        service.advance_estado(
            1, "CANCELADO", usuario_id=5, rol="CLIENT", motivo="No quiero el pedido"
        )

        assert len(historial_creados) == 1
        assert historial_creados[0].observacion == "No quiero el pedido"
        assert historial_creados[0].estado_nuevo == EstadoPedidoEnum.CANCELADO

    def test_un_solo_commit_por_advance_estado(self, service, mock_uow):
        """advance_estado hace exactamente 1 commit al final (no por operación)."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.CONFIRMADO)
        detalles = [_make_detalle(1, producto_id=10, cantidad=2)]
        _setup_advance(mock_uow, pedido, detalles)

        service.advance_estado(
            1, "CANCELADO", usuario_id=1, rol="ADMIN", motivo="Test"
        )

        assert mock_uow.commit.call_count == 1


# ══════════════════════════════════════════════════════════════════════════════
# Task 10.6 — Tests de get_order_detail con rol
# ══════════════════════════════════════════════════════════════════════════════

class TestGetOrderDetailConRol:
    """Tests de get_order_detail respetando el rol (D8)."""

    def test_gestor_puede_ver_pedido_ajeno(self, service, mock_uow):
        """PEDIDOS puede ver el detalle de cualquier pedido sin restricción de ownership."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.CONFIRMADO)
        pedido.direccion_snapshot = json.dumps({"calle": "Av. Corrientes"})

        mock_uow.pedidos.get_by_id.return_value = pedido
        mock_uow.detalles_pedido.list_by_pedido.return_value = []
        mock_uow.historial_estado.list_by_pedido.return_value = []

        # usuario_id=99 es diferente al cliente_id=5, pero el rol PEDIDOS permite
        result = service.get_order_detail(pedido_id=1, cliente_id=99, rol="PEDIDOS")

        assert result["id"] == 1
        assert result["cliente_id"] == 5

    def test_admin_puede_ver_pedido_ajeno(self, service, mock_uow):
        """ADMIN puede ver el detalle de cualquier pedido."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.EN_PREPARACION)
        pedido.direccion_snapshot = json.dumps({"calle": "Av. Santa Fe"})

        mock_uow.pedidos.get_by_id.return_value = pedido
        mock_uow.detalles_pedido.list_by_pedido.return_value = []
        mock_uow.historial_estado.list_by_pedido.return_value = []

        result = service.get_order_detail(pedido_id=1, cliente_id=999, rol="ADMIN")

        assert result["id"] == 1

    def test_client_bloqueado_en_pedido_ajeno(self, service, mock_uow):
        """CLIENT recibe UnauthorizedPedidoAccess si intenta ver un pedido de otro."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.CONFIRMADO)
        mock_uow.pedidos.get_by_id.return_value = pedido

        with pytest.raises(UnauthorizedPedidoAccess):
            service.get_order_detail(pedido_id=1, cliente_id=99, rol="CLIENT")

    def test_client_puede_ver_propio_pedido(self, service, mock_uow):
        """CLIENT puede ver su propio pedido."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.PENDIENTE)
        pedido.direccion_snapshot = json.dumps({"calle": "Calle Falsa 123"})

        mock_uow.pedidos.get_by_id.return_value = pedido
        mock_uow.detalles_pedido.list_by_pedido.return_value = []
        mock_uow.historial_estado.list_by_pedido.return_value = []

        result = service.get_order_detail(pedido_id=1, cliente_id=5, rol="CLIENT")

        assert result["cliente_id"] == 5


# ══════════════════════════════════════════════════════════════════════════════
# Extra: Tests de list_gestion con filtros
# ══════════════════════════════════════════════════════════════════════════════

class TestListGestion:
    """Tests de PedidoService.list_gestion()."""

    def test_list_gestion_llama_repositorio_con_filtros(self, service, mock_uow):
        """list_gestion delega correctamente al repositorio con los filtros."""
        pedido = _make_pedido(1, cliente_id=5, estado=EstadoPedidoEnum.CONFIRMADO)
        mock_uow.pedidos.list_all_filtered.return_value = [pedido]

        result = service.list_gestion(estado="CONFIRMADO", skip=0, limit=10)

        mock_uow.pedidos.list_all_filtered.assert_called_once_with(
            estado="CONFIRMADO",
            fecha_desde=None,
            fecha_hasta=None,
            skip=0,
            limit=10,
        )
        assert len(result) == 1
        assert result[0]["estado"] == EstadoPedidoEnum.CONFIRMADO.value

    def test_list_gestion_sin_filtros(self, service, mock_uow):
        """list_gestion sin filtros retorna todos los pedidos."""
        mock_uow.pedidos.list_all_filtered.return_value = []

        result = service.list_gestion()

        assert result == []
        mock_uow.pedidos.list_all_filtered.assert_called_once_with(
            estado=None,
            fecha_desde=None,
            fecha_hasta=None,
            skip=0,
            limit=20,
        )
