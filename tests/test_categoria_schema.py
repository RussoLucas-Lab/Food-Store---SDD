"""
Unit tests para Pydantic schemas de Categoría.

Prueba validación de inputs, sanitización y edge cases.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from backend.schemas.categoria_schema import (
    CategoriaCreateRequest,
    CategoriaUpdateRequest,
    CategoriaResponse,
    CategoriaListResponse
)


class TestCategoriaCreateRequest:
    """Tests para CategoriaCreateRequest"""
    
    def test_create_valid_with_descripcion(self):
        """Crear request válido con descripción"""
        req = CategoriaCreateRequest(
            nombre="Bebidas",
            descripcion="Bebidas frías y calientes"
        )
        assert req.nombre == "Bebidas"
        assert req.descripcion == "Bebidas frías y calientes"
    
    def test_create_valid_sin_descripcion(self):
        """Crear request sin descripción"""
        req = CategoriaCreateRequest(nombre="Postres")
        assert req.nombre == "Postres"
        assert req.descripcion is None
    
    def test_create_nombre_vacio_raises_error(self):
        """Nombre vacío debe fallar"""
        with pytest.raises(ValidationError) as exc_info:
            CategoriaCreateRequest(nombre="", descripcion="Test")
        
        assert "at least 1 character" in str(exc_info.value) or "min_length" in str(exc_info.value)
    
    def test_create_nombre_muy_largo_raises_error(self):
        """Nombre > 100 caracteres falla"""
        nombre_largo = "a" * 101
        with pytest.raises(ValidationError):
            CategoriaCreateRequest(nombre=nombre_largo)
    
    def test_create_nombre_con_caracteres_peligrosos_raises_error(self):
        """Caracteres peligrosos en nombre"""
        with pytest.raises(ValidationError):
            CategoriaCreateRequest(nombre="Bebidas<script>")
        
        with pytest.raises(ValidationError):
            CategoriaCreateRequest(nombre="Bebidas'; DROP TABLE--")
    
    def test_create_descripcion_muy_larga_raises_error(self):
        """Descripción > 500 caracteres falla"""
        desc_larga = "a" * 501
        with pytest.raises(ValidationError):
            CategoriaCreateRequest(nombre="Valid", descripcion=desc_larga)
    
    def test_create_sanitiza_espacios_en_blanco(self):
        """Espacios en blanco al inicio/final se sanitizan"""
        req = CategoriaCreateRequest(nombre="  Bebidas  ", descripcion="  Descripción  ")
        assert req.nombre == "Bebidas"
        assert req.descripcion == "Descripción"
    
    def test_create_nombre_caracteres_permitidos(self):
        """Nombres con caracteres permitidos pasan"""
        # Letras, números, acentos, guiones, puntos
        req = CategoriaCreateRequest(nombre="Bebidas-Frías Nº 1.")
        assert req.nombre == "Bebidas-Frías Nº 1."
    
    def test_create_nombre_acentos(self):
        """Nombres con acentos son permitidos"""
        req = CategoriaCreateRequest(nombre="Postres Lácteos")
        assert req.nombre == "Postres Lácteos"


class TestCategoriaUpdateRequest:
    """Tests para CategoriaUpdateRequest"""
    
    def test_update_solo_nombre(self):
        """Update solo nombre"""
        req = CategoriaUpdateRequest(nombre="Nuevo Nombre")
        assert req.nombre == "Nuevo Nombre"
        assert req.descripcion is None
    
    def test_update_solo_descripcion(self):
        """Update solo descripción"""
        req = CategoriaUpdateRequest(descripcion="Nueva descripción")
        assert req.nombre is None
        assert req.descripcion == "Nueva descripción"
    
    def test_update_ambos(self):
        """Update nombre y descripción"""
        req = CategoriaUpdateRequest(
            nombre="Nuevo",
            descripcion="Nueva desc"
        )
        assert req.nombre == "Nuevo"
        assert req.descripcion == "Nueva desc"
    
    def test_update_vacio_es_valido(self):
        """Update sin campos es válido (permite patch)"""
        req = CategoriaUpdateRequest()
        assert req.nombre is None
        assert req.descripcion is None
    
    def test_update_nombre_vacio_string_raises_error(self):
        """Nombre como string vacío falla"""
        with pytest.raises(ValidationError):
            CategoriaUpdateRequest(nombre="")
    
    def test_update_caracteres_peligrosos_raises_error(self):
        """Caracteres peligrosos fallan"""
        with pytest.raises(ValidationError):
            CategoriaUpdateRequest(nombre="<img src=x>")


class TestCategoriaResponse:
    """Tests para CategoriaResponse"""
    
    def test_response_valid(self):
        """Respuesta válida"""
        now = datetime.utcnow()
        resp = CategoriaResponse(
            id=1,
            nombre="Bebidas",
            descripcion="Test",
            is_active=True,
            created_at=now,
            updated_at=now
        )
        assert resp.id == 1
        assert resp.nombre == "Bebidas"
        assert resp.is_active is True
    
    def test_response_desde_dict(self):
        """Crear respuesta desde diccionario"""
        now = datetime.utcnow()
        data = {
            "id": 1,
            "nombre": "Bebidas",
            "descripcion": "Test",
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
        resp = CategoriaResponse(**data)
        assert resp.id == 1


class TestCategoriaListResponse:
    """Tests para CategoriaListResponse"""
    
    def test_list_response_valid(self):
        """Respuesta de listado válida"""
        now = datetime.utcnow()
        items = [
            CategoriaResponse(
                id=1,
                nombre="Cat1",
                descripcion="",
                is_active=True,
                created_at=now,
                updated_at=now
            ),
            CategoriaResponse(
                id=2,
                nombre="Cat2",
                descripcion="",
                is_active=True,
                created_at=now,
                updated_at=now
            ),
        ]
        
        resp = CategoriaListResponse(
            items=items,
            total=2,
            skip=0,
            limit=20
        )
        
        assert len(resp.items) == 2
        assert resp.total == 2
        assert resp.skip == 0
        assert resp.limit == 20
    
    def test_list_response_vacia(self):
        """Listado vacío"""
        resp = CategoriaListResponse(
            items=[],
            total=0,
            skip=0,
            limit=20
        )
        assert len(resp.items) == 0
        assert resp.total == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
