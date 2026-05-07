"""
Tests unitarios para IngredientService.

Prueba toda la lógica de negocio sin dependencias de FastAPI.
Usa mocks del UoW y repositorios para aislar la lógica.

Coverage target: > 90%
"""

import pytest
from unittest.mock import Mock, MagicMock
from backend.services.ingrediente_service import IngredientService


@pytest.fixture
def mock_uow():
    """Fixture: Mock Unit of Work"""
    uow = Mock()
    uow.ingredientes = Mock()
    uow.productos = Mock()
    uow.commit = Mock()
    return uow


@pytest.fixture
def service(mock_uow):
    """Fixture: IngredientService con mock UoW"""
    return IngredientService(mock_uow)


class TestCreateIngrediente:
    """Tests para IngredientService.create_ingrediente()"""
    
    def test_create_ingrediente_valid(self, service, mock_uow):
        """✓ Crear ingrediente con datos válidos"""
        mock_ing = Mock()
        mock_ing.to_dict.return_value = {
            "id": 1,
            "nombre": "Harina",
            "unidad_medida": "gramos",
            "cantidad_stock": 100,
            "cantidad_minima": 10,
            "status": "active"
        }
        mock_uow.ingredientes.find_by_name.return_value = None
        mock_uow.ingredientes.create.return_value = mock_ing
        
        result = service.create_ingrediente(
            nombre="Harina",
            unidad_medida="gramos",
            cantidad_stock=100,
            cantidad_minima=10
        )
        
        assert result["nombre"] == "Harina"
        mock_uow.commit.assert_called_once()
    
    def test_create_ingrediente_empty_name(self, service, mock_uow):
        """❌ Nombre vacío → ValueError"""
        with pytest.raises(ValueError, match="Nombre requerido"):
            service.create_ingrediente("", "gramos", 100, 10)
    
    def test_create_ingrediente_duplicate_name(self, service, mock_uow):
        """❌ Nombre duplicado → ValueError"""
        mock_uow.ingredientes.find_by_name.return_value = Mock()
        
        with pytest.raises(ValueError, match="ya existe"):
            service.create_ingrediente("Harina", "gramos", 100, 10)
    
    def test_create_ingrediente_invalid_unidad(self, service, mock_uow):
        """❌ Unidad de medida inválida → ValueError"""
        mock_uow.ingredientes.find_by_name.return_value = None
        
        with pytest.raises(ValueError, match="Unidad medida debe ser"):
            service.create_ingrediente("Harina", "toneladas", 100, 10)
    
    def test_create_ingrediente_negative_stock(self, service, mock_uow):
        """❌ Stock negativo → ValueError"""
        mock_uow.ingredientes.find_by_name.return_value = None
        
        with pytest.raises(ValueError, match="Stock no puede ser negativo"):
            service.create_ingrediente("Harina", "gramos", -50, 10)
    
    def test_create_ingrediente_negative_minima(self, service, mock_uow):
        """❌ Cantidad mínima negativa → ValueError"""
        mock_uow.ingredientes.find_by_name.return_value = None
        
        with pytest.raises(ValueError, match="Cantidad mínima no puede ser negativa"):
            service.create_ingrediente("Harina", "gramos", 100, -5)
    
    def test_create_ingrediente_descripcion_too_long(self, service, mock_uow):
        """❌ Descripción > 500 chars → ValueError"""
        mock_uow.ingredientes.find_by_name.return_value = None
        long_desc = "x" * 501
        
        with pytest.raises(ValueError, match="500 caracteres"):
            service.create_ingrediente("Harina", "gramos", 100, 10, descripcion=long_desc)


class TestUpdateIngrediente:
    """Tests para IngredientService.update_ingrediente()"""
    
    def test_update_ingrediente_valid(self, service, mock_uow):
        """✓ Actualizar ingrediente con datos válidos"""
        mock_ing = Mock()
        mock_ing.id = 1
        mock_ing.to_dict.return_value = {"id": 1, "cantidad_stock": 200}
        
        mock_uow.ingredientes.get_by_id.return_value = mock_ing
        mock_uow.ingredientes.find_by_name.return_value = None
        
        result = service.update_ingrediente(1, cantidad_stock=200)
        
        assert result["id"] == 1
        mock_uow.commit.assert_called_once()
    
    def test_update_ingrediente_not_found(self, service, mock_uow):
        """❌ ID no existe → ValueError"""
        mock_uow.ingredientes.get_by_id.return_value = None
        
        with pytest.raises(ValueError, match="no existe"):
            service.update_ingrediente(999)
    
    def test_update_ingrediente_negative_stock(self, service, mock_uow):
        """❌ Stock negativo → ValueError"""
        mock_ing = Mock()
        mock_uow.ingredientes.get_by_id.return_value = mock_ing
        
        with pytest.raises(ValueError, match="Stock no puede ser negativo"):
            service.update_ingrediente(1, cantidad_stock=-50)


class TestDeleteIngrediente:
    """Tests para IngredientService.delete_ingrediente()"""
    
    def test_delete_ingrediente_not_in_use(self, service, mock_uow):
        """✓ Soft-delete ingrediente no en uso"""
        mock_ing = Mock()
        mock_ing.id = 1
        mock_ing.nombre = "Harina"
        mock_ing.to_dict.return_value = {"id": 1, "status": "inactive"}
        
        mock_uow.ingredientes.get_by_id.return_value = mock_ing
        mock_uow.productos.count_by_ingredient.return_value = 0
        
        result = service.delete_ingrediente(1)
        
        assert result["status"] == "inactive"
        mock_uow.commit.assert_called_once()
    
    def test_delete_ingrediente_not_found(self, service, mock_uow):
        """❌ ID no existe → ValueError"""
        mock_uow.ingredientes.get_by_id.return_value = None
        
        with pytest.raises(ValueError, match="no existe"):
            service.delete_ingrediente(999)
    
    def test_delete_ingrediente_in_use(self, service, mock_uow):
        """❌ En uso por productos → ValueError"""
        mock_ing = Mock()
        mock_ing.nombre = "Harina"
        mock_uow.ingredientes.get_by_id.return_value = mock_ing
        mock_uow.productos.count_by_ingredient.return_value = 3
        
        with pytest.raises(ValueError, match="en uso"):
            service.delete_ingrediente(1)


class TestGetIngrediente:
    """Tests para IngredientService.get_ingrediente()"""
    
    def test_get_ingrediente_valid(self, service, mock_uow):
        """✓ Obtener ingrediente existente"""
        mock_ing = Mock()
        mock_ing.to_dict.return_value = {"id": 1, "nombre": "Harina"}
        mock_uow.ingredientes.get_by_id.return_value = mock_ing
        
        result = service.get_ingrediente(1)
        
        assert result["id"] == 1
    
    def test_get_ingrediente_not_found(self, service, mock_uow):
        """❌ ID no existe → ValueError"""
        mock_uow.ingredientes.get_by_id.return_value = None
        
        with pytest.raises(ValueError, match="no existe"):
            service.get_ingrediente(999)


class TestListIngredientes:
    """Tests para IngredientService.list_ingredientes()"""
    
    def test_list_ingredientes_no_filters(self, service, mock_uow):
        """✓ Listar sin filtros"""
        mock_ing1 = Mock()
        mock_ing1.to_dict.return_value = {"id": 1, "nombre": "Harina"}
        mock_ing2 = Mock()
        mock_ing2.to_dict.return_value = {"id": 2, "nombre": "Azúcar"}
        
        mock_uow.ingredientes.list_all.return_value = [mock_ing1, mock_ing2]
        
        result = service.list_ingredientes()
        
        assert len(result) == 2
        mock_uow.ingredientes.list_all.assert_called_once()
    
    def test_list_ingredientes_with_filters(self, service, mock_uow):
        """✓ Listar con filtros (unidad, categoría, búsqueda)"""
        mock_ing = Mock()
        mock_ing.to_dict.return_value = {"id": 1}
        mock_uow.ingredientes.list_all.return_value = [mock_ing]
        
        result = service.list_ingredientes(
            search="Har",
            unidad_medida="gramos",
            categoria_id=5
        )
        
        assert len(result) == 1
        call_kwargs = mock_uow.ingredientes.list_all.call_args[1]
        assert call_kwargs["search"] == "Har"
        assert call_kwargs["unidad_medida"] == "gramos"
        assert call_kwargs["categoria_id"] == 5


class TestGetStockHistory:
    """Tests para IngredientService.get_stock_history()"""
    
    def test_get_stock_history_valid(self, service, mock_uow):
        """✓ Obtener historial de stock"""
        mock_ing = Mock()
        mock_uow.ingredientes.get_by_id.return_value = mock_ing
        mock_uow.ingredientes.get_stock_history.return_value = [
            {"id": 1, "cantidad_anterior": 100, "cantidad_nueva": 150, "motivo": "purchase"},
            {"id": 2, "cantidad_anterior": 150, "cantidad_nueva": 100, "motivo": "use"}
        ]
        
        result = service.get_stock_history(1)
        
        assert len(result) == 2
    
    def test_get_stock_history_not_found(self, service, mock_uow):
        """❌ ID no existe → ValueError"""
        mock_uow.ingredientes.get_by_id.return_value = None
        
        with pytest.raises(ValueError, match="no existe"):
            service.get_stock_history(999)
    
    def test_get_stock_history_empty(self, service, mock_uow):
        """✓ Sin historial → retorna []"""
        mock_ing = Mock()
        mock_uow.ingredientes.get_by_id.return_value = mock_ing
        mock_uow.ingredientes.get_stock_history.return_value = None
        
        result = service.get_stock_history(1)
        
        assert result == []
