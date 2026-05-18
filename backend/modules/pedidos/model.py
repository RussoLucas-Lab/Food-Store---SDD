"""
Modelos Python puros para Pedidos (órdenes).

Estructura:
- EstadoPedidoEnum: estados válidos del pedido (FSM)
- Pedido: orden principal con estado, dirección snapshot, total, costo_envio
- DetallePedido: líneas de pedido con nombre_snapshot, precio_snapshot y personalización
- HistorialEstadoPedido: append-only audit trail de cambios de estado
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class EstadoPedidoEnum(str, Enum):
    """Estados válidos para un pedido (FSM unidireccional)."""
    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    EN_PREPARACION = "EN_PREPARACION"
    EN_CAMINO = "EN_CAMINO"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


class Pedido:
    """
    Modelo de Pedido (Orden).

    Representa una orden de compra del cliente, con snapshot inmutable
    de la dirección de entrega y totales calculados al momento de la compra.
    """

    def __init__(
        self,
        cliente_id: int,
        estado: EstadoPedidoEnum = EstadoPedidoEnum.PENDIENTE,
        direccion_snapshot: str = "",
        total: float = 0.0,
        costo_envio: float = 0.0,
        id: Optional[int] = None,
        creado_en: Optional[datetime] = None,
        actualizado_en: Optional[datetime] = None,
    ):
        self.id = id
        self.cliente_id = cliente_id
        self.estado = estado if isinstance(estado, EstadoPedidoEnum) else EstadoPedidoEnum(estado)
        self.direccion_snapshot = direccion_snapshot  # JSON string inmutable
        self.total = float(total)
        self.costo_envio = float(costo_envio)
        self.creado_en = creado_en or datetime.utcnow()
        self.actualizado_en = actualizado_en or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Serializa Pedido a diccionario serializable."""
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "estado": self.estado.value if isinstance(self.estado, EstadoPedidoEnum) else self.estado,
            "direccion_snapshot": self.direccion_snapshot,
            "total": float(self.total),
            "costo_envio": float(self.costo_envio),
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "actualizado_en": self.actualizado_en.isoformat() if self.actualizado_en else None,
        }


class DetallePedido:
    """
    Modelo de Detalle de Pedido (línea de orden).

    Almacena snapshots inmutables del nombre y precio del producto
    al momento de la compra, junto con la personalización del ítem.
    """

    def __init__(
        self,
        pedido_id: int,
        producto_id: int,
        nombre_snapshot: str,
        cantidad: int,
        precio_snapshot: float,
        personalizacion: Optional[List[int]] = None,
        id: Optional[int] = None,
        creado_en: Optional[datetime] = None,
    ):
        self.id = id
        self.pedido_id = pedido_id
        self.producto_id = producto_id
        self.nombre_snapshot = nombre_snapshot  # snapshot inmutable del nombre
        self.cantidad = max(1, int(cantidad))
        self.precio_snapshot = float(precio_snapshot)  # snapshot inmutable del precio
        self.personalizacion: List[int] = personalizacion or []  # IDs de ingredientes excluidos
        self.creado_en = creado_en or datetime.utcnow()

    def to_dict(self) -> Dict[str, Any]:
        """Serializa DetallePedido a diccionario serializable."""
        return {
            "id": self.id,
            "pedido_id": self.pedido_id,
            "producto_id": self.producto_id,
            "nombre_snapshot": self.nombre_snapshot,
            "cantidad": self.cantidad,
            "precio_snapshot": float(self.precio_snapshot),
            "personalizacion": self.personalizacion,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
        }


class HistorialEstadoPedido:
    """
    Modelo de Historial de Estado de Pedido.

    ⚠️ APPEND-ONLY: Esta entidad NUNCA se actualiza ni elimina.
    Solo se permiten operaciones INSERT. Esto garantiza un audit trail
    completo e inmutable de todos los cambios de estado del pedido.

    El primer registro de un pedido siempre tiene estado_anterior=None.
    """

    def __init__(
        self,
        pedido_id: int,
        estado_nuevo: EstadoPedidoEnum,
        estado_anterior: Optional[EstadoPedidoEnum] = None,
        usuario_id: Optional[int] = None,
        observacion: Optional[str] = None,
        id: Optional[int] = None,
        timestamp: Optional[datetime] = None,
    ):
        self.id = id
        self.pedido_id = pedido_id
        self.estado_anterior = (
            estado_anterior
            if isinstance(estado_anterior, (EstadoPedidoEnum, type(None)))
            else EstadoPedidoEnum(estado_anterior) if estado_anterior else None
        )
        self.estado_nuevo = (
            estado_nuevo
            if isinstance(estado_nuevo, EstadoPedidoEnum)
            else EstadoPedidoEnum(estado_nuevo)
        )
        self.usuario_id = usuario_id
        self.timestamp = timestamp or datetime.utcnow()
        self.observacion = observacion

    def to_dict(self) -> Dict[str, Any]:
        """Serializa HistorialEstadoPedido a diccionario serializable."""
        return {
            "id": self.id,
            "pedido_id": self.pedido_id,
            "estado_anterior": (
                self.estado_anterior.value
                if isinstance(self.estado_anterior, EstadoPedidoEnum)
                else self.estado_anterior
            ),
            "estado_nuevo": (
                self.estado_nuevo.value
                if isinstance(self.estado_nuevo, EstadoPedidoEnum)
                else self.estado_nuevo
            ),
            "usuario_id": self.usuario_id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "observacion": self.observacion,
        }
