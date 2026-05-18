"""
Repositorios in-memory para Pedidos.

Implementa:
- InMemoryPedidoRepository: CRUD para pedidos
- InMemoryDetallePedidoRepository: CRUD para detalles de pedido
- InMemoryHistorialEstadoPedidoRepository: append-only para historial (solo CREATE)
"""

from typing import List, Optional, Dict
from datetime import datetime, date
from .model import Pedido, DetallePedido, HistorialEstadoPedido, EstadoPedidoEnum


class InMemoryPedidoRepository:
    """
    Repositorio in-memory para operaciones sobre Pedidos.
    Consistente con el patrón InMemoryXRepository del proyecto.
    """

    def __init__(self):
        self._storage: Dict[int, Pedido] = {}
        self._next_id = 1

    def create(self, pedido: Pedido) -> Pedido:
        """Crear un nuevo pedido asignando ID autoincremental."""
        pedido.id = self._next_id
        self._next_id += 1
        self._storage[pedido.id] = pedido
        return pedido

    def get_by_id(self, pedido_id: int) -> Optional[Pedido]:
        """Obtener pedido por ID."""
        return self._storage.get(pedido_id)

    def list_by_cliente(self, cliente_id: int, skip: int = 0, limit: int = 10) -> List[Pedido]:
        """Listar pedidos de un cliente con paginación, ordenado por creado_en DESC."""
        pedidos = [p for p in self._storage.values() if p.cliente_id == cliente_id]
        pedidos.sort(key=lambda p: p.creado_en, reverse=True)
        return pedidos[skip:skip + limit]

    def list_all(self, skip: int = 0, limit: int = 10) -> List[Pedido]:
        """Listar todos los pedidos con paginación, ordenado por creado_en DESC."""
        pedidos = sorted(self._storage.values(), key=lambda p: p.creado_en, reverse=True)
        return pedidos[skip:skip + limit]

    def update_estado(self, pedido_id: int, nuevo_estado: EstadoPedidoEnum) -> Optional[Pedido]:
        """Actualizar estado de un pedido y su timestamp de actualización."""
        pedido = self._storage.get(pedido_id)
        if pedido:
            pedido.estado = nuevo_estado
            pedido.actualizado_en = datetime.utcnow()
        return pedido

    def count_by_cliente(self, cliente_id: int) -> int:
        """Contar pedidos de un cliente."""
        return len([p for p in self._storage.values() if p.cliente_id == cliente_id])

    def list_all_filtered(
        self,
        estado: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Pedido]:
        """
        Listar todos los pedidos con filtros opcionales, para gestores.

        Filtros opcionales:
        - estado: valor del EstadoPedidoEnum (e.g. "CONFIRMADO")
        - fecha_desde / fecha_hasta: rango de fechas de creación (inclusive)
        - skip / limit: paginación

        Retorna lista ordenada por creado_en DESC.
        """
        pedidos = list(self._storage.values())

        if estado:
            pedidos = [p for p in pedidos if p.estado.value == estado]

        if fecha_desde:
            pedidos = [
                p for p in pedidos
                if p.creado_en.date() >= fecha_desde
            ]

        if fecha_hasta:
            pedidos = [
                p for p in pedidos
                if p.creado_en.date() <= fecha_hasta
            ]

        pedidos.sort(key=lambda p: p.creado_en, reverse=True)
        return pedidos[skip:skip + limit]


class InMemoryDetallePedidoRepository:
    """
    Repositorio in-memory para operaciones sobre Detalles de Pedido.
    """

    def __init__(self):
        self._storage: Dict[int, DetallePedido] = {}
        self._next_id = 1

    def create(self, detalle: DetallePedido) -> DetallePedido:
        """Crear un nuevo detalle de pedido asignando ID autoincremental."""
        detalle.id = self._next_id
        self._next_id += 1
        self._storage[detalle.id] = detalle
        return detalle

    def get_by_id(self, detalle_id: int) -> Optional[DetallePedido]:
        """Obtener detalle por ID."""
        return self._storage.get(detalle_id)

    def list_by_pedido(self, pedido_id: int) -> List[DetallePedido]:
        """Listar todos los detalles de un pedido."""
        return [d for d in self._storage.values() if d.pedido_id == pedido_id]


class InMemoryHistorialEstadoPedidoRepository:
    """
    Repositorio in-memory append-only para Historial de Estado de Pedido.

    ⚠️ APPEND-ONLY: Solo se expone el método create().
    No existen métodos update() ni delete() — esto es intencional.
    """

    def __init__(self):
        self._storage: Dict[int, HistorialEstadoPedido] = {}
        self._next_id = 1

    def create(self, historial: HistorialEstadoPedido) -> HistorialEstadoPedido:
        """Registrar nuevo evento de cambio de estado (append-only, el único método de escritura)."""
        historial.id = self._next_id
        self._next_id += 1
        self._storage[historial.id] = historial
        return historial

    def list_by_pedido(self, pedido_id: int) -> List[HistorialEstadoPedido]:
        """Listar historial de un pedido ordenado cronológicamente (timestamp ASC)."""
        historial = [h for h in self._storage.values() if h.pedido_id == pedido_id]
        historial.sort(key=lambda h: h.timestamp)
        return historial
