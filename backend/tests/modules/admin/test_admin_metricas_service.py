"""
Tests unitarios para AdminMetricasService.

Verifica:
- Resumen excluye pedidos PENDIENTE/CANCELADO
- Serie temporal agrupa por granularidad
- Top productos ordenado desc
- Distribución por estado
- Rango de fechas invertido lanza HTTP 422
"""

import pytest
from unittest.mock import MagicMock
from datetime import datetime, date

from backend.modules.admin.service import AdminMetricasService
from backend.modules.pedidos.model import Pedido, DetallePedido, EstadoPedidoEnum
from backend.modules.productos.model import Product


def _make_uow(pedidos=None, detalles=None, usuarios=None, productos=None):
    """Crear mock UoW con datos de test."""
    uow = MagicMock()
    uow.pedidos._storage = {p.id: p for p in (pedidos or [])}
    uow.detalles_pedido._storage = {d.id: d for d in (detalles or [])}
    uow.usuarios._storage = {u["id"]: MagicMock(id=u["id"]) for u in (usuarios or [])}
    uow.productos._storage = {}
    for prod in (productos or []):
        m = MagicMock()
        m.id = prod["id"]
        m.stock = prod.get("stock", 10)
        uow.productos._storage[prod["id"]] = m
    return uow


def _make_pedido(id, estado, total, creado_en=None):
    p = Pedido(
        id=id,
        cliente_id=1,
        estado=estado,
        total=total,
        costo_envio=0.0,
        direccion_snapshot="{}",
        creado_en=creado_en or datetime(2026, 1, 15, 10, 0),
        actualizado_en=creado_en or datetime(2026, 1, 15, 10, 0),
    )
    return p


class TestResumenExcluyeNoEfectivos:
    """Resumen de métricas solo cuenta pedidos en estados de venta efectiva."""

    def test_excluye_pendiente(self):
        pedidos = [
            _make_pedido(1, EstadoPedidoEnum.PENDIENTE, 100.0),
            _make_pedido(2, EstadoPedidoEnum.CONFIRMADO, 200.0),
        ]
        uow = _make_uow(pedidos=pedidos)
        service = AdminMetricasService(uow)
        result = service.get_resumen()
        assert result["ventas_totales"] == 200.0
        assert result["cantidad_pedidos"] == 1

    def test_excluye_cancelado(self):
        pedidos = [
            _make_pedido(1, EstadoPedidoEnum.CANCELADO, 500.0),
            _make_pedido(2, EstadoPedidoEnum.ENTREGADO, 300.0),
        ]
        uow = _make_uow(pedidos=pedidos)
        service = AdminMetricasService(uow)
        result = service.get_resumen()
        assert result["ventas_totales"] == 300.0
        assert result["cantidad_pedidos"] == 1

    def test_incluye_en_preparacion(self):
        pedidos = [
            _make_pedido(1, EstadoPedidoEnum.EN_PREPARACION, 150.0),
            _make_pedido(2, EstadoPedidoEnum.EN_CAMINO, 250.0),
        ]
        uow = _make_uow(pedidos=pedidos)
        service = AdminMetricasService(uow)
        result = service.get_resumen()
        assert result["ventas_totales"] == 400.0
        assert result["cantidad_pedidos"] == 2

    def test_productos_sin_stock(self):
        pedidos = []
        uow = _make_uow(
            pedidos=pedidos,
            productos=[{"id": 1, "stock": 0}, {"id": 2, "stock": 5}, {"id": 3, "stock": 0}]
        )
        service = AdminMetricasService(uow)
        result = service.get_resumen()
        assert result["productos_sin_stock"] == 2


class TestSerieTemporalGranularidad:
    """Serie temporal de ventas agrupada por granularidad."""

    def test_granularidad_dia(self):
        pedidos = [
            _make_pedido(1, EstadoPedidoEnum.CONFIRMADO, 100.0, datetime(2026, 1, 10)),
            _make_pedido(2, EstadoPedidoEnum.CONFIRMADO, 200.0, datetime(2026, 1, 10)),
            _make_pedido(3, EstadoPedidoEnum.CONFIRMADO, 150.0, datetime(2026, 1, 11)),
        ]
        uow = _make_uow(pedidos=pedidos)
        service = AdminMetricasService(uow)
        serie = service.get_serie_temporal(None, None, "dia")
        assert len(serie) == 2
        assert serie[0]["periodo"] == "2026-01-10"
        assert serie[0]["monto"] == 300.0
        assert serie[1]["periodo"] == "2026-01-11"
        assert serie[1]["monto"] == 150.0

    def test_granularidad_mes(self):
        pedidos = [
            _make_pedido(1, EstadoPedidoEnum.CONFIRMADO, 100.0, datetime(2026, 1, 5)),
            _make_pedido(2, EstadoPedidoEnum.CONFIRMADO, 200.0, datetime(2026, 1, 20)),
            _make_pedido(3, EstadoPedidoEnum.CONFIRMADO, 300.0, datetime(2026, 2, 10)),
        ]
        uow = _make_uow(pedidos=pedidos)
        service = AdminMetricasService(uow)
        serie = service.get_serie_temporal(None, None, "mes")
        assert len(serie) == 2
        assert serie[0]["periodo"] == "2026-01-01"
        assert serie[0]["monto"] == 300.0

    def test_filtro_fechas(self):
        pedidos = [
            _make_pedido(1, EstadoPedidoEnum.CONFIRMADO, 100.0, datetime(2026, 1, 1)),
            _make_pedido(2, EstadoPedidoEnum.CONFIRMADO, 200.0, datetime(2026, 1, 15)),
            _make_pedido(3, EstadoPedidoEnum.CONFIRMADO, 300.0, datetime(2026, 2, 1)),
        ]
        uow = _make_uow(pedidos=pedidos)
        service = AdminMetricasService(uow)
        serie = service.get_serie_temporal(
            desde=date(2026, 1, 10),
            hasta=date(2026, 1, 31),
            granularidad="dia"
        )
        # Solo el pedido del 15 de enero
        assert len(serie) == 1
        assert serie[0]["monto"] == 200.0

    def test_rango_invertido_lanza_422(self):
        uow = _make_uow()
        service = AdminMetricasService(uow)
        with pytest.raises(Exception) as exc:
            service.get_serie_temporal(
                desde=date(2026, 2, 1),
                hasta=date(2026, 1, 1),
                granularidad="dia"
            )
        assert exc.value.status_code == 422


class TestTopProductos:
    """Ranking de productos más vendidos."""

    def test_ordenado_desc(self):
        pedidos = [
            _make_pedido(1, EstadoPedidoEnum.CONFIRMADO, 100.0),
        ]
        detalles = [
            DetallePedido(id=1, pedido_id=1, producto_id=1, nombre_snapshot="Pizza", cantidad=5, precio_snapshot=10.0),
            DetallePedido(id=2, pedido_id=1, producto_id=2, nombre_snapshot="Empanada", cantidad=10, precio_snapshot=5.0),
            DetallePedido(id=3, pedido_id=1, producto_id=3, nombre_snapshot="Milanesa", cantidad=3, precio_snapshot=20.0),
        ]
        uow = _make_uow(pedidos=pedidos, detalles=detalles)
        service = AdminMetricasService(uow)
        top = service.get_top_productos(top=10, desde=None, hasta=None)
        assert top[0]["producto_id"] == 2  # 10 unidades
        assert top[1]["producto_id"] == 1  # 5 unidades
        assert top[2]["producto_id"] == 3  # 3 unidades

    def test_excluye_pedidos_no_efectivos(self):
        pedidos = [
            _make_pedido(1, EstadoPedidoEnum.PENDIENTE, 100.0),
            _make_pedido(2, EstadoPedidoEnum.CONFIRMADO, 200.0),
        ]
        detalles = [
            DetallePedido(id=1, pedido_id=1, producto_id=1, nombre_snapshot="Pizza", cantidad=100, precio_snapshot=10.0),
            DetallePedido(id=2, pedido_id=2, producto_id=2, nombre_snapshot="Empanada", cantidad=5, precio_snapshot=5.0),
        ]
        uow = _make_uow(pedidos=pedidos, detalles=detalles)
        service = AdminMetricasService(uow)
        top = service.get_top_productos(top=10, desde=None, hasta=None)
        assert len(top) == 1
        assert top[0]["producto_id"] == 2


class TestDistribucionEstados:
    """Distribución de pedidos agrupados por estado."""

    def test_cuenta_por_estado(self):
        pedidos = [
            _make_pedido(1, EstadoPedidoEnum.PENDIENTE, 100.0),
            _make_pedido(2, EstadoPedidoEnum.PENDIENTE, 100.0),
            _make_pedido(3, EstadoPedidoEnum.CONFIRMADO, 200.0),
            _make_pedido(4, EstadoPedidoEnum.CANCELADO, 50.0),
        ]
        uow = _make_uow(pedidos=pedidos)
        service = AdminMetricasService(uow)
        dist = service.get_distribucion_estados(None, None)
        estado_map = {d["estado"]: d["cantidad"] for d in dist}
        assert estado_map.get("PENDIENTE") == 2
        assert estado_map.get("CONFIRMADO") == 1
        assert estado_map.get("CANCELADO") == 1

    def test_filtro_fechas(self):
        pedidos = [
            _make_pedido(1, EstadoPedidoEnum.PENDIENTE, 100.0, datetime(2026, 1, 5)),
            _make_pedido(2, EstadoPedidoEnum.CONFIRMADO, 200.0, datetime(2026, 2, 5)),
        ]
        uow = _make_uow(pedidos=pedidos)
        service = AdminMetricasService(uow)
        dist = service.get_distribucion_estados(
            desde=date(2026, 2, 1),
            hasta=date(2026, 2, 28)
        )
        assert len(dist) == 1
        assert dist[0]["estado"] == "CONFIRMADO"
