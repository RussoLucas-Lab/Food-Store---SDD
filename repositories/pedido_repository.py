"""
Repositorios para Pedidos.

Implementa:
- PedidoRepository: CRUD para pedidos
- DetallePedidoRepository: CRUD para detalles de pedido
- HistorialEstadoPedidoRepository: append-only para historial
"""

from typing import List, Optional, Dict, Any
from models.pedido import Pedido, DetallePedido, HistorialEstadoPedido, EstadoPedidoEnum
from datetime import datetime


class PedidoRepository:
    """
    Repositorio para operaciones CRUD de Pedidos.
    """
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self._data: Dict[int, Pedido] = {}  # In-memory store para testing
        self._id_counter = 1
    
    def create(self, pedido: Pedido) -> Pedido:
        """Crear un nuevo pedido"""
        if not pedido.id:
            pedido.id = self._id_counter
            self._id_counter += 1
        
        self._data[pedido.id] = pedido
        return pedido
    
    def get_by_id(self, pedido_id: int) -> Optional[Pedido]:
        """Obtener pedido por ID"""
        return self._data.get(pedido_id)
    
    def list_by_cliente(self, cliente_id: int, skip: int = 0, limit: int = 10) -> List[Pedido]:
        """Listar pedidos de un cliente con paginación"""
        pedidos = [p for p in self._data.values() if p.cliente_id == cliente_id]
        return sorted(pedidos, key=lambda p: p.creado_en, reverse=True)[skip:skip + limit]
    
    def list_all(self, skip: int = 0, limit: int = 10) -> List[Pedido]:
        """Listar todos los pedidos"""
        return sorted(self._data.values(), key=lambda p: p.creado_en, reverse=True)[skip:skip + limit]
    
    def update_status(self, pedido_id: int, new_status: EstadoPedidoEnum) -> Optional[Pedido]:
        """Actualizar estado de un pedido"""
        pedido = self._data.get(pedido_id)
        if pedido:
            pedido.estado = new_status
            pedido.actualizado_en = datetime.utcnow()
        return pedido
    
    def count_by_cliente(self, cliente_id: int) -> int:
        """Contar pedidos de un cliente"""
        return len([p for p in self._data.values() if p.cliente_id == cliente_id])
    
    def delete(self, pedido_id: int) -> bool:
        """Soft-delete de pedido (no implementado en production)"""
        if pedido_id in self._data:
            del self._data[pedido_id]
            return True
        return False


class DetallePedidoRepository:
    """
    Repositorio para operaciones CRUD de Detalles de Pedido.
    """
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self._data: Dict[int, DetallePedido] = {}  # In-memory store
        self._id_counter = 1
    
    def create(self, detalle: DetallePedido) -> DetallePedido:
        """Crear nuevo detalle de pedido"""
        if not detalle.id:
            detalle.id = self._id_counter
            self._id_counter += 1
        
        self._data[detalle.id] = detalle
        return detalle
    
    def get_by_id(self, detalle_id: int) -> Optional[DetallePedido]:
        """Obtener detalle por ID"""
        return self._data.get(detalle_id)
    
    def list_by_pedido(self, pedido_id: int) -> List[DetallePedido]:
        """Listar detalles de un pedido"""
        return [d for d in self._data.values() if d.pedido_id == pedido_id]
    
    def list_all(self, skip: int = 0, limit: int = 100) -> List[DetallePedido]:
        """Listar todos los detalles"""
        return sorted(self._data.values(), key=lambda d: d.id)[skip:skip + limit]
    
    def delete(self, detalle_id: int) -> bool:
        """Eliminar detalle (raro, pero posible)"""
        if detalle_id in self._data:
            del self._data[detalle_id]
            return True
        return False


class HistorialEstadoPedidoRepository:
    """
    Repositorio para operaciones append-only de Historial de Estado.
    
    ⚠️ Importante: Solo CREATE, NO UPDATE/DELETE
    """
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self._data: Dict[int, HistorialEstadoPedido] = {}  # In-memory store
        self._id_counter = 1
    
    def create(self, historial: HistorialEstadoPedido) -> HistorialEstadoPedido:
        """Crear registro de historial (append-only)"""
        if not historial.id:
            historial.id = self._id_counter
            self._id_counter += 1
        
        self._data[historial.id] = historial
        return historial
    
    def get_by_id(self, historial_id: int) -> Optional[HistorialEstadoPedido]:
        """Obtener registro de historial por ID (lectura)"""
        return self._data.get(historial_id)
    
    def list_by_pedido(self, pedido_id: int) -> List[HistorialEstadoPedido]:
        """Listar historial de un pedido en orden cronológico"""
        historial = [h for h in self._data.values() if h.pedido_id == pedido_id]
        return sorted(historial, key=lambda h: h.timestamp)
    
    def list_all(self, skip: int = 0, limit: int = 100) -> List[HistorialEstadoPedido]:
        """Listar todo el historial"""
        return sorted(self._data.values(), key=lambda h: h.timestamp)[skip:skip + limit]
    
    def count_by_pedido(self, pedido_id: int) -> int:
        """Contar registros de historial de un pedido"""
        return len([h for h in self._data.values() if h.pedido_id == pedido_id])
