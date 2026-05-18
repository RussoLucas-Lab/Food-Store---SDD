"""
Routers para operaciones CRUD de Categorías.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from backend.core.deps import get_uow
from backend.core.uow_postgresql import PostgreSQLUnitOfWork
from .service import CategoryService
from .schemas import (
    CategoriaCreateRequest,
    CategoriaUpdateRequest,
    CategoriaResponse,
    CategoriaListResponse
)
from backend.middleware.jwt_middleware import require_role

router = APIRouter(
    prefix="/categorias",
    tags=["categorias"],
    responses={404: {"description": "Not found"}}
)


@router.post(
    "",
    response_model=CategoriaResponse,
    status_code=201,
    summary="Crear nueva categoría",
    description="Solo administradores pueden crear categorías"
)
def create_categoria(
    req: CategoriaCreateRequest,
    user_id: int = Depends(require_role("admin", "ADMIN", "stock", "STOCK")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    categoria_service = CategoryService(uow)
    try:
        result = categoria_service.create_categoria(
            nombre=req.nombre,
            descripcion=req.descripcion or ""
        )
        return CategoriaResponse(**result)

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
    response_model=CategoriaListResponse,
    summary="Listar categorías",
    description="Devuelve categorías activas con paginación y ordenamiento"
)
def list_categorias(
    skip: int = Query(0, ge=0, description="Cantidad de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Límite de registros (máximo 100)"),
    sort: str = Query("id", regex="^(id|nombre|created_at)$", description="Campo de ordenamiento"),
    include_inactive: bool = Query(False, description="Incluir categorías inactivas (admin-only)"),
    user_id: Optional[int] = Depends(require_role(allow_customer=True)),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    try:
        categoria_service = CategoryService(uow)
        items_dict = categoria_service.list_categorias(
            skip=skip,
            limit=limit,
            search=None
        )

        all_items = uow.categorias.find_all(include_inactive=include_inactive)
        total = len(all_items)

        items = [CategoriaResponse(**item) for item in items_dict]

        return CategoriaListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    summary="Obtener detalles de categoría",
    description="Devuelve detalles de una categoría activa"
)
def get_categoria(
    categoria_id: int,
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    try:
        categoria_service = CategoryService(uow)
        result = categoria_service.get_categoria(categoria_id)
        return CategoriaResponse(**result)

    except ValueError as e:
        error_msg = str(e)
        if "no existe" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.put(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    summary="Actualizar categoría",
    description="Solo administradores pueden actualizar categorías"
)
def update_categoria(
    categoria_id: int,
    req: CategoriaUpdateRequest,
    user_id: int = Depends(require_role("admin", "ADMIN", "stock", "STOCK")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    try:
        categoria_service = CategoryService(uow)
        result = categoria_service.update_categoria(
            id=categoria_id,
            nombre=req.nombre or "",
            descripcion=req.descripcion or ""
        )
        return CategoriaResponse(**result)

    except ValueError as e:
        error_msg = str(e)
        if "no existe" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif "ya está en uso" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.delete(
    "/{categoria_id}",
    status_code=204,
    summary="Eliminar (soft delete) categoría",
    description="Marca categoría como inactiva. Solo administradores."
)
def delete_categoria(
    categoria_id: int,
    user_id: int = Depends(require_role("admin", "ADMIN", "stock", "STOCK")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    try:
        categoria_service = CategoryService(uow)
        categoria_service.delete_categoria(categoria_id)
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
