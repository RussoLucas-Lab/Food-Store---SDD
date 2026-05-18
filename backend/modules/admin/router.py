"""
Routers para el módulo admin.

Endpoints:
- GET /admin/metricas/resumen         — KPIs generales
- GET /admin/metricas/ventas          — serie temporal de ventas
- GET /admin/metricas/productos-top   — ranking de productos
- GET /admin/metricas/pedidos-por-estado — distribución por estado
- GET /admin/usuarios                 — listado paginado de usuarios
- PATCH /admin/usuarios/{id}          — editar datos y/o rol
- PATCH /admin/usuarios/{id}/activo   — activar/desactivar cuenta

Todos los endpoints requieren rol ADMIN.
El prefijo /api/v1/admin se agrega en main.py.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import date

from backend.core.deps import get_uow
from backend.core.uow_postgresql import PostgreSQLUnitOfWork
from backend.middleware.jwt_middleware import require_role_user, CurrentUser
from .service import AdminMetricasService, AdminUsuariosService
from .schemas import (
    ResumenMetricasRead,
    PuntoVentaRead,
    ProductoTopRead,
    PedidoPorEstadoRead,
    GranularidadEnum,
    UsuariosListRead,
    UsuarioAdminRead,
    UsuarioAdminUpdate,
    UsuarioActivoUpdate,
)

router = APIRouter(
    tags=["admin"],
    responses={
        401: {"description": "No autenticado"},
        403: {"description": "Sin permiso (requiere rol ADMIN)"},
    }
)


# ============================================================================
# Endpoints de métricas
# ============================================================================

@router.get(
    "/metricas/resumen",
    response_model=ResumenMetricasRead,
    summary="Resumen general de métricas",
    description="KPIs del negocio: ventas totales, pedidos, usuarios y productos sin stock. Solo ADMIN."
)
def get_metricas_resumen(
    current_user: CurrentUser = Depends(require_role_user("ADMIN", "admin")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """GET /api/v1/admin/metricas/resumen"""
    metricas_service = AdminMetricasService(uow)
    data = metricas_service.get_resumen()
    return ResumenMetricasRead(**data)


@router.get(
    "/metricas/ventas",
    response_model=List[PuntoVentaRead],
    summary="Serie temporal de ventas",
    description="Ventas agrupadas por día, semana o mes. Filtra por rango de fechas. Solo ADMIN."
)
def get_metricas_ventas(
    desde: Optional[date] = Query(default=None, description="Fecha de inicio (YYYY-MM-DD)"),
    hasta: Optional[date] = Query(default=None, description="Fecha de fin (YYYY-MM-DD)"),
    granularidad: GranularidadEnum = Query(
        default=GranularidadEnum.DIA,
        description="Agrupación temporal: dia, semana o mes"
    ),
    current_user: CurrentUser = Depends(require_role_user("ADMIN", "admin")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """GET /api/v1/admin/metricas/ventas"""
    metricas_service = AdminMetricasService(uow)
    data = metricas_service.get_serie_temporal(
        desde=desde,
        hasta=hasta,
        granularidad=granularidad.value,
    )
    return [PuntoVentaRead(**p) for p in data]


@router.get(
    "/metricas/productos-top",
    response_model=List[ProductoTopRead],
    summary="Ranking de productos más vendidos",
    description="Top N de productos por cantidad vendida en pedidos efectivos. Solo ADMIN."
)
def get_metricas_productos_top(
    top: int = Query(default=10, ge=1, le=100, description="Cantidad de resultados"),
    desde: Optional[date] = Query(default=None, description="Fecha de inicio"),
    hasta: Optional[date] = Query(default=None, description="Fecha de fin"),
    current_user: CurrentUser = Depends(require_role_user("ADMIN", "admin")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """GET /api/v1/admin/metricas/productos-top"""
    metricas_service = AdminMetricasService(uow)
    data = metricas_service.get_top_productos(top=top, desde=desde, hasta=hasta)
    return [ProductoTopRead(**p) for p in data]


@router.get(
    "/metricas/pedidos-por-estado",
    response_model=List[PedidoPorEstadoRead],
    summary="Distribución de pedidos por estado",
    description="Cantidad de pedidos agrupados por estado, con filtro opcional de fechas. Solo ADMIN."
)
def get_metricas_pedidos_estado(
    desde: Optional[date] = Query(default=None, description="Fecha de inicio"),
    hasta: Optional[date] = Query(default=None, description="Fecha de fin"),
    current_user: CurrentUser = Depends(require_role_user("ADMIN", "admin")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """GET /api/v1/admin/metricas/pedidos-por-estado"""
    metricas_service = AdminMetricasService(uow)
    data = metricas_service.get_distribucion_estados(desde=desde, hasta=hasta)
    return [PedidoPorEstadoRead(**p) for p in data]


# ============================================================================
# Endpoints de gestión de usuarios
# ============================================================================

@router.get(
    "/usuarios",
    response_model=UsuariosListRead,
    summary="Listar usuarios paginados",
    description="Listado de usuarios con búsqueda, filtros y paginación. Nunca expone hashes. Solo ADMIN."
)
def list_usuarios(
    page: int = Query(default=1, ge=1, description="Número de página"),
    size: int = Query(default=20, ge=1, le=100, description="Tamaño de página"),
    q: Optional[str] = Query(default=None, description="Búsqueda por nombre o email"),
    rol: Optional[str] = Query(default=None, description="Filtrar por rol"),
    activo: Optional[bool] = Query(default=None, description="Filtrar por estado activo"),
    current_user: CurrentUser = Depends(require_role_user("ADMIN", "admin")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """GET /api/v1/admin/usuarios"""
    usuarios_service = AdminUsuariosService(uow)
    result = usuarios_service.list_usuarios(
        page=page, size=size, q=q, rol=rol, activo=activo
    )
    items = [UsuarioAdminRead(**u) for u in result["items"]]
    return UsuariosListRead(
        items=items,
        total=result["total"],
        page=result["page"],
        size=result["size"],
    )


@router.patch(
    "/usuarios/{user_id}",
    response_model=UsuarioAdminRead,
    summary="Editar datos y/o rol de un usuario",
    description=(
        "Modifica nombre, email y/o rol del usuario. "
        "Revoca tokens al cambiar rol. Valida RN-RB04. Solo ADMIN."
    )
)
def update_usuario(
    user_id: int,
    body: UsuarioAdminUpdate,
    current_user: CurrentUser = Depends(require_role_user("ADMIN", "admin")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """PATCH /api/v1/admin/usuarios/{id}"""
    usuarios_service = AdminUsuariosService(uow)
    result = usuarios_service.update_usuario(
        user_id=user_id,
        current_user_id=current_user.user_id,
        nombre=body.nombre,
        email=body.email,
        role=body.role,
        roles=body.roles,
    )
    return UsuarioAdminRead(**result)


@router.patch(
    "/usuarios/{user_id}/activo",
    response_model=UsuarioAdminRead,
    summary="Activar o desactivar cuenta de usuario",
    description=(
        "Modifica el estado activo/inactivo de la cuenta. "
        "Revoca tokens al desactivar. Rechaza auto-desactivación y dejar sin ADMIN. Solo ADMIN."
    )
)
def toggle_usuario_activo(
    user_id: int,
    body: UsuarioActivoUpdate,
    current_user: CurrentUser = Depends(require_role_user("ADMIN", "admin")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """PATCH /api/v1/admin/usuarios/{id}/activo"""
    usuarios_service = AdminUsuariosService(uow)
    result = usuarios_service.toggle_activo(
        user_id=user_id,
        current_user_id=current_user.user_id,
        activo=body.activo,
    )
    return UsuarioAdminRead(**result)
