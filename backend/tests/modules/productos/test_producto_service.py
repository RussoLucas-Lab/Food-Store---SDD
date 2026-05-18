"""
Tests unitarios para ProductService.

Prueba la lógica de negocio de productos sin dependencias de FastAPI.
Usa mocks del UoW y repositorios para aislar la lógica.
"""

import pytest
from unittest.mock import Mock, patch
from backend.modules.productos.service import ProductService


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures locales
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_uow():
    uow = Mock()
    uow.productos = Mock()
    uow.categorias = Mock()
    uow.ingredientes = Mock()
    uow.commit = Mock()
    uow.rollback = Mock()
    return uow


@pytest.fixture
def service(mock_uow):
    return ProductService(mock_uow)


# ─────────────────────────────────────────────────────────────────────────────
# 2.2 — crear producto con datos válidos retorna "valid"
# ─────────────────────────────────────────────────────────────────────────────

class TestValidateProductInput:
    """Tests para ProductService.validate_product_input()"""

    def test_valid_product_returns_valid_true(self, service, mock_uow):
        """Crear producto con datos válidos → {"valid": True}"""
        mock_uow.categorias.find_by_id.return_value = Mock()
        mock_uow.ingredientes.find_by_id.return_value = Mock()

        result = service.validate_product_input(
            nombre="Pizza Margherita",
            base_price=150.0,
            descripcion="Pizza clásica",
            category_ids=[1],
            ingredients=[{"ingredient_id": 1, "quantity_required": 0.5}]
        )

        assert result["valid"] is True

    # 2.3 — sin category_ids lanza ValueError
    def test_no_category_ids_raises_value_error(self, service, mock_uow):
        """Sin category_ids → ValueError"""
        with pytest.raises(ValueError, match="categor"):
            service.validate_product_input(
                nombre="Pizza",
                base_price=100.0,
                category_ids=[],
                ingredients=[{"ingredient_id": 1, "quantity_required": 1}]
            )

    def test_none_category_ids_raises_value_error(self, service):
        """category_ids=None → ValueError"""
        with pytest.raises(ValueError):
            service.validate_product_input(
                nombre="Pizza",
                base_price=100.0,
                category_ids=None,
                ingredients=[{"ingredient_id": 1, "quantity_required": 1}]
            )

    # 2.4 — sin ingredients lanza ValueError
    def test_no_ingredients_raises_value_error(self, service, mock_uow):
        """Sin ingredients → ValueError"""
        mock_uow.categorias.find_by_id.return_value = Mock()

        with pytest.raises(ValueError, match="ingrediente"):
            service.validate_product_input(
                nombre="Pizza",
                base_price=100.0,
                category_ids=[1],
                ingredients=[]
            )

    def test_none_ingredients_raises_value_error(self, service, mock_uow):
        """ingredients=None → ValueError"""
        mock_uow.categorias.find_by_id.return_value = Mock()

        with pytest.raises(ValueError):
            service.validate_product_input(
                nombre="Pizza",
                base_price=100.0,
                category_ids=[1],
                ingredients=None
            )

    # 2.5 — base_price <= 0 lanza ValueError
    def test_zero_price_raises_value_error(self, service):
        """base_price = 0 → ValueError"""
        with pytest.raises(ValueError, match="[Pp]recio"):
            service.validate_product_input(
                nombre="Pizza",
                base_price=0,
                category_ids=[1],
                ingredients=[{"ingredient_id": 1, "quantity_required": 1}]
            )

    def test_negative_price_raises_value_error(self, service):
        """base_price < 0 → ValueError"""
        with pytest.raises(ValueError, match="[Pp]recio"):
            service.validate_product_input(
                nombre="Pizza",
                base_price=-10.0,
                category_ids=[1],
                ingredients=[{"ingredient_id": 1, "quantity_required": 1}]
            )

    def test_empty_name_raises_value_error(self, service):
        """nombre vacío → ValueError"""
        with pytest.raises(ValueError, match="[Nn]ombre"):
            service.validate_product_input(
                nombre="",
                base_price=100.0,
                category_ids=[1],
                ingredients=[{"ingredient_id": 1, "quantity_required": 1}]
            )

    def test_nonexistent_category_raises_value_error(self, service, mock_uow):
        """Categoría inexistente → ValueError"""
        mock_uow.categorias.find_by_id.return_value = None

        with pytest.raises(ValueError, match="[Cc]ategor"):
            service.validate_product_input(
                nombre="Pizza",
                base_price=100.0,
                category_ids=[999],
                ingredients=[{"ingredient_id": 1, "quantity_required": 1}]
            )

    def test_nonexistent_ingredient_raises_value_error(self, service, mock_uow):
        """Ingrediente inexistente → ValueError"""
        mock_uow.categorias.find_by_id.return_value = Mock()
        mock_uow.ingredientes.find_by_id.return_value = None

        with pytest.raises(ValueError, match="[Ii]ngrediente"):
            service.validate_product_input(
                nombre="Pizza",
                base_price=100.0,
                category_ids=[1],
                ingredients=[{"ingredient_id": 999, "quantity_required": 1}]
            )


# ─────────────────────────────────────────────────────────────────────────────
# 2.6 — calculate_product_stock con ingrediente disponible
# ─────────────────────────────────────────────────────────────────────────────

class TestCalculateProductStock:
    """Tests para ProductService.calculate_product_stock()"""

    def test_stock_calculated_from_ingredients(self, service, mock_uow):
        """Stock calculado correctamente desde ingrediente."""
        # Producto con 1 ingrediente que requiere 0.5 unidades
        mock_producto = Mock()
        mock_producto.ingredients = [
            {"ingredient_id": 1, "quantity_required": 0.5}
        ]
        mock_uow.productos.find_by_id.return_value = mock_producto

        mock_ingrediente = Mock()
        mock_uow.ingredientes.find_by_id.return_value = mock_ingrediente
        mock_uow.ingredientes.stock_disponible.return_value = 10.0  # 10 unidades disponibles

        stock = service.calculate_product_stock(1)

        # 10.0 / 0.5 = 20.0 productos posibles
        assert stock == 20.0

    def test_stock_is_minimum_of_all_ingredients(self, service, mock_uow):
        """El stock es el mínimo entre todos los ingredientes."""
        mock_producto = Mock()
        mock_producto.ingredients = [
            {"ingredient_id": 1, "quantity_required": 1.0},
            {"ingredient_id": 2, "quantity_required": 1.0},
        ]
        mock_uow.productos.find_by_id.return_value = mock_producto
        mock_uow.ingredientes.find_by_id.return_value = Mock()
        # Ingrediente 1 → stock 5, ingrediente 2 → stock 3
        mock_uow.ingredientes.stock_disponible.side_effect = [5.0, 3.0]

        stock = service.calculate_product_stock(1)

        assert stock == 3.0  # mín(5, 3)

    def test_product_not_found_returns_zero(self, service, mock_uow):
        """Producto no encontrado → retorna 0.0"""
        mock_uow.productos.find_by_id.return_value = None

        stock = service.calculate_product_stock(999)

        assert stock == 0.0

    def test_product_no_ingredients_returns_zero(self, service, mock_uow):
        """Producto sin ingredientes → retorna 0.0"""
        mock_producto = Mock()
        mock_producto.ingredients = []
        mock_uow.productos.find_by_id.return_value = mock_producto

        stock = service.calculate_product_stock(1)

        assert stock == 0.0


# ─────────────────────────────────────────────────────────────────────────────
# 2.7 — deactivate_product pone status = inactive
# ─────────────────────────────────────────────────────────────────────────────

class TestDeactivateProduct:
    """Tests para ProductService.deactivate_product()"""

    def test_deactivate_product_calls_soft_delete(self, service, mock_uow):
        """deactivate_product llama soft_delete y commit."""
        mock_uow.productos.soft_delete.return_value = True

        result = service.deactivate_product(1)

        mock_uow.productos.soft_delete.assert_called_once_with(1)
        mock_uow.commit.assert_called_once()
        assert result is True

    def test_deactivate_nonexistent_product_returns_false(self, service, mock_uow):
        """deactivate_product con ID inexistente → False."""
        mock_uow.productos.soft_delete.return_value = False

        result = service.deactivate_product(999)

        assert result is False


# ─────────────────────────────────────────────────────────────────────────────
# Tests para validate_categories_exist y validate_ingredients_exist
# ─────────────────────────────────────────────────────────────────────────────

class TestValidateHelpers:
    """Tests para helpers de validación."""

    def test_validate_categories_all_exist_returns_true(self, service, mock_uow):
        """Todas las categorías existen → True."""
        mock_uow.categorias.find_by_id.return_value = Mock()

        assert service.validate_categories_exist([1, 2, 3]) is True

    def test_validate_categories_one_missing_returns_false(self, service, mock_uow):
        """Una categoría no existe → False."""
        mock_uow.categorias.find_by_id.side_effect = [Mock(), None, Mock()]

        assert service.validate_categories_exist([1, 2, 3]) is False

    def test_validate_ingredients_all_exist_returns_true(self, service, mock_uow):
        """Todos los ingredientes existen → True."""
        mock_uow.ingredientes.find_by_id.return_value = Mock()

        ingredients = [
            {"ingredient_id": 1, "quantity_required": 1.0},
            {"ingredient_id": 2, "quantity_required": 0.5},
        ]
        assert service.validate_ingredients_exist(ingredients) is True

    def test_validate_ingredients_one_missing_returns_false(self, service, mock_uow):
        """Un ingrediente no existe → False."""
        mock_uow.ingredientes.find_by_id.side_effect = [Mock(), None]

        ingredients = [
            {"ingredient_id": 1, "quantity_required": 1.0},
            {"ingredient_id": 2, "quantity_required": 0.5},
        ]
        assert service.validate_ingredients_exist(ingredients) is False
