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

from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import Optional
from backend.core.deps import get_uow
from backend.core.uow_postgresql import PostgreSQLUnitOfWork
from .schemas import (
    ProductCreateRequest,
    ProductUpdateRequest,
    ProductResponse,
    ProductDetailResponse,
    ProductStockResponse,
    ProductStockUpdateRequest,
    ProductListResponse
)
from .service import ProductService
from backend.middleware.jwt_middleware import require_role


def _build_detail_response(
    uow: "PostgreSQLUnitOfWork",
    producto,
    product_id: int,
    product_service: ProductService,
) -> ProductDetailResponse:
    """Construye un ProductDetailResponse completo con categorías e ingredientes."""
    stock_int = int(product_service.calculate_product_stock(product_id))

    producto.categories = uow.productos.get_categories_for_product(product_id)

    pis = uow.product_ingredients.get_by_product(product_id)
    producto.ingredients = [
        {
            'id': pi.id,
            'ingredient_id': pi.ingredient_id,
            'quantity_required': pi.quantity_required,
            'created_at': pi.created_at,
            'updated_at': pi.updated_at,
        }
        for pi in pis
    ]

    d = producto.to_dict()
    d['stock_disponible'] = stock_int
    return ProductDetailResponse(**d)

router = APIRouter(
    prefix="/productos",
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
    user_id: int = Depends(require_role("admin", "ADMIN", "stock", "STOCK")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
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
    product_service = ProductService(uow)
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

        return _build_detail_response(uow, producto, producto.id, product_service)

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
    user_id: Optional[int] = Depends(require_role(allow_customer=True)),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
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
    product_service = ProductService(uow)
    try:
        productos = uow.productos.list_active(
            skip=skip,
            limit=limit,
            search=search,
            category_id=category_id,
            sort_by=sort
        )

        # Calcular stock y construir respuesta (to_dict() recalcula con ingredients=[],
        # por eso sobreescribimos stock_disponible explícitamente)
        items = []
        for p in productos:
            stock = product_service.calculate_product_stock(p.id)
            stock_int = int(stock)
            prod_dict = p.to_dict()
            prod_dict['stock_disponible'] = stock_int
            items.append(
                ProductResponse(
                    **prod_dict,
                    precio=p.base_price,
                    disponible=p.status == 'active' and stock_int > 0,
                    stock=stock_int,
                )
            )

        return ProductListResponse(
            items=items,
            total=len(items),
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
    product_id: int = Path(..., gt=0, description="ID del producto"),
    user_id: Optional[int] = Depends(require_role(allow_customer=True)),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
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
    product_service = ProductService(uow)
    try:
        producto = uow.productos.find_by_id(product_id)
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {product_id} no encontrado")

        return _build_detail_response(uow, producto, product_id, product_service)

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
    product_id: int = Path(..., gt=0, description="ID del producto"),
    user_id: Optional[int] = Depends(require_role(allow_customer=True)),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """
    Obtener stock disponible de un producto.

    Calcula: min(stock_disponible_ingrediente / cantidad_requerida)

    Returns:
        - 200: Stock disponible
        - 404: Producto no encontrado
    """
    product_service = ProductService(uow)
    try:
        producto = uow.productos.find_by_id(product_id)
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {product_id} no encontrado")

        stock = product_service.calculate_product_stock(product_id)

        return ProductStockResponse(
            product_id=product_id,
            nombre=producto.nombre,
            stock_disponible=int(stock)
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@router.patch(
    "/{product_id}/stock",
    response_model=ProductStockResponse,
    summary="Actualizar stock del producto",
    description="Actualiza el stock directo de un producto (admin/stock)"
)
def update_product_stock(
    product_id: int = Path(..., gt=0, description="ID del producto"),
    req: ProductStockUpdateRequest = None,
    user_id: int = Depends(require_role("admin", "ADMIN", "stock", "STOCK")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
):
    """
    Actualizar stock del producto directamente.

    Para productos sin ingredientes (ej: bebidas), este valor es el stock efectivo.
    Para productos con ingredientes, el stock calculado sigue derivándose de ingredientes.

    Returns:
        - 200: Stock actualizado
        - 404: Producto no encontrado
    """
    try:
        producto = uow.productos.find_by_id(product_id)
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {product_id} no encontrado")

        nuevo_stock = req.stock if req else 0
        uow.productos.update_stock(product_id, nuevo_stock)
        uow.commit()

        product_service = ProductService(uow)
        stock_calculado = int(product_service.calculate_product_stock(product_id))

        return ProductStockResponse(
            product_id=product_id,
            nombre=producto.nombre,
            stock_disponible=stock_calculado,
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
    product_id: int = Path(..., gt=0, description="ID del producto"),
    req: ProductUpdateRequest = None,
    user_id: int = Depends(require_role("admin", "ADMIN", "stock", "STOCK")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
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
    product_service = ProductService(uow)
    try:
        producto = uow.productos.find_by_id(product_id)
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {product_id} no encontrado")

        # Verificar si puede modificarse (no está en pedidos activos)
        product_service.check_can_modify_product(product_id)

        # Convertir ingredientes Pydantic → dicts antes de validar y actualizar
        ingredients_list = None
        if req and req.ingredients is not None:
            ingredients_list = [
                {'ingredient_id': ing.ingredient_id, 'quantity_required': ing.quantity_required}
                for ing in req.ingredients
            ]

        # Validar nuevo input si se proporciona
        if req:
            if req.nombre or req.base_price or req.categories or ingredients_list:
                product_service.validate_product_input(
                    nombre=req.nombre or producto.nombre,
                    base_price=req.base_price or producto.base_price,
                    descripcion=req.descripcion or producto.descripcion,
                    category_ids=req.categories or [],
                    ingredients=ingredients_list or []
                )

        # Actualizar
        producto_actualizado = uow.productos.update(
            product_id=product_id,
            nombre=req.nombre if req else None,
            descripcion=req.descripcion if req else None,
            base_price=req.base_price if req else None,
            category_ids=req.categories if req else None,
            ingredients=ingredients_list,
        )

        uow.commit()

        return _build_detail_response(uow, producto_actualizado, product_id, product_service)

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
    product_id: int = Path(..., gt=0, description="ID del producto"),
    user_id: int = Depends(require_role("admin", "ADMIN", "stock", "STOCK")),
    uow: PostgreSQLUnitOfWork = Depends(get_uow),
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
    product_service = ProductService(uow)
    try:
        producto = uow.productos.find_by_id(product_id)
        if not producto:
            raise HTTPException(status_code=404, detail=f"Producto {product_id} no encontrado")

        # Verificar si está en ordenes y soft delete
        uow.productos.soft_delete(product_id)

        uow.commit()

        # 204 No Content
        return None

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
