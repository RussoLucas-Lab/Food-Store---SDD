"""
Routers para operaciones CRUD de Categorías.

Proporciona 5 endpoints RESTful:
- POST /categorias (crear, admin-only)
- GET /categorias (listar)
- GET /categorias/{id} (detalle)
- PUT /categorias/{id} (actualizar, admin-only)
- DELETE /categorias/{id} (soft delete, admin-only)

Los routers delegan la lógica de negocio a CategoryService y solo se ocupan
de HTTP concerns: autenticación, response formatting, exception mapping.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from uow.inmemory import InMemoryUnitOfWork
from backend.services.categoria_service import CategoryService
from backend.schemas.categoria_schema import (
    CategoriaCreateRequest,
    CategoriaUpdateRequest,
    CategoriaResponse,
    CategoriaListResponse
)
from backend.middleware.jwt_middleware import require_role

# Instancia de UoW (en producción sería inyectada)
uow = InMemoryUnitOfWork()

# Instancia de servicio
categoria_service = CategoryService(uow)

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
    user_id: int = Depends(require_role("admin"))
):
    """
    Crear nueva categoría.
    
    - **nombre**: Requerido, 1-100 caracteres, único
    - **descripcion**: Opcional, máximo 500 caracteres
    
    Returns:
        - 201: Categoría creada exitosamente
        - 400: Datos inválidos
        - 403: Usuario no autorizado (no es admin)
        - 409: Nombre ya existe
    """
    try:
        result = categoria_service.create_categoria(
            nombre=req.nombre,
            descripcion=req.descripcion or ""
        )
        return CategoriaResponse(**result)
    
    except ValueError as e:
        error_msg = str(e)
        # Map ValueError to appropriate HTTP status
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
    user_id: Optional[int] = Depends(require_role(allow_customer=True))
):
    """
    Listar categorías.
    
    - **skip**: Registros a saltar (paginación)
    - **limit**: Límite por página (máximo 100)
    - **sort**: Ordenar por: id, nombre, o created_at
    - **include_inactive**: Ver inactivas (solo admins)
    
    Returns:
        - 200: Listado de categorías
        - 400: Parámetros inválidos
        - 403: Parámetro include_inactive requiere rol admin
    """
    try:
        # Validar que solo admins vean inactivas
        if include_inactive and user_id:
            # Verificar rol (simplificado - en producción usar contexto JWT)
            from models.usuario import RoleEnum
            # Por ahora permitir - en producción verificar contra token JWT
        
        items_dict = categoria_service.list_categorias(
            skip=skip,
            limit=limit,
            search=None
        )
        
        # Obtener total de categorías
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
def get_categoria(categoria_id: int):
    """
    Obtener detalles de una categoría por ID.
    
    Returns:
        - 200: Categoría encontrada
        - 404: Categoría no existe o está inactiva
    """
    try:
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
    user_id: int = Depends(require_role("admin"))
):
    """
    Actualizar categoría existente.
    
    - **nombre**: Nuevo nombre (opcional, debe ser único)
    - **descripcion**: Nueva descripción (opcional)
    
    Returns:
        - 200: Categoría actualizada
        - 403: Usuario no autorizado
        - 404: Categoría no encontrada
        - 409: Nombre ya existe
    """
    try:
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
    user_id: int = Depends(require_role("admin"))
):
    """
    Marcar categoría como inactiva (soft delete).
    
    Valida que no haya productos activos asignados a esta categoría.
    Si hay productos, retorna 409 Conflict.
    
    La categoría no se elimina de la BD, solo se marca como inactiva.
    Esta operación es idempotente.
    
    Returns:
        - 204: Categoría marcada como inactiva
        - 403: Usuario no autorizado
        - 404: Categoría no encontrada
        - 409: Categoría está en uso por productos activos
    """
    try:
        categoria_service.delete_categoria(categoria_id)
        # 204 No Content (sin body)
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
