"""
Unit tests para IngredienteSchema.

Migrado desde tests/test_ingrediente_schema.py.
Prueba validaciones Pydantic para ingredientes.
"""

import pytest
from pydantic import ValidationError
from backend.modules.ingredientes.schemas import (
    IngredienteCreateRequest,
    IngredienteUpdateRequest,
    UnidadMedidaEnum,
    IngredienteResponse
)


class TestIngredienteCreateRequest:
    """Tests para IngredienteCreateRequest"""

    def test_create_valid(self):
        """Crear request válido"""
        req = IngredienteCreateRequest(
            nombre="Sal",
            unidad_medida=UnidadMedidaEnum.GRAMOS,
            cantidad_stock=1000,
            cantidad_minima=100,
            descripcion="Sal de mesa"
        )

        assert req.nombre == "Sal"
        assert req.unidad_medida == "gramos"
        assert req.cantidad_stock == 1000
        assert req.cantidad_minima == 100

    def test_create_minimal(self):
        """Crear request con valores mínimos"""
        req = IngredienteCreateRequest(
            nombre="Azúcar",
            unidad_medida=UnidadMedidaEnum.KILOS,
            cantidad_stock=0,
            cantidad_minima=0
        )

        assert req.nombre == "Azúcar"
        assert req.descripcion is None
        assert req.categoria_id is None

    def test_create_nombre_vacío_raises_error(self):
        """Nombre vacío lanza ValidationError"""
        with pytest.raises(ValidationError):
            IngredienteCreateRequest(
                nombre="",
                unidad_medida=UnidadMedidaEnum.LITROS,
                cantidad_stock=100,
                cantidad_minima=10
            )

    def test_create_nombre_muy_largo_raises_error(self):
        """Nombre mayor a 100 caracteres lanza error"""
        largo_nombre = "a" * 101
        with pytest.raises(ValidationError):
            IngredienteCreateRequest(
                nombre=largo_nombre,
                unidad_medida=UnidadMedidaEnum.GRAMOS,
                cantidad_stock=100,
                cantidad_minima=10
            )

    def test_create_descripcion_muy_larga_raises_error(self):
        """Descripción mayor a 500 caracteres lanza error"""
        larga_desc = "a" * 501
        with pytest.raises(ValidationError):
            IngredienteCreateRequest(
                nombre="Test",
                unidad_medida=UnidadMedidaEnum.GRAMOS,
                cantidad_stock=100,
                cantidad_minima=10,
                descripcion=larga_desc
            )

    def test_create_stock_negativo_raises_error(self):
        """Stock negativo lanza error"""
        with pytest.raises(ValidationError):
            IngredienteCreateRequest(
                nombre="Test",
                unidad_medida=UnidadMedidaEnum.GRAMOS,
                cantidad_stock=-100,
                cantidad_minima=10
            )

    def test_create_unidad_invalida_raises_error(self):
        """Unidad de medida inválida lanza error"""
        with pytest.raises(ValidationError):
            IngredienteCreateRequest(
                nombre="Test",
                unidad_medida="toneladas",  # type: ignore
                cantidad_stock=100,
                cantidad_minima=10
            )

    def test_create_nombre_con_caracteres_peligrosos_raises_error(self):
        """Nombre con caracteres peligrosos lanza error"""
        with pytest.raises(ValidationError):
            IngredienteCreateRequest(
                nombre="<script>alert('xss')</script>",
                unidad_medida=UnidadMedidaEnum.GRAMOS,
                cantidad_stock=100,
                cantidad_minima=10
            )

    def test_create_nombre_sanitizado(self):
        """Nombre se sanitiza (whitespace removido)"""
        req = IngredienteCreateRequest(
            nombre="  Sal  ",
            unidad_medida=UnidadMedidaEnum.GRAMOS,
            cantidad_stock=100,
            cantidad_minima=10
        )

        assert req.nombre == "Sal"

    def test_create_all_unidades(self):
        """Crear con cada unidad de medida válida"""
        for unidad in UnidadMedidaEnum:
            req = IngredienteCreateRequest(
                nombre=f"Ingrediente {unidad.value}",
                unidad_medida=unidad,
                cantidad_stock=100,
                cantidad_minima=10
            )
            assert req.unidad_medida == unidad.value


class TestIngredienteUpdateRequest:
    """Tests para IngredienteUpdateRequest"""

    def test_update_all_fields(self):
        """Actualizar todos los campos"""
        req = IngredienteUpdateRequest(
            nombre="Nuevo Nombre",
            descripcion="Nueva descripción",
            cantidad_stock=500,
            cantidad_minima=50
        )

        assert req.nombre == "Nuevo Nombre"
        assert req.cantidad_stock == 500

    def test_update_no_fields(self):
        """Update sin campos es válido"""
        req = IngredienteUpdateRequest()

        assert req.nombre is None
        assert req.cantidad_stock is None

    def test_update_nombre_vacío_raises_error(self):
        """Nombre vacío lanza error"""
        with pytest.raises(ValidationError):
            IngredienteUpdateRequest(nombre="")

    def test_update_stock_negativo_raises_error(self):
        """Stock negativo lanza error"""
        with pytest.raises(ValidationError):
            IngredienteUpdateRequest(cantidad_stock=-10)

    def test_update_minima_negativa_raises_error(self):
        """Cantidad mínima negativa lanza error"""
        with pytest.raises(ValidationError):
            IngredienteUpdateRequest(cantidad_minima=-5)


class TestIngredienteResponse:
    """Tests para IngredienteResponse"""

    def test_response_valid(self):
        """Response válida se construye correctamente"""
        from datetime import datetime

        resp = IngredienteResponse(
            id=1,
            nombre="Sal",
            descripcion="Sal de mesa",
            unidad_medida="gramos",
            cantidad_stock=1000,
            cantidad_minima=100,
            cantidad_reservada=100,
            stock_disponible=900,
            alerta_stock_bajo=False,
            categoria_id=1,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            deleted_at=None
        )

        assert resp.id == 1
        assert resp.nombre == "Sal"
        assert resp.stock_disponible == 900
