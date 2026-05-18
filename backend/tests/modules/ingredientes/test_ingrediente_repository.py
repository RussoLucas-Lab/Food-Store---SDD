"""
Unit tests para IngredienteRepository.

Migrado desde tests/test_ingrediente_repository.py.
Prueba todos los métodos del repository incluyendo:
- Creación, lectura, actualización, soft delete
- Búsqueda y filtros
- Lógica de stock y disponibilidad
- Duplicados e idempotencia
"""

import pytest
from datetime import datetime
from backend.modules.ingredientes.repository import InMemoryIngredienteRepository
from backend.modules.ingredientes.model import Ingrediente, UnidadMedida


@pytest.fixture
def repo():
    """Fixture: instancia limpia de InMemoryIngredienteRepository"""
    return InMemoryIngredienteRepository()


class TestIngredienteRepositoryCreate:
    """Tests de creación de ingredientes"""

    def test_create_valid_ingrediente(self, repo):
        """Crear ingrediente válido"""
        ingrediente = repo.create(
            nombre="Sal",
            unidad_medida="gramos",
            cantidad_stock=1000,
            cantidad_minima=100,
            descripcion="Sal de mesa"
        )

        assert ingrediente.id == 1
        assert ingrediente.nombre == "Sal"
        assert ingrediente.descripcion == "Sal de mesa"
        assert ingrediente.unidad_medida == "gramos"
        assert ingrediente.cantidad_stock == 1000
        assert ingrediente.cantidad_minima == 100
        assert ingrediente.is_active is True
        assert isinstance(ingrediente.created_at, datetime)
        assert isinstance(ingrediente.updated_at, datetime)
        assert ingrediente.deleted_at is None

    def test_create_ingrediente_sin_descripcion(self, repo):
        """Crear ingrediente sin descripción"""
        ingrediente = repo.create(
            nombre="Azúcar",
            unidad_medida="kilos",
            cantidad_stock=500,
            cantidad_minima=50
        )

        assert ingrediente.nombre == "Azúcar"
        assert ingrediente.descripcion == ""

    def test_create_ingrediente_con_categoria(self, repo):
        """Crear ingrediente con categoría"""
        ingrediente = repo.create(
            nombre="Harina",
            unidad_medida="kilos",
            cantidad_stock=100,
            cantidad_minima=10,
            categoria_id=5
        )

        assert ingrediente.categoria_id == 5

    def test_create_ingrediente_duplicado_raises_error(self, repo):
        """Intentar crear ingrediente con nombre duplicado lanza ValueError"""
        repo.create("Leche", "litros", 100, 10)

        with pytest.raises(ValueError, match="ya existe"):
            repo.create("Leche", "litros", 50, 5)

    def test_create_ingrediente_unidad_invalida(self, repo):
        """Intentar crear ingrediente con unidad inválida lanza ValueError"""
        with pytest.raises(ValueError, match="inválida"):
            repo.create("Mantequilla", "toneladas", 10, 1)

    def test_create_multiple_ingredientes(self, repo):
        """Crear múltiples ingredientes con IDs secuenciales"""
        ing1 = repo.create("Ingrediente1", "gramos", 100, 10)
        ing2 = repo.create("Ingrediente2", "litros", 50, 5)

        assert ing1.id == 1
        assert ing2.id == 2


class TestIngredienteRepositoryRead:
    """Tests de lectura de ingredientes"""

    def test_find_by_id_existing(self, repo):
        """Encontrar ingrediente existente por id"""
        created = repo.create("Chocolate", "gramos", 200, 20)
        found = repo.find_by_id(created.id)

        assert found is not None
        assert found.nombre == "Chocolate"

    def test_find_by_id_nonexistent(self, repo):
        """Buscar ingrediente inexistente retorna None"""
        result = repo.find_by_id(999)
        assert result is None

    def test_find_by_id_inactive_returns_none(self, repo):
        """Buscar ingrediente inactivo retorna None"""
        created = repo.create("Canela", "gramos", 50, 5)
        repo.soft_delete(created.id)

        result = repo.find_by_id(created.id)
        assert result is None

    def test_find_by_name_existing(self, repo):
        """Encontrar ingrediente por nombre"""
        repo.create("Vainilla", "mililitros", 100, 10)
        found = repo.find_by_name("Vainilla")

        assert found is not None
        assert found.nombre == "Vainilla"

    def test_find_by_name_case_insensitive(self, repo):
        """Búsqueda por nombre es case-insensitive"""
        repo.create("Pimienta", "gramos", 50, 5)

        found1 = repo.find_by_name("pimienta")
        found2 = repo.find_by_name("PIMIENTA")

        assert found1 is not None
        assert found2 is not None

    def test_find_by_name_nonexistent(self, repo):
        """Buscar ingrediente no existente retorna None"""
        result = repo.find_by_name("Inexistente")
        assert result is None


class TestIngredienteRepositoryUpdate:
    """Tests de actualización de ingredientes"""

    def test_update_nombre(self, repo):
        """Actualizar nombre de ingrediente"""
        created = repo.create("OldName", "gramos", 100, 10)
        original_updated_at = created.updated_at
        updated = repo.update(created.id, nombre="NewName")

        assert updated.nombre == "NewName"
        assert updated.updated_at >= original_updated_at

    def test_update_stock(self, repo):
        """Actualizar stock de ingrediente"""
        created = repo.create("Nueces", "gramos", 100, 10)
        updated = repo.update(created.id, cantidad_stock=500)

        assert updated.cantidad_stock == 500

    def test_update_cantidad_minima(self, repo):
        """Actualizar cantidad mínima"""
        created = repo.create("Almendras", "gramos", 200, 20)
        updated = repo.update(created.id, cantidad_minima=50)

        assert updated.cantidad_minima == 50

    def test_update_nonexistent_returns_none(self, repo):
        """Actualizar ingrediente inexistente retorna None"""
        result = repo.update(999, nombre="Test")
        assert result is None

    def test_update_nombre_duplicado_raises_error(self, repo):
        """Actualizar a nombre duplicado lanza error"""
        repo.create("Nombre1", "gramos", 100, 10)
        ing2 = repo.create("Nombre2", "gramos", 50, 5)

        with pytest.raises(ValueError, match="ya existe"):
            repo.update(ing2.id, nombre="Nombre1")

    def test_update_stock_negativo_raises_error(self, repo):
        """Actualizar con stock negativo lanza error"""
        created = repo.create("Test", "gramos", 100, 10)

        with pytest.raises(ValueError, match="negativa"):
            repo.update(created.id, cantidad_stock=-50)


class TestIngredienteRepositorySoftDelete:
    """Tests de soft delete"""

    def test_soft_delete_active(self, repo):
        """Soft delete marca ingrediente como inactivo"""
        created = repo.create("ToDelete", "gramos", 100, 10)
        result = repo.soft_delete(created.id)

        assert result is True
        assert created.is_active is False
        assert created.deleted_at is not None

    def test_soft_delete_idempotent(self, repo):
        """Soft delete es idempotente"""
        created = repo.create("ToDelete", "gramos", 100, 10)
        repo.soft_delete(created.id)
        result2 = repo.soft_delete(created.id)

        assert result2 is True

    def test_soft_delete_nonexistent(self, repo):
        """Soft delete de inexistente retorna False"""
        result = repo.soft_delete(999)
        assert result is False


class TestIngredienteRepositorySearch:
    """Tests de búsqueda y filtros"""

    def test_buscar_por_nombre_exact(self, repo):
        """Buscar por nombre exacto"""
        repo.create("Café", "gramos", 100, 10)
        results = repo.buscar_por_nombre("Café")

        assert len(results) == 1
        assert results[0].nombre == "Café"

    def test_buscar_por_nombre_partial(self, repo):
        """Buscar por nombre parcial"""
        repo.create("Café Premium", "gramos", 100, 10)
        repo.create("Café Regular", "gramos", 50, 5)

        results = repo.buscar_por_nombre("Café")
        assert len(results) == 2

    def test_buscar_por_nombre_case_insensitive(self, repo):
        """Búsqueda por nombre es case-insensitive"""
        repo.create("Té", "gramos", 100, 10)

        results1 = repo.buscar_por_nombre("té")
        results2 = repo.buscar_por_nombre("TÉ")

        assert len(results1) == 1
        assert len(results2) == 1

    def test_buscar_sin_resultados(self, repo):
        """Buscar sin resultados retorna lista vacía"""
        results = repo.buscar_por_nombre("Inexistente")
        assert results == []

    def test_list_active_all(self, repo):
        """Listar todos los ingredientes activos"""
        repo.create("Ing1", "gramos", 100, 10)
        repo.create("Ing2", "litros", 50, 5)

        results = repo.list_active()
        assert len(results) == 2

    def test_list_active_with_pagination(self, repo):
        """Listar con paginación"""
        for i in range(5):
            repo.create(f"Ing{i}", "gramos", 100, 10)

        results = repo.list_active(skip=0, limit=2)
        assert len(results) == 2

    def test_list_active_filter_categoria(self, repo):
        """Filtrar por categoría"""
        repo.create("Ing1", "gramos", 100, 10, categoria_id=1)
        repo.create("Ing2", "litros", 50, 5, categoria_id=2)

        results = repo.list_active(categoria_id=1)
        assert len(results) == 1
        assert results[0].categoria_id == 1

    def test_list_active_filter_disponibles(self, repo):
        """Filtrar solo disponibles (stock > 0)"""
        ing1 = repo.create("Ing1", "gramos", 100, 10)
        ing2 = repo.create("Ing2", "gramos", 50, 5)

        ing2.cantidad_reservada = 50  # Stock disponible = 0

        results = repo.list_active(disponibles_solo=True)
        assert any(i.id == ing1.id for i in results)


class TestIngredienteRepositoryStock:
    """Tests de lógica de stock"""

    def test_puede_descontar_sufficient(self, repo):
        """Verificar disponibilidad con stock suficiente"""
        created = repo.create("Stock1", "gramos", 1000, 100)
        result = repo.puede_descontar(created.id, 500)

        assert result is True

    def test_puede_descontar_insufficient(self, repo):
        """Verificar disponibilidad con stock insuficiente"""
        created = repo.create("Stock2", "gramos", 100, 10)
        result = repo.puede_descontar(created.id, 500)

        assert result is False

    def test_puede_descontar_negative_cantidad(self, repo):
        """Descontar cantidad negativa lanza error"""
        created = repo.create("Stock3", "gramos", 100, 10)

        with pytest.raises(ValueError):
            repo.puede_descontar(created.id, -100)

    def test_puede_descontar_inactive(self, repo):
        """Descontar de ingrediente inactivo lanza error"""
        created = repo.create("Stock4", "gramos", 100, 10)
        repo.soft_delete(created.id)

        with pytest.raises(ValueError):
            repo.puede_descontar(created.id, 10)

    def test_stock_disponible(self, repo):
        """Calcular stock disponible"""
        created = repo.create("StockCalc", "gramos", 1000, 100)
        created.cantidad_reservada = 300

        available = repo.stock_disponible(created.id)
        assert available == 700
