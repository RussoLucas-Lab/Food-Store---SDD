"""
Pydantic schemas para el módulo admin.

Incluye schemas para:
- Métricas: resumen, serie temporal, top productos, distribución por estado
- Gestión de usuarios: listado, edición, activación/desactivación
"""

from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from typing import List, Optional
from datetime import date
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class GranularidadEnum(str, Enum):
    """Granularidad temporal para la serie de ventas."""
    DIA = "dia"
    SEMANA = "semana"
    MES = "mes"


# ============================================================================
# Query schemas para métricas
# ============================================================================

class MetricasVentasQuery(BaseModel):
    """Query params para GET /admin/metricas/ventas"""
    desde: Optional[date] = None
    hasta: Optional[date] = None
    granularidad: GranularidadEnum = GranularidadEnum.DIA

    @model_validator(mode="after")
    def validar_rango(self) -> "MetricasVentasQuery":
        if self.desde and self.hasta and self.desde > self.hasta:
            raise ValueError("El parámetro 'desde' no puede ser posterior a 'hasta'.")
        return self


class MetricasProductosTopQuery(BaseModel):
    """Query params para GET /admin/metricas/productos-top"""
    top: int = 10
    desde: Optional[date] = None
    hasta: Optional[date] = None


class MetricasPedidosEstadoQuery(BaseModel):
    """Query params para GET /admin/metricas/pedidos-por-estado"""
    desde: Optional[date] = None
    hasta: Optional[date] = None


# ============================================================================
# Response schemas para métricas
# ============================================================================

class ResumenMetricasRead(BaseModel):
    """KPIs generales del negocio."""
    ventas_totales: float
    cantidad_pedidos: int
    cantidad_usuarios: int
    productos_sin_stock: int

    model_config = ConfigDict(from_attributes=True)


class PuntoVentaRead(BaseModel):
    """Punto en la serie temporal de ventas."""
    periodo: str       # fecha como string ISO (e.g. "2026-01-01")
    monto: float

    model_config = ConfigDict(from_attributes=True)


class ProductoTopRead(BaseModel):
    """Producto en el ranking de más vendidos."""
    producto_id: int
    nombre: str
    cantidad_vendida: int

    model_config = ConfigDict(from_attributes=True)


class PedidoPorEstadoRead(BaseModel):
    """Distribución de pedidos por estado."""
    estado: str
    cantidad: int

    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# Schemas para gestión de usuarios
# ============================================================================

class UsuarioAdminRead(BaseModel):
    """Datos completos del usuario para el panel admin (sin hash de contraseña)."""
    id: int
    email: str
    nombre: Optional[str] = None
    role: str          # rol único del modelo auth (admin/customer)
    is_active: bool
    roles: List[str] = []   # lista de roles simbólicos

    model_config = ConfigDict(from_attributes=True)


class UsuarioAdminUpdate(BaseModel):
    """Payload para editar datos y/o rol de un usuario."""
    nombre: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None          # nuevo rol (admin/customer)
    roles: Optional[List[str]] = None   # lista simbólica de roles


class UsuarioActivoUpdate(BaseModel):
    """Payload para activar/desactivar cuenta."""
    activo: bool


class UsuariosListQuery(BaseModel):
    """Query params para GET /admin/usuarios"""
    page: int = 1
    size: int = 20
    q: Optional[str] = None        # búsqueda por nombre/email
    rol: Optional[str] = None      # filtro por rol
    activo: Optional[bool] = None  # filtro por estado activo


class UsuariosListRead(BaseModel):
    """Respuesta paginada de usuarios."""
    items: List[UsuarioAdminRead]
    total: int
    page: int
    size: int

    model_config = ConfigDict(from_attributes=True)
