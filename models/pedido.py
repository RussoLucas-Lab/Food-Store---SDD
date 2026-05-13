"""
Modelos SQLModel para Pedidos (órdenes).

Estructura:
- Pedido: orden principal con estado, dirección snapshot, total
- DetallePedido: líneas de pedido con precio snapshot y personalización
- HistorialEstadoPedido: append-only audit trail de cambios de estado
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class EstadoPedidoEnum(str, Enum):
    """Estados válidos para un pedido"""
    PENDIENTE = "PENDIENTE"
    CONFIRMADO = "CONFIRMADO"
    EN_PREPARACION = "EN_PREPARACION"
    LISTO = "LISTO"
    EN_VIAJE = "EN_VIAJE"
    ENTREGADO = "ENTREGADO"
    CANCELADO = "CANCELADO"


class Pedido:
    """
    Modelo de Pedido (Orden).
    
    Propiedades:
    - id: identificador único
    - cliente_id: referencia al usuario que hizo el pedido
    - estado: estado actual del pedido (PENDIENTE, CONFIRMADO, etc.)
    - direccion_snapshot: JSON con dirección de entrega (inmutable)
    - total: monto total del pedido (>0)
    - creado_en: timestamp de creación
    - actualizado_en: timestamp de última actualización
    """
    
    def __init__(
        self,
        id: Optional[int] = None,
        cliente_id: int = None,
        estado: EstadoPedidoEnum = EstadoPedidoEnum.PENDIENTE,
        direccion_snapshot: str = None,
        total: float = 0.0,
        creado_en: Optional[datetime] = None,
        actualizado_en: Optional[datetime] = None
    ):
        self.id = id
        self.cliente_id = cliente_id
        self.estado = estado if isinstance(estado, EstadoPedidoEnum) else EstadoPedidoEnum(estado)
        self.direccion_snapshot = direccion_snapshot  # JSON string
        self.total = float(total)
        self.creado_en = creado_en or datetime.utcnow()
        self.actualizado_en = actualizado_en or datetime.utcnow()
        
        # Relaciones (populated by repository)
        self.detalles: List['DetallePedido'] = []
        self.historial: List['HistorialEstadoPedido'] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'estado': self.estado.value if isinstance(self.estado, EstadoPedidoEnum) else self.estado,
            'direccion_snapshot': self.direccion_snapshot,
            'total': float(self.total),
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
            'actualizado_en': self.actualizado_en.isoformat() if self.actualizado_en else None,
        }


class DetallePedido:
    """
    Modelo de Detalle de Pedido (línea de orden).
    
    Propiedades:
    - id: identificador único
    - pedido_id: referencia al pedido
    - producto_id: referencia al producto
    - cantidad: cantidad ordenada (>0)
    - precio_snapshot: precio en el momento de la compra (>=0)
    - personalizacion: array de ingrediente_ids excluidos
    - creado_en: timestamp de creación
    """
    
    def __init__(
        self,
        id: Optional[int] = None,
        pedido_id: int = None,
        producto_id: int = None,
        cantidad: int = 1,
        precio_snapshot: float = 0.0,
        personalizacion: Optional[List[int]] = None,
        creado_en: Optional[datetime] = None
    ):
        self.id = id
        self.pedido_id = pedido_id
        self.producto_id = producto_id
        self.cantidad = max(1, int(cantidad))
        self.precio_snapshot = float(precio_snapshot)
        self.personalizacion = personalizacion or []
        self.creado_en = creado_en or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'producto_id': self.producto_id,
            'cantidad': self.cantidad,
            'precio_snapshot': float(self.precio_snapshot),
            'personalizacion': self.personalizacion,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
        }


class HistorialEstadoPedido:
    """
    Modelo de Historial de Estado de Pedido (append-only audit trail).
    
    Propiedades:
    - id: identificador único
    - pedido_id: referencia al pedido
    - estado_anterior: estado previo (puede ser NULL si es primer estado)
    - estado_nuevo: nuevo estado
    - usuario_id: usuario que realizó el cambio (puede ser NULL si es SISTEMA)
    - timestamp: momento del cambio
    - observacion: nota adicional (opcional)
    
    ⚠️ IMPORTANTE: Nunca se actualiza o borra, solo se inserta (append-only)
    """
    
    def __init__(
        self,
        id: Optional[int] = None,
        pedido_id: int = None,
        estado_anterior: Optional[EstadoPedidoEnum] = None,
        estado_nuevo: EstadoPedidoEnum = EstadoPedidoEnum.PENDIENTE,
        usuario_id: Optional[int] = None,
        timestamp: Optional[datetime] = None,
        observacion: Optional[str] = None
    ):
        self.id = id
        self.pedido_id = pedido_id
        self.estado_anterior = estado_anterior if isinstance(estado_anterior, (EstadoPedidoEnum, type(None))) else EstadoPedidoEnum(estado_anterior) if estado_anterior else None
        self.estado_nuevo = estado_nuevo if isinstance(estado_nuevo, EstadoPedidoEnum) else EstadoPedidoEnum(estado_nuevo)
        self.usuario_id = usuario_id
        self.timestamp = timestamp or datetime.utcnow()
        self.observacion = observacion
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el modelo a diccionario"""
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'estado_anterior': self.estado_anterior.value if isinstance(self.estado_anterior, EstadoPedidoEnum) else self.estado_anterior,
            'estado_nuevo': self.estado_nuevo.value if isinstance(self.estado_nuevo, EstadoPedidoEnum) else self.estado_nuevo,
            'usuario_id': self.usuario_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'observacion': self.observacion,
        }
