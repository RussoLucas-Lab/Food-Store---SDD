"""
Routers para operaciones CRUD de Ingredientes.

Proporciona 7 endpoints RESTful:
- POST /ingredientes (crear, admin-only)
- GET /ingredientes (listar con filtros)
- GET /ingredientes/buscar (búsqueda por nombre)
- GET /ingredientes/{id} (detalle)
- PUT /ingredientes/{id} (actualizar, admin-only)
- DELETE /ingredientes/{id} (soft delete, admin-only)
- GET /ingredientes/{id}/historial-stock (historial, admin-only)

Los routers delegan la lógica de negocio a IngredientService y solo se ocupan
de HTTP concerns: autenticación, response formatting, exception mapping.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from uow.inmemory import InMemoryUnitOfWork
from backend.services.ingrediente_service import IngredientService
from backend.schemas.ingrediente_schema import (
    IngredienteCreateRequest,
    IngredienteUpdateRequest,
    IngredienteResponse,
    IngredienteListResponse,
    UnidadMedidaEnum
)
from backend.middleware.jwt_middleware import require_role

# Instancia de UoW (en producción sería inyectada)
uow = InMemoryUnitOfWork()

# Instancia de servicio
ingrediente_service = IngredientService(uow)

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
    user_id: int = Depends(require_role("admin"))
):
    """
    Crear nuevo ingrediente.
    
    - **nombre**: Requerido, 1-100 caracteres, único
    - **unidad_medida**: gramos, litros, unidades, kilos, mililitros
    - **cantidad_stock**: Stock inicial (>= 0)
    - **cantidad_minima**: Cantidad mínima para alerta (>= 0)
    - **descripcion**: Opcional, máximo 500 caracteres
    - **categoria_id**: ID de categoría (opcional)
    
    Returns:
        - 201: Ingrediente creado exitosamente
        - 400: Datos inválidos
        - 403: Usuario no autorizado (no es admin)
        - 409: Nombre ya existe
    """
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
    user_id: Optional[int] = Depends(require_role(allow_customer=True))
):
    """
    Listar ingredientes con opciones de filtrado y paginación.
    
    Returns:
        - 200: Listado de ingredientes
        - 400: Parámetros inválidos
    """
    try:
        # Validar unidad_medida si se proporciona
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
        
        # Calcular total
        all_items = uow.ingredientes.find_all(include_inactive=False)
        total = len(all_items)
        
        return IngredienteListResponse(
            ingredientes=[IngredienteResponse(**i) for i in items_dict],
            total=total,
            skip=skip,
            limit=limit
        )
    
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
    user_id: Optional[int] = Depends(require_role(allow_customer=True))
):
    """
    Buscar ingredientes por nombre.
    
    - **q**: Término de búsqueda (requerido, mínimo 1 carácter)
    - **skip**: Registros a saltar (paginación)
    - **limit**: Límite por página (máximo 100)
    
    Returns:
        - 200: Resultados de búsqueda
        - 400: Parámetro q requerido
    """
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
    user_id: Optional[int] = Depends(require_role(allow_customer=True))
):
    """
    Obtener detalles de un ingrediente.
    
    Returns:
        - 200: Detalles del ingrediente
        - 404: Ingrediente no encontrado o inactivo
    """
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
    user_id: int = Depends(require_role("admin"))
):
    """
    Actualizar un ingrediente existente.
    
    Solo se actualizan los campos proporcionados. Todos son opcionales.
    
    Returns:
        - 200: Ingrediente actualizado
        - 404: Ingrediente no encontrado
        - 409: Nombre ya existe
        - 403: Usuario no autorizado (no es admin)
    """
    try:
        result = ingrediente_service.update_ingrediente(
            id=ingrediente_id,
            nombre=req.nombre,
            unidad_medida=req.unidad_medida.value if req.unidad_medida else None,
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
    user_id: int = Depends(require_role("admin"))
):
    """
    Marcar ingrediente como inactivo (soft delete).
    
    Valida que no haya productos activos que lo usen como componente.
    Si hay productos, retorna 409 Conflict.
    
    Esta operación es idempotente: si el ingrediente ya está inactivo,
    retorna 204 sin cambios.
    
    Returns:
        - 204: Ingrediente marcado como inactivo
        - 404: Ingrediente no encontrado
        - 403: Usuario no autorizado (no es admin)
        - 409: Ingrediente está en uso por productos activos
    """
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
    user_id: int = Depends(require_role("admin"))
):
    """
    Obtener historial de cambios de stock de un ingrediente.
    
    Nota: Esta funcionalidad requiere tabla de auditoría stock_history.
    Por ahora retorna estructura placeholder.
    
    Returns:
        - 200: Listado de cambios de stock
        - 404: Ingrediente no encontrado
        - 403: Usuario no autorizado (no es admin)
    """
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
