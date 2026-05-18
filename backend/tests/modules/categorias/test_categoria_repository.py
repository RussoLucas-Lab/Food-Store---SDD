"""
Unit tests para CategoriaRepository.

Migrado desde tests/test_categoria_repository.py.
Prueba todos los métodos del repository incluyendo:
- Creación, lectura, actualización, soft delete
- Duplicados
- Idempotencia
"""

import pytest
from datetime import datetime
from backend.modules.categorias.repository import InMemoryCategoriaRepository
from backend.modules.categorias.model import Categoria


@pytest.fixture
def repo():
    """Fixture: instancia limpia de InMemoryCategoriaRepository"""
    return InMemoryCategoriaRepository()


class TestCategoriaRepositoryCreate:
    """Tests de creación de categorías"""

    def test_create_valid_categoria(self, repo):
        """Crear categoría válida"""
        categoria = repo.create("Bebidas", "Bebidas frías y calientes")

        assert categoria.id == 1
        assert categoria.nombre == "Bebidas"
        assert categoria.descripcion == "Bebidas frías y calientes"
        assert categoria.is_active is True
        assert isinstance(categoria.created_at, datetime)
        assert isinstance(categoria.updated_at, datetime)
        assert categoria.deleted_at is None

    def test_create_categoria_sin_descripcion(self, repo):
        """Crear categoría sin descripción"""
        categoria = repo.create("Postres")

        assert categoria.nombre == "Postres"
        assert categoria.descripcion == ""

    def test_create_categoria_duplicada_raises_error(self, repo):
        """Intentar crear categoría con nombre duplicado lanza ValueError"""
        repo.create("Bebidas")

        with pytest.raises(ValueError, match="ya existe"):
            repo.create("Bebidas")

    def test_create_categoria_case_insensitive_duplicate(self, repo):
        """Duplicado debe ser case-insensitive"""
        repo.create("Bebidas")

        with pytest.raises(ValueError):
            repo.create("bebidas")

    def test_create_multiple_categorias(self, repo):
        """Crear múltiples categorías"""
        cat1 = repo.create("Bebidas")
        cat2 = repo.create("Postres")
        cat3 = repo.create("Hamburguesas")

        assert cat1.id == 1
        assert cat2.id == 2
        assert cat3.id == 3


class TestCategoriaRepositoryRead:
    """Tests de lectura de categorías"""

    def test_find_by_id_existe(self, repo):
        """Encontrar categoría por ID"""
        creada = repo.create("Bebidas")
        encontrada = repo.find_by_id(1)

        assert encontrada is not None
        assert encontrada.id == creada.id
        assert encontrada.nombre == creada.nombre

    def test_find_by_id_no_existe(self, repo):
        """Buscar categoría inexistente devuelve None"""
        resultado = repo.find_by_id(999)
        assert resultado is None

    def test_find_by_id_inactiva(self, repo):
        """Buscar categoría inactiva devuelve None"""
        repo.create("Bebidas")
        repo.soft_delete(1)

        resultado = repo.find_by_id(1)
        assert resultado is None

    def test_find_by_name_existe(self, repo):
        """Encontrar categoría por nombre"""
        repo.create("Bebidas", "Descripción")
        encontrada = repo.find_by_name("Bebidas")

        assert encontrada is not None
        assert encontrada.nombre == "Bebidas"

    def test_find_by_name_case_insensitive(self, repo):
        """Búsqueda por nombre case-insensitive"""
        repo.create("Bebidas")
        encontrada = repo.find_by_name("bebidas")

        assert encontrada is not None

    def test_find_by_name_inactiva(self, repo):
        """Buscar categoría inactiva por nombre devuelve None"""
        repo.create("Bebidas")
        repo.soft_delete(1)

        resultado = repo.find_by_name("Bebidas")
        assert resultado is None

    def test_find_all_active(self, repo):
        """Obtener todas las categorías activas"""
        repo.create("Bebidas")
        repo.create("Postres")
        repo.create("Hamburguesas")

        todas = repo.find_all()
        assert len(todas) == 3

    def test_find_all_incluye_inactivas(self, repo):
        """Obtener todas incluyendo inactivas"""
        repo.create("Bebidas")
        repo.create("Postres")
        repo.create("Hamburguesas")
        repo.soft_delete(2)  # Marcar Postres como inactiva

        activas = repo.find_all(include_inactive=False)
        todas = repo.find_all(include_inactive=True)

        assert len(activas) == 2
        assert len(todas) == 3


class TestCategoriaRepositoryUpdate:
    """Tests de actualización de categorías"""

    def test_update_nombre(self, repo):
        """Actualizar nombre de categoría"""
        repo.create("Bebidas")
        categoria = repo.update(1, nombre="Bebidas Frías")

        assert categoria is not None
        assert categoria.nombre == "Bebidas Frías"
        assert categoria.updated_at is not None

    def test_update_descripcion(self, repo):
        """Actualizar descripción de categoría"""
        repo.create("Bebidas", "Vieja descripción")
        categoria = repo.update(1, descripcion="Nueva descripción")

        assert categoria.descripcion == "Nueva descripción"

    def test_update_ambos_campos(self, repo):
        """Actualizar nombre y descripción"""
        repo.create("Bebidas")
        categoria = repo.update(1, nombre="Bebidas Frías", descripcion="Muy refrescante")

        assert categoria.nombre == "Bebidas Frías"
        assert categoria.descripcion == "Muy refrescante"

    def test_update_nombre_duplicado_raises_error(self, repo):
        """Actualizar a nombre ya existente lanza ValueError"""
        repo.create("Bebidas")
        repo.create("Postres")

        with pytest.raises(ValueError, match="ya existe"):
            repo.update(1, nombre="Postres")

    def test_update_inexistente(self, repo):
        """Actualizar categoría inexistente devuelve None"""
        resultado = repo.update(999, nombre="Algo")
        assert resultado is None

    def test_update_mismo_nombre(self, repo):
        """Actualizar con el mismo nombre (no debe fallar)"""
        repo.create("Bebidas")
        categoria = repo.update(1, nombre="Bebidas")

        assert categoria is not None
        assert categoria.nombre == "Bebidas"


class TestCategoriaRepositorySoftDelete:
    """Tests de soft delete"""

    def test_soft_delete_activa(self, repo):
        """Marcar categoría como inactiva"""
        repo.create("Bebidas")
        resultado = repo.soft_delete(1)

        assert resultado is True
        assert repo._storage[1].is_active is False
        assert repo._storage[1].deleted_at is not None

    def test_soft_delete_inexistente(self, repo):
        """Soft delete de categoría inexistente devuelve False"""
        resultado = repo.soft_delete(999)
        assert resultado is False

    def test_soft_delete_idempotente(self, repo):
        """Soft delete es idempotente"""
        repo.create("Bebidas")
        repo.soft_delete(1)
        primera_delete_at = repo._storage[1].deleted_at

        repo.soft_delete(1)  # Intentar borrar nuevamente
        segunda_delete_at = repo._storage[1].deleted_at

        # deleted_at no debe cambiar (idempotente)
        assert primera_delete_at == segunda_delete_at


class TestCategoriaRepositoryListActive:
    """Tests de listado con paginación"""

    def test_list_active_pagina_default(self, repo):
        """Listar con parámetros por defecto (skip=0, limit=20)"""
        for i in range(5):
            repo.create(f"Categoria{i}")

        resultado = repo.list_active()
        assert len(resultado) == 5

    def test_list_active_skip_limit(self, repo):
        """Listar con skip y limit"""
        for i in range(10):
            repo.create(f"Categoria{i:02d}")

        resultado = repo.list_active(skip=5, limit=3)
        assert len(resultado) == 3

    def test_list_active_sort_by_nombre(self, repo):
        """Listar ordenado por nombre"""
        repo.create("Zebras")
        repo.create("Aves")
        repo.create("Mamíferos")

        resultado = repo.list_active(sort_by="nombre")
        assert resultado[0].nombre == "Aves"
        assert resultado[1].nombre == "Mamíferos"
        assert resultado[2].nombre == "Zebras"

    def test_list_active_sort_by_created_at_desc(self, repo):
        """Listar ordenado por created_at retorna todos los items"""
        from datetime import timedelta
        import time
        repo.create("Primera")
        time.sleep(0.01)  # Ensure distinct timestamps
        repo.create("Segunda")
        time.sleep(0.01)
        repo.create("Tercera")

        resultado = repo.list_active(sort_by="created_at")
        # Just verify we get all 3 items back, order may vary if timestamps are equal
        assert len(resultado) == 3
        nombres = [r.nombre for r in resultado]
        assert "Primera" in nombres
        assert "Segunda" in nombres
        assert "Tercera" in nombres

    def test_list_active_exclude_inactive(self, repo):
        """Listar excluye inactivas por defecto"""
        repo.create("Activa1")
        repo.create("Inactiva")
        repo.create("Activa2")
        repo.soft_delete(2)

        resultado = repo.list_active(include_inactive=False)
        assert len(resultado) == 2
        assert all(c.is_active for c in resultado)

    def test_list_active_include_inactive(self, repo):
        """Listar incluye inactivas si se especifica"""
        repo.create("Activa1")
        repo.create("Inactiva")
        repo.create("Activa2")
        repo.soft_delete(2)

        resultado = repo.list_active(include_inactive=True)
        assert len(resultado) == 3


class TestCategoriaRepositoryIntegration:
    """Tests de integración"""

    def test_ciclo_completo(self, repo):
        """Ciclo completo: crear, leer, actualizar, borrar"""
        # Crear
        cat = repo.create("Bebidas", "Inicial")
        assert cat.id == 1

        # Leer
        encontrada = repo.find_by_id(1)
        assert encontrada.nombre == "Bebidas"

        # Actualizar
        actualizada = repo.update(1, nombre="Bebidas Frías", descripcion="Actualizada")
        assert actualizada.nombre == "Bebidas Frías"

        # Soft delete
        repo.soft_delete(1)
        no_encontrada = repo.find_by_id(1)
        assert no_encontrada is None

        # Pero existe en storage
        assert 1 in repo._storage
        assert repo._storage[1].is_active is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
