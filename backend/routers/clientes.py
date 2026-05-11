"""
Routers para operaciones CRUD de Clientes.

Proporciona 7 endpoints RESTful:
- POST /clientes (crear, admin-only)
- GET /clientes (listar - admin: todos, user: solo propio)
- GET /clientes/{id} (detalle - admin: cualquiera, user: propio)
- PATCH /clientes/{id} (actualizar - admin: cualquiera, user: propio)
- DELETE /clientes/{id} (soft delete, admin-only)
- GET /clientes/search (buscar por nombre/email, admin-only)
- PATCH /clientes/{id}/reactivar (reactivar, admin-only)

Los routers delegan la lógica de negocio a ClienteService y solo se ocupan
de HTTP concerns: autenticación, response formatting, exception mapping.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from uow.inmemory import InMemoryUnitOfWork
from backend.services.cliente_service import ClienteService
from backend.schemas.cliente_schema import (
    ClienteCreateRequest,
    ClienteUpdateRequest,
    ClienteResponse,
    ClienteListResponse,
    ClienteSearchResponse
)
from backend.middleware.jwt_middleware import require_role

# Instancia de UoW (en producción sería inyectada)
uow = InMemoryUnitOfWork()

# Instancia de servicio
cliente_service = ClienteService(uow)

router = APIRouter(
    prefix="/clientes",
    tags=["clientes"],
    responses={404: {"description": "Not found"}}
)


@router.post(
    "",
    response_model=ClienteResponse,
    status_code=201,
    summary="Crear nuevo cliente",
    description="Solo administradores pueden crear clientes"
)
def create_cliente(
    req: ClienteCreateRequest,
    user_id: int = Depends(require_role("admin"))
):
    """
    Crear nuevo cliente.
    
    - **nombre**: Requerido, 1-255 caracteres
    - **email**: Requerido, formato válido, único en el sistema
    - **direccion**: Requerido, 1-500 caracteres
    - **telefono**: Opcional, formato: números, guiones, espacios, paréntesis
    
    Returns:
        - 201: Cliente creado exitosamente
        - 400: Datos inválidos
        - 403: Usuario no autorizado (no es admin)
        - 409: Email ya está registrado
    """
    try:
        result = cliente_service.create_cliente(
            nombre=req.nombre,
            email=req.email,
            direccion=req.direccion,
            telefono=req.telefono,
            requesting_user_role="ADMIN"
        )
        return ClienteResponse(**result)
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        error_msg = str(e)
        if "ya está registrado" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "",
    response_model=ClienteListResponse,
    summary="Listar clientes",
    description="Admin: todos los clientes activos. User: solo su propio cliente"
)
def list_clientes(
    skip: int = Query(0, ge=0, description="Cantidad de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Límite de registros (máximo 100)"),
    user_id: Optional[int] = Depends(require_role(allow_customer=True)),
    user_role: str = Query("USER", description="Rol del usuario (ADMIN/USER)")
):
    """
    Listar clientes.
    
    - **skip**: Registros a saltar (paginación)
    - **limit**: Límite por página (máximo 100)
    
    Comportamiento:
    - ADMIN: ve todos los clientes activos
    - USER: ve solo su propio cliente
    
    Returns:
        - 200: Listado de clientes
        - 400: Parámetros inválidos
    """
    try:
        items_dict = cliente_service.list_clientes(
            skip=skip,
            limit=limit,
            requesting_user_id=user_id,
            requesting_user_role=user_role
        )
        
        # Obtener total
        all_items = uow.clientes.find_all(include_inactive=False)
        total = len(all_items)
        
        items = [ClienteResponse(**item) for item in items_dict]
        
        return ClienteListResponse(
            items=items,
            total=total,
            skip=skip,
            limit=limit
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Obtener detalles de cliente",
    description="Admin: cualquier cliente. User: solo propio"
)
def get_cliente(
    cliente_id: int,
    user_id: Optional[int] = Depends(require_role(allow_customer=True)),
    user_role: str = Query("USER", description="Rol del usuario")
):
    """
    Obtener detalles de un cliente por ID.
    
    Control de acceso:
    - ADMIN: puede obtener cualquier cliente
    - USER: solo puede obtener su propio cliente
    
    Returns:
        - 200: Cliente encontrado
        - 403: No tienes permiso
        - 404: Cliente no existe
    """
    try:
        result = cliente_service.get_cliente(
            cliente_id=cliente_id,
            requesting_user_id=user_id,
            requesting_user_role=user_role
        )
        return ClienteResponse(**result)
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        error_msg = str(e)
        if "no existe" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.patch(
    "/{cliente_id}",
    response_model=ClienteResponse,
    summary="Actualizar cliente",
    description="Admin: puede actualizar cualquier cliente. User: solo propio"
)
def update_cliente(
    cliente_id: int,
    req: ClienteUpdateRequest,
    user_id: Optional[int] = Depends(require_role(allow_customer=True)),
    user_role: str = Query("USER", description="Rol del usuario")
):
    """
    Actualizar cliente existente.
    
    - **nombre**: Nuevo nombre (opcional)
    - **email**: Nuevo email (opcional, debe ser único)
    - **direccion**: Nueva dirección (opcional)
    - **telefono**: Nuevo teléfono (opcional)
    
    Control de acceso:
    - ADMIN: puede actualizar cualquier cliente
    - USER: solo su propio cliente
    
    Returns:
        - 200: Cliente actualizado
        - 400: Datos inválidos
        - 403: No tienes permiso
        - 404: Cliente no encontrado
        - 409: Email ya está registrado
    """
    try:
        result = cliente_service.update_cliente(
            cliente_id=cliente_id,
            nombre=req.nombre,
            email=req.email,
            telefono=req.telefono,
            direccion=req.direccion,
            requesting_user_id=user_id,
            requesting_user_role=user_role
        )
        return ClienteResponse(**result)
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        error_msg = str(e)
        if "no existe" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        elif "ya está registrado" in error_msg:
            raise HTTPException(status_code=409, detail=error_msg)
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.delete(
    "/{cliente_id}",
    status_code=204,
    summary="Eliminar cliente",
    description="Soft-delete: marca cliente como inactivo (admin-only)"
)
def delete_cliente(
    cliente_id: int,
    user_id: int = Depends(require_role("admin"))
):
    """
    Soft-delete de cliente (marcar como inactivo).
    
    El cliente es marcado como inactivo pero los datos se preservan
    para referencias históricas (pedidos, pagos, etc).
    
    Returns:
        - 204: Eliminado correctamente
        - 403: No autorizado (no es admin)
        - 404: Cliente no encontrada
    """
    try:
        cliente_service.soft_delete_cliente(
            cliente_id=cliente_id,
            requesting_user_role="ADMIN"
        )
        return None  # 204 No Content
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        error_msg = str(e)
        if "no existe" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/search",
    response_model=ClienteSearchResponse,
    summary="Buscar clientes",
    description="Buscar clientes por nombre o email (admin-only)"
)
def search_clientes(
    q: str = Query(..., min_length=1, description="Término de búsqueda (nombre o email)"),
    skip: int = Query(0, ge=0, description="Cantidad de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Límite de registros"),
    user_id: int = Depends(require_role("admin"))
):
    """
    Buscar clientes por nombre o email.
    
    Solo administradores pueden usar este endpoint.
    
    Returns:
        - 200: Resultados de búsqueda
        - 400: Búsqueda vacía o parámetros inválidos
        - 403: No autorizado (no es admin)
    """
    try:
        items_dict = cliente_service.search_clientes(
            query=q,
            skip=skip,
            limit=limit,
            requesting_user_role="ADMIN"
        )
        
        items = [ClienteResponse(**item) for item in items_dict]
        
        return ClienteSearchResponse(
            items=items,
            query=q,
            count=len(items)
        )
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.patch(
    "/{cliente_id}/reactivar",
    response_model=ClienteResponse,
    summary="Reactivar cliente",
    description="Reactivar un cliente que fue eliminado (admin-only)"
)
def reactivate_cliente(
    cliente_id: int,
    user_id: int = Depends(require_role("admin"))
):
    """
    Reactivar cliente inactivo.
    
    Marca un cliente previamente eliminado (soft-delete) como activo nuevamente.
    
    Returns:
        - 200: Cliente reactivado
        - 403: No autorizado (no es admin)
        - 404: Cliente no existe
    """
    try:
        result = cliente_service.reactivate_cliente(
            cliente_id=cliente_id,
            requesting_user_role="ADMIN"
        )
        return ClienteResponse(**result)
    
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ValueError as e:
        error_msg = str(e)
        if "no existe" in error_msg:
            raise HTTPException(status_code=404, detail=error_msg)
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
