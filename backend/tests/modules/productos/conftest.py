"""
Fixtures compartidas para tests del módulo productos.
"""

import pytest
from unittest.mock import Mock
from backend.modules.productos.service import ProductService


@pytest.fixture
def mock_uow():
    """Mock Unit of Work con repositorios para productos."""
    uow = Mock()
    uow.productos = Mock()
    uow.categorias = Mock()
    uow.ingredientes = Mock()
    uow.commit = Mock()
    uow.rollback = Mock()
    return uow


@pytest.fixture
def service(mock_uow):
    """ProductService con mock UoW."""
    return ProductService(mock_uow)


@pytest.fixture
def mock_categoria():
    """Mock de una categoría existente."""
    cat = Mock()
    cat.id = 1
    cat.nombre = "Pizzas"
    cat.status = "active"
    return cat


@pytest.fixture
def mock_ingrediente():
    """Mock de un ingrediente existente."""
    ing = Mock()
    ing.id = 1
    ing.nombre = "Harina"
    ing.stock = 100.0
    return ing


@pytest.fixture
def mock_producto():
    """Mock de un producto existente."""
    prod = Mock()
    prod.id = 1
    prod.nombre = "Pizza Margherita"
    prod.base_price = 150.0
    prod.status = "active"
    prod.ingredients = [
        {"ingredient_id": 1, "quantity_required": 0.5}
    ]
    prod.is_active = Mock(return_value=True)
    prod.to_dict = Mock(return_value={
        "id": 1,
        "nombre": "Pizza Margherita",
        "base_price": 150.0,
        "status": "active",
        "categories": [],
        "ingredients": [],
        "stock_disponible": 0.0,
        "created_at": "2026-05-01T10:00:00",
        "updated_at": "2026-05-01T10:00:00",
        "deleted_at": None,
    })
    return prod
