"""
Routers para operaciones CRUD de Productos.

Proporciona 6 endpoints RESTful:
- POST /api/productos (crear, admin-only)
- GET /api/productos (listar con filtros)
- GET /api/productos/{id} (detalle)
- GET /api/productos/{id}/stock (stock disponible)
- PUT /api/productos/{id} (actualizar, admin-only)
- DELETE /api/productos/{id} (soft delete, admin-only)
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from uow.inmemory import InMemoryUnitOfWork
from backend.schemas.product_schema import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    ProductDetailResponse,
    ProductStockResponse,
    ProductListResponse
)
from backend.services.product_service import ProductService
from backend.middleware.jwt_middleware import require_role

# Instancia de UoW (en producción sería inyectada)
uow = InMemoryUnitOfWork()
product_service = ProductService(uow)

router = APIRouter(
    prefix="/api/productos",
    tags=["productos"],
    responses={404: {"description": "Not found"}}
)


@router.post(
    "",
    response_model=ProductDetailResponse,
    status_code=201,
    summary="Crear nuevo producto",
    description="Solo administradores pueden crear productos"
)
def create_product(
    req: ProductCreateRequest,
    user_id: int = Depends(require_role("admin"))
):
    """
    Crear nuevo producto con composición de ingredientes.
    
    - **nombre**: Requerido, 1-100 caracteres, único
    - **base_price**: Requerido, > 0
    - **descripcion**: Opcional, máximo 500 caracteres
    - **categories**: Array requerido, mín 1 categoría que debe existir
    - **ingredients**: Array requerido, mín 1 ingrediente con quantity_required > 0
    
    Returns:
        - 201: Producto creado exitosamente
        - 400: Datos inválidos
        - 403: Usuario no autorizado (no es admin)
        - 409: Nombre ya existe o categoría/ingrediente no encontrado
    """
    try:
        # Validar input
        product_service.validate_product_input(
            nombre=req.nombre,
            base_price=req.base_price,
            descripcion=req.descripcion or "",
            category_ids=req.categories,
            ingredients=[{
                'ingredient_id': ing.ingredient_id,
                'quantity_required': ing.quantity_required
            } for ing in req.ingredients]
        )
        
        # Verificar nombre no duplicado
        if uow.productos.find_by_name(req.nombre):
            raise HTTPException(
                status_code=409,
                detail=f"Producto '{req.nombre}' ya existe"
            )
        
        # Crear producto
        producto = uow.productos.create(
            nombre=req.nombre,
            base_price=req.base_price,
            descripcion=req.descripcion or "",
            category_ids=req.categories,
            ingredients=[{
                'ingredient_id': ing.ingredient_id,
                'quantity_required': ing.quantity_required
            } for ing in req.ingredients]
        )
        
        uow.commit()
        
        # Calcular stock disponible
        stock = product_service.calculate_product_stock(producto.id)
        producto_dict = producto.to_dict()
        producto_dict['stock_disponible'] = stock
        
        return ProductDetailResponse(**producto_dict)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "",
    response_model=ProductListResponse,
    summary="Listar productos",
    description="Devuelve productos activos con paginación y filtros"
)
def list_productos(
    skip: int = Query(0, ge=0, description="Cantidad de registros a saltar"),
    limit: int = Query(20, ge=1, le=100, description="Límite de registros (máximo 100)"),
    search: Optional[str] = Query(None, max_length=100, description="Búsqueda por nombre (parcial)"),
    category_id: Optional[int] = Query(None, gt=0, description="Filtrar por categoría"),
    sort: str = Query("id", regex="^(id|nombre|base_price)$", description="Campo de ordenamiento"),
    user_id: Optional[int] = Depends(require_role(allow_customer=True))
):
    """
    Listar productos.
    
    - **skip**: Registros a saltar (paginación)
    - **limit**: Límite por página (máximo 100)
    - **search**: Búsqueda parcial por nombre (case-insensitive)
    - **category_id**: Filtrar por categoría
    - **sort**: Ordenar por: id, nombre, o base_price
    
    Returns:
        - 200: Listado de productos activos
        - 400: Parámetros inválidos
    """
    try:
        productos = uow.productos.list_active(
            skip=skip,
            limit=limit,
            search=search,
            category_id=category_id,
            sort_by=sort
        )
        
        # Agregar stock disponible a cada producto
        for prod in productos:
            prod.stock_disponible = product_service.calculate_product_stock(prod.id)
        
        # Formatear respuesta
        items = [ProductResponse(**p.to_dict()) for p in productos]
        
        return ProductListResponse(
            items=items,
            total=len(items),  # En producción: usar COUNT(*) de BD
            skip=skip,
            limit=limit
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/{product_id}",
    response_model=ProductDetailResponse,
    summary="Obtener detalle de producto",
    description="Retorna información completa del producto incluyendo composición"
)
def get_product(
    product_id: int = Query(..., gt=0, description="ID del producto"),
    user_id: Optional[int] = Depends(require_role(allow_customer=True))
):
    """
    Obtener detalle completo de un producto.
    
    Incluye:
    - Información básica (nombre, precio, descripción)
    - Categorías asignadas
    - Ingredientes con cantidades
    - Stock disponible calculado
    
    Returns:
        - 200: Detalle del producto
        - 404: Producto no encontrado
    """
    try:
        producto = uow.productos.find_by_id(product_id)
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {product_id} no encontrado")
        
        # Calcular stock
        stock = product_service.calculate_product_stock(product_id)
        producto_dict = producto.to_dict()
        producto_dict['stock_disponible'] = stock
        
        return ProductDetailResponse(**producto_dict)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.get(
    "/{product_id}/stock",
    response_model=ProductStockResponse,
    summary="Obtener stock disponible",
    description="Retorna el stock disponible calculado de un producto"
)
def get_product_stock(
    product_id: int = Query(..., gt=0, description="ID del producto"),
    user_id: Optional[int] = Depends(require_role(allow_customer=True))
):
    """
    Obtener stock disponible de un producto.
    
    Calcula: min(stock_disponible_ingrediente / cantidad_requerida)
    
    Returns:
        - 200: Stock disponible
        - 404: Producto no encontrado
    """
    try:
        producto = uow.productos.find_by_id(product_id)
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {product_id} no encontrado")
        
        stock = product_service.calculate_product_stock(product_id)
        
        return ProductStockResponse(
            product_id=product_id,
            nombre=producto.nombre,
            stock_disponible=stock
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.put(
    "/{product_id}",
    response_model=ProductDetailResponse,
    summary="Actualizar producto",
    description="Solo administradores pueden actualizar productos"
)
def update_product(
    product_id: int = Query(..., gt=0, description="ID del producto"),
    req: ProductUpdateRequest = None,
    user_id: int = Depends(require_role("admin"))
):
    """
    Actualizar producto existente.
    
    Se pueden cambiar: nombre, descripción, precio, categorías, ingredientes.
    
    Returns:
        - 200: Producto actualizado
        - 400: Datos inválidos
        - 403: Usuario no autorizado
        - 404: Producto no encontrado
        - 409: Nombre duplicado o producto en uso
    """
    try:
        producto = uow.productos.find_by_id(product_id)
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {product_id} no encontrado")
        
        # Verificar si puede modificarse (no está en pedidos activos)
        # Esta validación completa se hace en Change 8
        product_service.check_can_modify_product(product_id)
        
        # Validar nuevo input si se proporciona
        if req:
            if req.nombre or req.base_price or req.categories or req.ingredients:
                product_service.validate_product_input(
                    nombre=req.nombre or producto.nombre,
                    base_price=req.base_price or producto.base_price,
                    descripcion=req.descripcion or producto.descripcion,
                    category_ids=req.categories or [],
                    ingredients=req.ingredients or []
                )
        
        # Actualizar
        producto_actualizado = uow.productos.update(
            product_id=product_id,
            nombre=req.nombre if req else None,
            descripcion=req.descripcion if req else None,
            base_price=req.base_price if req else None,
            category_ids=req.categories if req else None,
            ingredients=req.ingredients if req else None
        )
        
        uow.commit()
        
        # Calcular stock
        stock = product_service.calculate_product_stock(product_id)
        producto_dict = producto_actualizado.to_dict()
        producto_dict['stock_disponible'] = stock
        
        return ProductDetailResponse(**producto_dict)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.delete(
    "/{product_id}",
    status_code=204,
    summary="Eliminar producto",
    description="Solo administradores pueden eliminar productos (soft delete)"
)
def delete_product(
    product_id: int = Query(..., gt=0, description="ID del producto"),
    user_id: int = Depends(require_role("admin"))
):
    """
    Eliminar (soft delete) un producto.
    
    Si el producto nunca fue usado en pedidos: elimina completamente.
    Si está en historial de pedidos: marca como inactivo.
    
    Returns:
        - 204: Producto eliminado
        - 404: Producto no encontrado
        - 409: Producto en uso (no puede eliminarse completamente)
    """
    try:
        producto = uow.productos.find_by_id(product_id)
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {product_id} no encontrado")
        
        # Verificar si está en ordenes
        if product_service.uow.productos.is_used_in_orders(product_id):
            # Soft delete
            uow.productos.soft_delete(product_id)
        else:
            # Hard delete (en memoria, solo marcamos inactivo; en BD se eliminaría fila)
            uow.productos.soft_delete(product_id)
        
        uow.commit()
        
        # 204 No Content
        return None
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
