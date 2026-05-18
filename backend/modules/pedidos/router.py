"""
Routers para operaciones de Pedidos (carrito → orden).

Endpoints:
- POST /pedidos → crear pedido desde carrito (requiere cliente autenticado)
- GET  /pedidos → listar pedidos del cliente autenticado
- GET  /pedidos/{pedido_id} → detalle de pedido (solo propio)

El prefijo /api/v1 se agrega en main.py.
"""

import json
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import date
from backend.core.deps import get_uow
from backend.core.uow_postgresql import PostgreSQLUnitOfWork
from .service import PedidoService
from .schemas import (
    CartCreateDTO,
    PedidoResponse,
    PedidoDetailResponse,
    PedidoGestionResponse,
    EstadoUpdateDTO,
)
from .exceptions import (
    CartEmptyError,
    StockInsufficient,
    PedidoNotFound,
    UnauthorizedPedidoAccess,
    DireccionNotFound,
    TransicionInvalida,
    RolNoAutorizadoParaTransicion,
)
from backend.middleware.jwt_middleware import require_role, require_role_user, CurrentUser

router = APIRouter(
    prefix="/pedidos",
    tags=["pedidos"],
    responses={404: {"description": "Not found"}}
)


@router.post(
    "",
    response_model=PedidoResponse,
    status_code=201,
    summary="Crear pedido desde carrito",
    description="Crea un nuevo pedido a partir del carrito del cliente autenticado. "
                "Valida stock y captura snapshots de precios y dirección."
)
def create_order(
    carrito_dto: CartCreateDTO,
    user_id: int = Depends(require_role("client", "admin")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """POST /api/v1/pedidos — crear pedido desde carrito."""
    pedido_service = PedidoService(uow)
    try:
        result = pedido_service.create_order(
            cliente_id=user_id,
            carrito_dto=carrito_dto,
        )
        return PedidoResponse(**result)

    except CartEmptyError as e:
        raise HTTPException(status_code=400, detail=e.message)
    except StockInsufficient as e:
        raise HTTPException(status_code=400, detail=e.message)
    except DireccionNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "",
    response_model=List[PedidoResponse],
    summary="Listar pedidos del cliente",
    description="Retorna los pedidos del cliente autenticado con paginación."
)
def list_orders(
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(10, ge=1, le=100, description="Máximo de registros"),
    user_id: int = Depends(require_role("client", "admin")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """GET /api/v1/pedidos — listar pedidos del cliente autenticado."""
    pedido_service = PedidoService(uow)
    try:
        pedidos = pedido_service.list_orders(
            cliente_id=user_id,
            skip=skip,
            limit=limit,
        )
        return [PedidoResponse(**p) for p in pedidos]

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/gestion",
    response_model=List[PedidoGestionResponse],
    summary="Listado de gestión de pedidos",
    description="Lista todos los pedidos del sistema con filtros opcionales. "
                "Exclusivo para roles PEDIDOS y ADMIN."
)
def list_gestion(
    estado: Optional[str] = Query(default=None, description="Filtrar por estado (e.g. CONFIRMADO)"),
    fecha_desde: Optional[date] = Query(default=None, description="Fecha de inicio del rango (YYYY-MM-DD)"),
    fecha_hasta: Optional[date] = Query(default=None, description="Fecha de fin del rango (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0, description="Registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de registros"),
    current_user: CurrentUser = Depends(require_role_user("PEDIDOS", "ADMIN")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """GET /api/v1/pedidos/gestion — listado de gestión para PEDIDOS y ADMIN."""
    pedido_service = PedidoService(uow)
    try:
        pedidos = pedido_service.list_gestion(
            estado=estado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            skip=skip,
            limit=limit,
        )
        return [PedidoGestionResponse(**p) for p in pedidos]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.patch(
    "/{pedido_id}/estado",
    response_model=PedidoResponse,
    summary="Cambiar estado del pedido (FSM)",
    description=(
        "Avanza o cancela el estado de un pedido siguiendo la FSM. "
        "PENDIENTE→CONFIRMADO está bloqueada (solo automática). "
        "Motivo obligatorio al cancelar."
    )
)
def update_estado(
    pedido_id: int,
    dto: EstadoUpdateDTO,
    current_user: CurrentUser = Depends(
        require_role_user("CLIENT", "client", "PEDIDOS", "pedidos", "ADMIN", "admin")
    ),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """PATCH /api/v1/pedidos/{pedido_id}/estado — cambio de estado manual (FSM)."""
    pedido_service = PedidoService(uow)
    # Normalizar rol a mayúsculas para coincidir con los mapas FSM
    rol = current_user.role.upper()
    # Mapear rol 'CLIENT' también para variantes de token antiguo
    rol_map = {"ADMIN": "ADMIN", "PEDIDOS": "PEDIDOS", "CLIENT": "CLIENT",
               "client": "CLIENT", "admin": "ADMIN", "pedidos": "PEDIDOS"}
    rol = rol_map.get(current_user.role, current_user.role.upper())

    try:
        result = pedido_service.advance_estado(
            pedido_id=pedido_id,
            nuevo_estado_str=dto.nuevo_estado,
            usuario_id=current_user.user_id,
            rol=rol,
            motivo=dto.motivo,
        )
        return PedidoResponse(**result)

    except PedidoNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
    except TransicionInvalida as e:
        raise HTTPException(status_code=409, detail=e.message)
    except RolNoAutorizadoParaTransicion as e:
        raise HTTPException(status_code=403, detail=e.message)
    except UnauthorizedPedidoAccess as e:
        raise HTTPException(status_code=403, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/{pedido_id}",
    response_model=PedidoDetailResponse,
    summary="Detalle de pedido",
    description=(
        "Retorna el detalle completo de un pedido (detalles + historial). "
        "CLIENT solo puede ver sus propios pedidos. PEDIDOS y ADMIN pueden ver cualquiera."
    )
)
def get_order_detail(
    pedido_id: int,
    current_user: CurrentUser = Depends(
        require_role_user("CLIENT", "client", "PEDIDOS", "pedidos", "ADMIN", "admin")
    ),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """GET /api/v1/pedidos/{pedido_id} — detalle completo del pedido."""
    pedido_service = PedidoService(uow)
    rol_map = {"ADMIN": "ADMIN", "PEDIDOS": "PEDIDOS", "CLIENT": "CLIENT",
               "client": "CLIENT", "admin": "ADMIN", "pedidos": "PEDIDOS"}
    rol = rol_map.get(current_user.role, current_user.role.upper())

    try:
        result = pedido_service.get_order_detail(
            pedido_id=pedido_id,
            cliente_id=current_user.user_id,
            rol=rol,
        )
        return PedidoDetailResponse(**result)

    except PedidoNotFound as e:
        raise HTTPException(status_code=404, detail=e.message)
    except UnauthorizedPedidoAccess as e:
        raise HTTPException(status_code=403, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
