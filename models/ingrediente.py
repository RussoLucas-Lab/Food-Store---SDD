from datetime import datetime
from typing import Optional
from enum import Enum


class UnidadMedida(str, Enum):
    """Unidades de medida disponibles para ingredientes"""
    GRAMOS = "gramos"
    LITROS = "litros"
    UNIDADES = "unidades"
    KILOS = "kilos"
    MILILITROS = "mililitros"


class Ingrediente:
    """
    Modelo de Ingrediente para el catálogo de productos.
    
    Atributos:
        id: Identificador único (PK)
        nombre: Nombre del ingrediente (unique)
        descripcion: Descripción opcional
        unidad_medida: Unidad de medida (gramos, litros, unidades, kilos, mililitros)
        cantidad_stock: Cantidad disponible en stock
        cantidad_minima: Cantidad mínima antes de generar alerta
        cantidad_reservada: Cantidad reservada en carritos/pedidos pendientes
        categoria_id: ID de categoría relacionada (FK opcional)
        is_active: Estado del ingrediente (activo/inactivo)
        created_at: Timestamp de creación
        updated_at: Timestamp de última actualización
        deleted_at: Timestamp de soft delete (None si activo)
    """
    
    def __init__(
        self,
        id: int,
        nombre: str,
        unidad_medida: str,
        cantidad_stock: int,
        cantidad_minima: int,
        descripcion: str = "",
        cantidad_reservada: int = 0,
        categoria_id: Optional[int] = None,
        is_active: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        deleted_at: Optional[datetime] = None
    ):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.unidad_medida = unidad_medida
        self.cantidad_stock = cantidad_stock
        self.cantidad_minima = cantidad_minima
        self.cantidad_reservada = cantidad_reservada
        self.categoria_id = categoria_id
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.deleted_at = deleted_at
    
    @property
    def stock_disponible(self) -> int:
        """Calcula stock disponible (stock - reservadas)"""
        return max(0, self.cantidad_stock - self.cantidad_reservada)
    
    @property
    def alerta_stock_bajo(self) -> bool:
        """Determina si el stock está por debajo del mínimo"""
        return self.cantidad_stock < self.cantidad_minima
    
    def puede_descontar(self, cantidad: int) -> bool:
        """Verifica si se puede descontar la cantidad solicitada"""
        if cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa")
        if not self.is_active:
            raise ValueError("Ingrediente no activo")
        return cantidad <= self.stock_disponible
    
    def __repr__(self) -> str:
        return f"<Ingrediente id={self.id} nombre='{self.nombre}' unidad={self.unidad_medida} stock={self.cantidad_stock} is_active={self.is_active}>"
    
    def to_dict(self) -> dict:
        """Serializa Ingrediente a diccionario."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "unidad_medida": self.unidad_medida,
            "cantidad_stock": self.cantidad_stock,
            "cantidad_minima": self.cantidad_minima,
            "cantidad_reservada": self.cantidad_reservada,
            "stock_disponible": self.stock_disponible,
            "alerta_stock_bajo": self.alerta_stock_bajo,
            "categoria_id": self.categoria_id,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
            "deleted_at": self.deleted_at.isoformat() if isinstance(self.deleted_at, datetime) else self.deleted_at,
        }
