"""
Router para DireccionEntrega.

Endpoints bajo /clientes/me/direcciones (el prefijo /api/v1 lo agrega main.py):
- POST   /clientes/me/direcciones           → 201 crear dirección
- GET    /clientes/me/direcciones           → 200 listar direcciones propias
- PUT    /clientes/me/direcciones/{id}      → 200 actualizar dirección
- DELETE /clientes/me/direcciones/{id}      → 204 soft delete
- PUT    /clientes/me/direcciones/{id}/predeterminada → 200 marcar predeterminada
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from backend.core.deps import get_uow
from backend.core.uow_postgresql import PostgreSQLUnitOfWork
from .service import DireccionService
from .schemas import DireccionCreate, DireccionUpdate, DireccionResponse
from .exceptions import DireccionNotFound, UnauthorizedDireccionAccess
from backend.middleware.jwt_middleware import require_role

router = APIRouter(
    prefix="/clientes/me/direcciones",
    tags=["direcciones"],
    responses={404: {"description": "Not found"}},
)


def _map_exception(exc: Exception) -> HTTPException:
    """Mapear excepciones de dominio a HTTPException."""
    if isinstance(exc, DireccionNotFound):
        return HTTPException(status_code=404, detail=str(exc))
    if isinstance(exc, UnauthorizedDireccionAccess):
        return HTTPException(status_code=403, detail=str(exc))
    if isinstance(exc, ValueError):
        return HTTPException(status_code=400, detail=str(exc))
    return HTTPException(status_code=500, detail=f"Error interno: {str(exc)}")


# ── Endpoints ──────────────────────────────────────────────────────────────────


@router.post(
    "",
    response_model=DireccionResponse,
    status_code=201,
    summary="Crear dirección de entrega",
    description="Crea una nueva dirección para el cliente autenticado.",
)
def create_direccion(
    dto: DireccionCreate,
    user_id: int = Depends(require_role("client", "admin")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """
    Crear dirección de entrega.

    - Primera dirección del cliente → automáticamente es_predeterminada=True (RN-DI01)
    - cliente_id viene del JWT, no del body

    Returns:
        201: Dirección creada
        400: Datos inválidos
        401: No autenticado
        403: Rol insuficiente
    """
    direccion_service = DireccionService(uow)
    try:
        result = direccion_service.create_direccion(user_id=user_id, dto=dto)
        return DireccionResponse(**result)
    except Exception as exc:
        raise _map_exception(exc)


@router.get(
    "",
    response_model=List[DireccionResponse],
    summary="Listar direcciones propias",
    description="Devuelve todas las direcciones activas del cliente autenticado.",
)
def list_direcciones(
    user_id: int = Depends(require_role("client", "admin")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """
    Listar direcciones de entrega del cliente autenticado.

    Returns:
        200: Lista de direcciones
        401: No autenticado
    """
    direccion_service = DireccionService(uow)
    try:
        results = direccion_service.list_direcciones(user_id=user_id)
        return [DireccionResponse(**r) for r in results]
    except Exception as exc:
        raise _map_exception(exc)


@router.put(
    "/{direccion_id}",
    response_model=DireccionResponse,
    summary="Actualizar dirección",
    description="Actualiza los campos de una dirección propia.",
)
def update_direccion(
    direccion_id: int,
    dto: DireccionUpdate,
    user_id: int = Depends(require_role("client", "admin")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """
    Actualizar dirección de entrega.

    Returns:
        200: Dirección actualizada
        400: No se proveyeron campos / datos inválidos
        401: No autenticado
        403: No es propietario de la dirección
        404: Dirección no existe
    """
    direccion_service = DireccionService(uow)
    try:
        result = direccion_service.update_direccion(
            user_id=user_id, direccion_id=direccion_id, dto=dto
        )
        return DireccionResponse(**result)
    except Exception as exc:
        raise _map_exception(exc)


@router.delete(
    "/{direccion_id}",
    status_code=204,
    summary="Eliminar dirección",
    description="Soft-delete de una dirección propia.",
)
def delete_direccion(
    direccion_id: int,
    user_id: int = Depends(require_role("client", "admin")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """
    Eliminar (soft-delete) dirección de entrega.

    Si era la predeterminada y quedan otras activas, se reasigna la predeterminada
    a la más antigua.

    Returns:
        204: Eliminada correctamente
        401: No autenticado
        403: No es propietario de la dirección
        404: Dirección no existe
    """
    direccion_service = DireccionService(uow)
    try:
        direccion_service.delete_direccion(user_id=user_id, direccion_id=direccion_id)
        return None  # 204 No Content
    except Exception as exc:
        raise _map_exception(exc)


@router.put(
    "/{direccion_id}/predeterminada",
    response_model=DireccionResponse,
    summary="Marcar como predeterminada",
    description="Marca una dirección como la predeterminada del cliente.",
)
def set_predeterminada(
    direccion_id: int,
    user_id: int = Depends(require_role("client", "admin")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """
    Marcar dirección como predeterminada.

    Desmarca automáticamente cualquier otra dirección predeterminada del cliente (RN-DI02).

    Returns:
        200: Dirección marcada como predeterminada
        401: No autenticado
        403: No es propietario de la dirección
        404: Dirección no existe
    """
    direccion_service = DireccionService(uow)
    try:
        result = direccion_service.set_predeterminada(
            user_id=user_id, direccion_id=direccion_id
        )
        return DireccionResponse(**result)
    except Exception as exc:
        raise _map_exception(exc)
