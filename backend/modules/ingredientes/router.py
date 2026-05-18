"""
Routers para operaciones CRUD de Ingredientes.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from backend.core.deps import get_uow
from backend.core.uow_postgresql import PostgreSQLUnitOfWork
from .service import IngredientService
from .schemas import (
    IngredienteCreateRequest,
    IngredienteUpdateRequest,
    IngredienteResponse,
    IngredienteListResponse,
    UnidadMedidaEnum
)
from backend.middleware.jwt_middleware import require_role

router = APIRouter(
    prefix="/ingredientes",
    tags=["ingredientes"],
    responses={404: {"description": "Not found"}}
)


@router.post(
    "",
    response_model=IngredienteResponse,
    status_code=201,
    summary="Crear nuevo ingrediente",
    description="Solo administradores pueden crear ingredientes"
)
def create_ingrediente(
    req: IngredienteCreateRequest,
    user_id: int = Depends(require_role("admin", "ADMIN", "stock", "STOCK")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    ingrediente_service = IngredientService(uow)
    try:
        result = ingrediente_service.create_ingrediente(
            nombre=req.nombre,
            unidad_medida=req.unidad_medida.value,
            cantidad_stock=req.cantidad_stock,
            cantidad_minima=req.cantidad_minima,
            descripcion=req.descripcion or "",
            categoria_id=req.categoria_id
        )
        return IngredienteResponse(**result)

    except ValueError as e:
        error_msg = str(e)
        if "ya existe" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "",
    response_model=IngredienteListResponse,
    summary="Listar ingredientes",
    description="Devuelve ingredientes activos con paginación, filtros y ordenamiento"
)
def list_ingredientes(
    skip: int = Query(0, ge=0, description="Cantidad de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Límite de registros (máximo 100)"),
    categoria_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    disponibles_solo: bool = Query(False, description="Solo ingredientes con stock > 0"),
    alerta_stock_bajo: bool = Query(False, description="Solo ingredientes con stock bajo"),
    unidad_medida: Optional[str] = Query(None, description="Filtrar por unidad de medida"),
    ordenar_por: str = Query("id", regex="^(id|nombre|cantidad_stock|created_at)$"),
    orden: str = Query("asc", regex="^(asc|desc)$"),
    user_id: Optional[int] = Depends(require_role(allow_customer=True)),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    ingrediente_service = IngredientService(uow)
    try:
        if unidad_medida:
            try:
                UnidadMedidaEnum(unidad_medida)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"unidad_medida inválida. Válidas: {', '.join([u.value for u in UnidadMedidaEnum])}"
                )

        items_dict = ingrediente_service.list_ingredientes(
            skip=skip,
            limit=limit,
            search=None,
            unidad_medida=unidad_medida,
            categoria_id=categoria_id
        )

        all_items = uow.ingredientes.find_all(include_inactive=False)
        total = len(all_items)

        return IngredienteListResponse(
            ingredientes=[IngredienteResponse(**i) for i in items_dict],
            total=total,
            skip=skip,
            limit=limit
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/buscar",
    response_model=IngredienteListResponse,
    summary="Buscar ingredientes por nombre",
    description="Búsqueda parcial case-insensitive"
)
def buscar_ingredientes(
    q: str = Query(..., min_length=1, description="Término de búsqueda"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = Depends(require_role(allow_customer=True)),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    ingrediente_service = IngredientService(uow)
    try:
        items_dict = ingrediente_service.list_ingredientes(
            skip=skip,
            limit=limit,
            search=q
        )

        return IngredienteListResponse(
            ingredientes=[IngredienteResponse(**i) for i in items_dict],
            total=len(items_dict),
            skip=skip,
            limit=limit
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/{ingrediente_id}",
    response_model=IngredienteResponse,
    summary="Obtener detalles de ingrediente",
    description="Devuelve un ingrediente activo por su ID"
)
def get_ingrediente(
    ingrediente_id: int,
    user_id: Optional[int] = Depends(require_role(allow_customer=True)),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    ingrediente_service = IngredientService(uow)
    try:
        result = ingrediente_service.get_ingrediente(ingrediente_id)
        return IngredienteResponse(**result)

    except ValueError as e:
        error_msg = str(e)
        if "no existe" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.put(
    "/{ingrediente_id}",
    response_model=IngredienteResponse,
    summary="Actualizar ingrediente",
    description="Solo administradores pueden actualizar ingredientes"
)
def update_ingrediente(
    ingrediente_id: int,
    req: IngredienteUpdateRequest,
    user_id: int = Depends(require_role("admin", "ADMIN", "stock", "STOCK")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    ingrediente_service = IngredientService(uow)
    try:
        result = ingrediente_service.update_ingrediente(
            id=ingrediente_id,
            nombre=req.nombre,
            unidad_medida=getattr(req, 'unidad_medida', None),
            cantidad_stock=req.cantidad_stock,
            cantidad_minima=req.cantidad_minima,
            descripcion=req.descripcion
        )
        return IngredienteResponse(**result)

    except ValueError as e:
        error_msg = str(e)
        if "no existe" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif "ya está en uso" in error_msg or "ya existe" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.delete(
    "/{ingrediente_id}",
    status_code=204,
    summary="Eliminar ingrediente (soft delete)",
    description="Marca el ingrediente como inactivo (soft delete, idempotente)"
)
def delete_ingrediente(
    ingrediente_id: int,
    user_id: int = Depends(require_role("admin", "ADMIN", "stock", "STOCK")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    ingrediente_service = IngredientService(uow)
    try:
        ingrediente_service.delete_ingrediente(ingrediente_id)
        return None

    except ValueError as e:
        error_msg = str(e)
        if "no existe" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif "en uso" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/{ingrediente_id}/historial-stock",
    summary="Obtener historial de stock",
    description="Devuelve cambios recientes de stock del ingrediente (admin-only)"
)
def get_historial_stock(
    ingrediente_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: int = Depends(require_role("admin", "ADMIN", "stock", "STOCK")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    ingrediente_service = IngredientService(uow)
    try:
        history = ingrediente_service.get_stock_history(ingrediente_id)

        return {
            "ingrediente_id": ingrediente_id,
            "historial": history,
            "total": len(history)
        }

    except ValueError as e:
        error_msg = str(e)
        if "no existe" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
