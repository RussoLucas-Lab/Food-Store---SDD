"""
Implementaciones PostgreSQL para pedidos:
- PostgreSQLPedidoRepository
- PostgreSQLDetallePedidoRepository
- PostgreSQLHistorialEstadoPedidoRepository
"""

from typing import List, Optional, Dict
from datetime import datetime, date
from sqlmodel import Session, select

from .model import Pedido, DetallePedido, HistorialEstadoPedido, EstadoPedidoEnum
from .sqlmodel_model import PedidoDB, DetallePedidoDB, HistorialEstadoPedidoDB


def _to_pedido_domain(db_obj: PedidoDB) -> Pedido:
    """Convertir PedidoDB → Pedido (dominio)."""
    return Pedido(
        id=db_obj.id,
        cliente_id=db_obj.cliente_id,
        estado=EstadoPedidoEnum(db_obj.estado),
        direccion_snapshot=db_obj.direccion_snapshot,
        total=db_obj.total,
        costo_envio=db_obj.costo_envio,
        creado_en=db_obj.creado_en,
        actualizado_en=db_obj.actualizado_en,
    )


def _to_detalle_domain(db_obj: DetallePedidoDB) -> DetallePedido:
    """Convertir DetallePedidoDB → DetallePedido (dominio)."""
    return DetallePedido(
        id=db_obj.id,
        pedido_id=db_obj.pedido_id,
        producto_id=db_obj.producto_id,
        nombre_snapshot=db_obj.nombre_snapshot,
        cantidad=db_obj.cantidad,
        precio_snapshot=db_obj.precio_snapshot,
        personalizacion=db_obj.personalizacion or [],
        creado_en=db_obj.creado_en,
    )


def _to_historial_domain(db_obj: HistorialEstadoPedidoDB) -> HistorialEstadoPedido:
    """Convertir HistorialEstadoPedidoDB → HistorialEstadoPedido (dominio)."""
    return HistorialEstadoPedido(
        id=db_obj.id,
        pedido_id=db_obj.pedido_id,
        estado_nuevo=EstadoPedidoEnum(db_obj.estado_nuevo),
        estado_anterior=EstadoPedidoEnum(db_obj.estado_anterior) if db_obj.estado_anterior else None,
        usuario_id=db_obj.usuario_id,
        observacion=db_obj.observacion,
        timestamp=db_obj.timestamp,
    )


class PostgreSQLPedidoRepository:
    """Repositorio PostgreSQL para Pedidos."""

    def __init__(self, session: Session):
        self._session = session

    def create(self, pedido: Pedido) -> Pedido:
        """Crear un nuevo pedido."""
        now = datetime.utcnow()
        db_obj = PedidoDB(
            cliente_id=pedido.cliente_id,
            estado=pedido.estado.value if isinstance(pedido.estado, EstadoPedidoEnum) else pedido.estado,
            direccion_snapshot=pedido.direccion_snapshot,
            total=pedido.total,
            costo_envio=pedido.costo_envio,
            creado_en=pedido.creado_en or now,
            actualizado_en=pedido.actualizado_en or now,
        )
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        result = _to_pedido_domain(db_obj)
        pedido.id = result.id  # Actualizar id en el objeto original
        return result

    def get_by_id(self, pedido_id: int) -> Optional[Pedido]:
        """Obtener pedido por ID."""
        db_obj = self._session.get(PedidoDB, pedido_id)
        return _to_pedido_domain(db_obj) if db_obj else None

    def list_by_cliente(self, cliente_id: int, skip: int = 0, limit: int = 10) -> List[Pedido]:
        """Listar pedidos de un cliente con paginación."""
        stmt = (
            select(PedidoDB)
            .where(PedidoDB.cliente_id == cliente_id)
            .order_by(PedidoDB.creado_en.desc())
            .offset(skip)
            .limit(limit)
        )
        db_objs = self._session.exec(stmt).all()
        return [_to_pedido_domain(obj) for obj in db_objs]

    def list_all(self, skip: int = 0, limit: int = 10) -> List[Pedido]:
        """Listar todos los pedidos con paginación."""
        stmt = (
            select(PedidoDB)
            .order_by(PedidoDB.creado_en.desc())
            .offset(skip)
            .limit(limit)
        )
        db_objs = self._session.exec(stmt).all()
        return [_to_pedido_domain(obj) for obj in db_objs]

    def update_estado(self, pedido_id: int, nuevo_estado: EstadoPedidoEnum) -> Optional[Pedido]:
        """Actualizar estado de un pedido."""
        db_obj = self._session.get(PedidoDB, pedido_id)
        if not db_obj:
            return None
        db_obj.estado = nuevo_estado.value if isinstance(nuevo_estado, EstadoPedidoEnum) else nuevo_estado
        db_obj.actualizado_en = datetime.utcnow()
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        return _to_pedido_domain(db_obj)

    def count_by_cliente(self, cliente_id: int) -> int:
        """Contar pedidos de un cliente."""
        db_objs = self._session.exec(
            select(PedidoDB).where(PedidoDB.cliente_id == cliente_id)
        ).all()
        return len(db_objs)

    def list_all_filtered(
        self,
        estado: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Pedido]:
        """Listar todos los pedidos con filtros opcionales."""
        stmt = select(PedidoDB)

        if estado:
            stmt = stmt.where(PedidoDB.estado == estado)

        if fecha_desde:
            from datetime import datetime as dt
            stmt = stmt.where(PedidoDB.creado_en >= dt(fecha_desde.year, fecha_desde.month, fecha_desde.day))

        if fecha_hasta:
            from datetime import datetime as dt, timedelta
            end = dt(fecha_hasta.year, fecha_hasta.month, fecha_hasta.day) + timedelta(days=1)
            stmt = stmt.where(PedidoDB.creado_en < end)

        stmt = stmt.order_by(PedidoDB.creado_en.desc()).offset(skip).limit(limit)
        db_objs = self._session.exec(stmt).all()
        return [_to_pedido_domain(obj) for obj in db_objs]


class PostgreSQLDetallePedidoRepository:
    """Repositorio PostgreSQL para Detalles de Pedido."""

    def __init__(self, session: Session):
        self._session = session

    def create(self, detalle: DetallePedido) -> DetallePedido:
        """Crear un nuevo detalle de pedido."""
        now = datetime.utcnow()
        db_obj = DetallePedidoDB(
            pedido_id=detalle.pedido_id,
            producto_id=detalle.producto_id,
            nombre_snapshot=detalle.nombre_snapshot,
            cantidad=detalle.cantidad,
            precio_snapshot=detalle.precio_snapshot,
            personalizacion=detalle.personalizacion or [],
            creado_en=detalle.creado_en or now,
        )
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        result = _to_detalle_domain(db_obj)
        detalle.id = result.id
        return result

    def get_by_id(self, detalle_id: int) -> Optional[DetallePedido]:
        """Obtener detalle por ID."""
        db_obj = self._session.get(DetallePedidoDB, detalle_id)
        return _to_detalle_domain(db_obj) if db_obj else None

    def list_by_pedido(self, pedido_id: int) -> List[DetallePedido]:
        """Listar todos los detalles de un pedido."""
        db_objs = self._session.exec(
            select(DetallePedidoDB).where(DetallePedidoDB.pedido_id == pedido_id)
        ).all()
        return [_to_detalle_domain(obj) for obj in db_objs]


class PostgreSQLHistorialEstadoPedidoRepository:
    """
    Repositorio PostgreSQL append-only para Historial de Estado de Pedido.

    Solo expone create() y list_by_pedido() — no existen update() ni delete().
    """

    def __init__(self, session: Session):
        self._session = session

    def create(self, historial: HistorialEstadoPedido) -> HistorialEstadoPedido:
        """Registrar nuevo evento de cambio de estado (append-only)."""
        now = datetime.utcnow()
        db_obj = HistorialEstadoPedidoDB(
            pedido_id=historial.pedido_id,
            estado_nuevo=historial.estado_nuevo.value if isinstance(historial.estado_nuevo, EstadoPedidoEnum) else historial.estado_nuevo,
            estado_anterior=historial.estado_anterior.value if isinstance(historial.estado_anterior, EstadoPedidoEnum) else historial.estado_anterior,
            usuario_id=historial.usuario_id,
            observacion=historial.observacion,
            timestamp=historial.timestamp or now,
        )
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        result = _to_historial_domain(db_obj)
        historial.id = result.id
        return result

    def list_by_pedido(self, pedido_id: int) -> List[HistorialEstadoPedido]:
        """Listar historial de un pedido ordenado cronológicamente."""
        db_objs = self._session.exec(
            select(HistorialEstadoPedidoDB)
            .where(HistorialEstadoPedidoDB.pedido_id == pedido_id)
            .order_by(HistorialEstadoPedidoDB.timestamp)
        ).all()
        return [_to_historial_domain(obj) for obj in db_objs]
