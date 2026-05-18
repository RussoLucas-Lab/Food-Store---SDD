"""
Tests unitarios para CategoryService.

Migrado desde backend/tests/test_categoria_service.py.
Prueba toda la lógica de negocio sin dependencias de FastAPI.
Usa mocks del UoW y repositorios para aislar la lógica.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from backend.modules.categorias.service import CategoryService


@pytest.fixture
def mock_uow():
    """Fixture: Mock Unit of Work con repositorios"""
    uow = Mock()
    uow.categorias = Mock()
    uow.productos = Mock()
    uow.commit = Mock()
    return uow


@pytest.fixture
def service(mock_uow):
    """Fixture: CategoryService con mock UoW"""
    return CategoryService(mock_uow)


class TestCreateCategoria:
    """Tests para CategoryService.create_categoria()"""

    def test_create_categoria_valid(self, service, mock_uow):
        """Crear categoría con nombre y descripción válidos"""
        mock_categoria = Mock()
        mock_categoria.to_dict.return_value = {
            "id": 1,
            "nombre": "Frutas",
            "descripcion": "Frutas frescas",
            "status": "active",
            "created_at": "2026-05-07T12:00:00",
            "updated_at": "2026-05-07T12:00:00"
        }
        mock_uow.categorias.find_by_name.return_value = None
        mock_uow.categorias.create.return_value = mock_categoria

        result = service.create_categoria("Frutas", "Frutas frescas")

        assert result["nombre"] == "Frutas"
        assert result["status"] == "active"
        mock_uow.categorias.find_by_name.assert_called_once()
        mock_uow.categorias.create.assert_called_once_with("Frutas", "Frutas frescas")
        mock_uow.commit.assert_called_once()

    def test_create_categoria_empty_name(self, service, mock_uow):
        """Crear categoría con nombre vacío → ValueError"""
        with pytest.raises(ValueError, match="Nombre requerido"):
            service.create_categoria("", "description")

    def test_create_categoria_whitespace_name(self, service, mock_uow):
        """Crear categoría con nombre solo espacios → ValueError"""
        with pytest.raises(ValueError, match="Nombre requerido"):
            service.create_categoria("   ", "description")

    def test_create_categoria_duplicate_name(self, service, mock_uow):
        """Crear categoría con nombre duplicado → ValueError"""
        mock_existing = Mock()
        mock_uow.categorias.find_by_name.return_value = mock_existing

        with pytest.raises(ValueError, match="ya existe"):
            service.create_categoria("Frutas", "description")

    def test_create_categoria_name_too_long(self, service, mock_uow):
        """Crear categoría con nombre > 100 chars → ValueError"""
        long_name = "x" * 101
        with pytest.raises(ValueError, match="100 caracteres"):
            service.create_categoria(long_name, "description")

    def test_create_categoria_descripcion_too_long(self, service, mock_uow):
        """Crear categoría con descripción > 500 chars → ValueError"""
        long_desc = "x" * 501
        mock_uow.categorias.find_by_name.return_value = None

        with pytest.raises(ValueError, match="500 caracteres"):
            service.create_categoria("Frutas", long_desc)


class TestUpdateCategoria:
    """Tests para CategoryService.update_categoria()"""

    def test_update_categoria_valid(self, service, mock_uow):
        """Actualizar categoría con nombre y descripción válidos"""
        mock_categoria = Mock()
        mock_categoria.id = 1
        mock_categoria.nombre = "Frutas"
        mock_updated = Mock()
        mock_updated.to_dict.return_value = {
            "id": 1,
            "nombre": "Frutas Cítricas",
            "descripcion": "Nueva descripción",
            "status": "active"
        }
        mock_uow.categorias.find_by_id.return_value = mock_categoria
        mock_uow.categorias.find_by_name.return_value = None
        mock_uow.categorias.update.return_value = mock_updated

        result = service.update_categoria(1, "Frutas Cítricas", "Nueva descripción")

        assert result["id"] == 1
        assert result["nombre"] == "Frutas Cítricas"
        mock_uow.categorias.update.assert_called_once()
        mock_uow.commit.assert_called_once()

    def test_update_categoria_not_found(self, service, mock_uow):
        """Actualizar categoría que no existe → ValueError"""
        mock_uow.categorias.find_by_id.return_value = None

        with pytest.raises(ValueError, match="no existe"):
            service.update_categoria(999, "NewName", "desc")

    def test_update_categoria_empty_name(self, service, mock_uow):
        """Actualizar con nombre vacío → ValueError"""
        with pytest.raises(ValueError, match="Nombre requerido"):
            service.update_categoria(1, "", "desc")

    def test_update_categoria_duplicate_name(self, service, mock_uow):
        """Actualizar con nombre duplicado (otra categoría) → ValueError"""
        mock_categoria = Mock()
        mock_categoria.id = 1
        mock_existing = Mock()
        mock_existing.id = 2

        mock_uow.categorias.find_by_id.return_value = mock_categoria
        mock_uow.categorias.find_by_name.return_value = mock_existing

        with pytest.raises(ValueError, match="ya está en uso"):
            service.update_categoria(1, "Nombre de Otra", "desc")


class TestDeleteCategoria:
    """Tests para CategoryService.delete_categoria()"""

    def test_delete_categoria_not_in_use(self, service, mock_uow):
        """Soft-delete categoría no en uso → éxito"""
        mock_categoria = Mock()
        mock_categoria.id = 1
        mock_categoria.nombre = "Frutas"
        mock_categoria.status = "active"
        mock_categoria.descripcion = "Desc"
        mock_categoria.created_at = "2026-05-07T12:00:00"
        mock_categoria.updated_at = "2026-05-07T12:00:00"

        mock_uow.categorias.find_by_id.return_value = mock_categoria
        mock_uow.productos.count_by_category.return_value = 0
        mock_uow.categorias.soft_delete.return_value = True

        result = service.delete_categoria(1)

        assert result["status"] == "inactive"
        mock_uow.categorias.soft_delete.assert_called_once()
        mock_uow.commit.assert_called_once()

    def test_delete_categoria_not_found(self, service, mock_uow):
        """Eliminar categoría que no existe → ValueError"""
        mock_uow.categorias.find_by_id.return_value = None

        with pytest.raises(ValueError, match="no existe"):
            service.delete_categoria(999)

    def test_delete_categoria_in_use(self, service, mock_uow):
        """Eliminar categoría en uso por productos → ValueError"""
        mock_categoria = Mock()
        mock_categoria.id = 1
        mock_categoria.nombre = "Frutas"
        mock_uow.categorias.find_by_id.return_value = mock_categoria
        mock_uow.productos.count_by_category.return_value = 5

        with pytest.raises(ValueError, match="en uso"):
            service.delete_categoria(1)


class TestGetCategoria:
    """Tests para CategoryService.get_categoria()"""

    def test_get_categoria_valid(self, service, mock_uow):
        """Obtener categoría existente"""
        mock_categoria = Mock()
        mock_categoria.id = 1
        mock_categoria.nombre = "Frutas"
        mock_categoria.to_dict.return_value = {
            "id": 1,
            "nombre": "Frutas",
            "status": "active"
        }
        mock_uow.categorias.find_by_id.return_value = mock_categoria

        result = service.get_categoria(1)

        assert result["id"] == 1
        assert result["nombre"] == "Frutas"

    def test_get_categoria_not_found(self, service, mock_uow):
        """Obtener categoría que no existe → ValueError"""
        mock_uow.categorias.find_by_id.return_value = None

        with pytest.raises(ValueError, match="no existe"):
            service.get_categoria(999)


class TestListCategorias:
    """Tests para CategoryService.list_categorias()"""

    def test_list_categorias_no_filters(self, service, mock_uow):
        """Listar categorías sin filtros → retorna lista paginada"""
        mock_cat1 = Mock()
        mock_cat1.to_dict.return_value = {"id": 1, "nombre": "Frutas"}
        mock_cat2 = Mock()
        mock_cat2.to_dict.return_value = {"id": 2, "nombre": "Verduras"}

        mock_uow.categorias.list_active.return_value = [mock_cat1, mock_cat2]

        result = service.list_categorias(skip=0, limit=10)

        assert len(result) == 2
        assert result[0]["nombre"] == "Frutas"
        assert result[1]["nombre"] == "Verduras"

    def test_list_categorias_with_search(self, service, mock_uow):
        """Listar categorías con búsqueda → retorna filtrados"""
        mock_cat1 = Mock()
        mock_cat1.to_dict.return_value = {"id": 1, "nombre": "Frutas Cítricas"}

        mock_uow.categorias.list_active.return_value = [mock_cat1]

        result = service.list_categorias(skip=0, limit=10, search="Frut")

        assert len(result) == 1
        assert result[0]["nombre"] == "Frutas Cítricas"

    def test_list_categorias_empty(self, service, mock_uow):
        """Listar cuando no hay categorías → retorna lista vacía"""
        mock_uow.categorias.list_active.return_value = []

        result = service.list_categorias()

        assert len(result) == 0
