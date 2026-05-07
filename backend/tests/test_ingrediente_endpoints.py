"""
Tests de integración para endpoints de Ingredientes.

Verifica que los endpoints REST funcionen correctamente con UoW real.
Mapeo de excepciones a HTTP status codes.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """Fixture: TestClient para FastAPI"""
    return TestClient(app)


@pytest.fixture
def admin_headers():
    """Fixture: Headers con token admin"""
    return {"Authorization": "Bearer admin-token"}


class TestCreateIngredienteEndpoint:
    """Tests para POST /ingredientes"""
    
    def test_post_ingredientes_valid(self, client, admin_headers):
        """✓ POST /ingredientes válido → 201"""
        response = client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "gramos",
                "cantidad_stock": 100,
                "cantidad_minima": 10,
                "descripcion": "Harina blanca"
            },
            headers=admin_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == "Harina"
        assert data["unidad_medida"] == "gramos"
    
    def test_post_ingredientes_duplicate(self, client, admin_headers):
        """✓ POST /ingredientes nombre duplicado → 409"""
        # Crear primero
        client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "gramos",
                "cantidad_stock": 100,
                "cantidad_minima": 10
            },
            headers=admin_headers
        )
        
        # Intenta crear duplicado
        response = client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "litros",
                "cantidad_stock": 50,
                "cantidad_minima": 5
            },
            headers=admin_headers
        )
        
        assert response.status_code == 409
    
    def test_post_ingredientes_invalid_unidad(self, client, admin_headers):
        """✓ POST /ingredientes unidad inválida → 400"""
        response = client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "toneladas",
                "cantidad_stock": 100,
                "cantidad_minima": 10
            },
            headers=admin_headers
        )
        
        assert response.status_code == 400
    
    def test_post_ingredientes_negative_stock(self, client, admin_headers):
        """✓ POST /ingredientes stock negativo → 400"""
        response = client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "gramos",
                "cantidad_stock": -50,
                "cantidad_minima": 10
            },
            headers=admin_headers
        )
        
        assert response.status_code == 400


class TestListIngredientesEndpoint:
    """Tests para GET /ingredientes"""
    
    def test_get_ingredientes_list(self, client):
        """✓ GET /ingredientes → 200"""
        response = client.get("/ingredientes")
        
        assert response.status_code == 200
        data = response.json()
        assert "ingredientes" in data or "items" in data
    
    def test_get_ingredientes_with_filters(self, client, admin_headers):
        """✓ GET /ingredientes con filtros (unidad_medida, categoria_id)"""
        # Crear un ingrediente
        client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "gramos",
                "cantidad_stock": 100,
                "cantidad_minima": 10
            },
            headers=admin_headers
        )
        
        # Filtrar por unidad
        response = client.get("/ingredientes?unidad_medida=gramos")
        
        assert response.status_code == 200


class TestBuscarIngredientesEndpoint:
    """Tests para GET /ingredientes/buscar"""
    
    def test_buscar_ingredientes_valid(self, client, admin_headers):
        """✓ GET /ingredientes/buscar?q=termo → 200"""
        # Crear
        client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "gramos",
                "cantidad_stock": 100,
                "cantidad_minima": 10
            },
            headers=admin_headers
        )
        
        # Buscar
        response = client.get("/ingredientes/buscar?q=Har")
        
        assert response.status_code == 200


class TestGetIngredienteEndpoint:
    """Tests para GET /ingredientes/{id}"""
    
    def test_get_ingrediente_valid(self, client, admin_headers):
        """✓ GET /ingredientes/{id} válido → 200"""
        # Crear
        create_resp = client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "gramos",
                "cantidad_stock": 100,
                "cantidad_minima": 10
            },
            headers=admin_headers
        )
        ing_id = create_resp.json()["id"]
        
        # Obtener
        response = client.get(f"/ingredientes/{ing_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == ing_id
    
    def test_get_ingrediente_not_found(self, client):
        """✓ GET /ingredientes/{id} no existe → 404"""
        response = client.get("/ingredientes/9999")
        
        assert response.status_code == 404


class TestUpdateIngredienteEndpoint:
    """Tests para PUT /ingredientes/{id}"""
    
    def test_put_ingrediente_valid(self, client, admin_headers):
        """✓ PUT /ingredientes/{id} válido → 200"""
        # Crear
        create_resp = client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "gramos",
                "cantidad_stock": 100,
                "cantidad_minima": 10
            },
            headers=admin_headers
        )
        ing_id = create_resp.json()["id"]
        
        # Actualizar
        response = client.put(
            f"/ingredientes/{ing_id}",
            json={"cantidad_stock": 200},
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["cantidad_stock"] == 200
    
    def test_put_ingrediente_not_found(self, client, admin_headers):
        """✓ PUT /ingredientes/{id} no existe → 404"""
        response = client.put(
            "/ingredientes/9999",
            json={"cantidad_stock": 200},
            headers=admin_headers
        )
        
        assert response.status_code == 404


class TestDeleteIngredienteEndpoint:
    """Tests para DELETE /ingredientes/{id}"""
    
    def test_delete_ingrediente_valid(self, client, admin_headers):
        """✓ DELETE /ingredientes/{id} → 204"""
        # Crear
        create_resp = client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "gramos",
                "cantidad_stock": 100,
                "cantidad_minima": 10
            },
            headers=admin_headers
        )
        ing_id = create_resp.json()["id"]
        
        # Eliminar
        response = client.delete(
            f"/ingredientes/{ing_id}",
            headers=admin_headers
        )
        
        assert response.status_code == 204
    
    def test_delete_ingrediente_not_found(self, client, admin_headers):
        """✓ DELETE /ingredientes/{id} no existe → 404"""
        response = client.delete(
            "/ingredientes/9999",
            headers=admin_headers
        )
        
        assert response.status_code == 404


class TestHistorialStockEndpoint:
    """Tests para GET /ingredientes/{id}/historial-stock"""
    
    def test_get_historial_stock_valid(self, client, admin_headers):
        """✓ GET /ingredientes/{id}/historial-stock → 200"""
        # Crear
        create_resp = client.post(
            "/ingredientes",
            json={
                "nombre": "Harina",
                "unidad_medida": "gramos",
                "cantidad_stock": 100,
                "cantidad_minima": 10
            },
            headers=admin_headers
        )
        ing_id = create_resp.json()["id"]
        
        # Obtener historial
        response = client.get(
            f"/ingredientes/{ing_id}/historial-stock",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "historial" in data
    
    def test_get_historial_stock_not_found(self, client, admin_headers):
        """✓ GET /ingredientes/{id}/historial-stock no existe → 404"""
        response = client.get(
            "/ingredientes/9999/historial-stock",
            headers=admin_headers
        )
        
        assert response.status_code == 404
