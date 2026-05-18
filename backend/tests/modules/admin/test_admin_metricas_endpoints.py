"""
Tests de integración para endpoints de métricas del admin.

Verifica:
- HTTP 200 con datos válidos (ADMIN autenticado)
- HTTP 422 granularidad/rango inválido
- HTTP 403 para no-ADMIN
- HTTP 401 sin token
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.security import TokenService


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def admin_headers():
    # user_id 9999 no existe en el sistema in-memory (solo queries de lectura para métricas)
    token = TokenService.create_access_token(user_id=9999, email="admin@test.com", role="ADMIN")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client_headers():
    token = TokenService.create_access_token(user_id=2, email="client@test.com", role="customer")
    return {"Authorization": f"Bearer {token}"}


class TestMetricasResumen:
    """Tests para GET /api/v1/admin/metricas/resumen"""

    def test_admin_obtiene_resumen(self, client, admin_headers):
        response = client.get("/api/v1/admin/metricas/resumen", headers=admin_headers)
        assert response.status_code == 200
        data = response.json()
        assert "ventas_totales" in data
        assert "cantidad_pedidos" in data
        assert "cantidad_usuarios" in data
        assert "productos_sin_stock" in data

    def test_sin_token_retorna_401(self, client):
        response = client.get("/api/v1/admin/metricas/resumen")
        assert response.status_code == 401

    def test_no_admin_retorna_403(self, client, client_headers):
        response = client.get("/api/v1/admin/metricas/resumen", headers=client_headers)
        assert response.status_code == 403


class TestMetricasVentas:
    """Tests para GET /api/v1/admin/metricas/ventas"""

    def test_admin_obtiene_serie(self, client, admin_headers):
        response = client.get(
            "/api/v1/admin/metricas/ventas?granularidad=dia",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_granularidad_invalida(self, client, admin_headers):
        response = client.get(
            "/api/v1/admin/metricas/ventas?granularidad=hora",
            headers=admin_headers
        )
        assert response.status_code == 422

    def test_rango_invertido(self, client, admin_headers):
        response = client.get(
            "/api/v1/admin/metricas/ventas?desde=2026-02-01&hasta=2026-01-01&granularidad=dia",
            headers=admin_headers
        )
        assert response.status_code == 422

    def test_no_admin_retorna_403(self, client, client_headers):
        response = client.get("/api/v1/admin/metricas/ventas", headers=client_headers)
        assert response.status_code == 403

    def test_sin_token_retorna_401(self, client):
        response = client.get("/api/v1/admin/metricas/ventas")
        assert response.status_code == 401


class TestMetricasProductosTop:
    """Tests para GET /api/v1/admin/metricas/productos-top"""

    def test_admin_obtiene_top(self, client, admin_headers):
        response = client.get(
            "/api/v1/admin/metricas/productos-top?top=5",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_no_admin_retorna_403(self, client, client_headers):
        response = client.get("/api/v1/admin/metricas/productos-top", headers=client_headers)
        assert response.status_code == 403


class TestMetricasPedidosEstado:
    """Tests para GET /api/v1/admin/metricas/pedidos-por-estado"""

    def test_admin_obtiene_distribucion(self, client, admin_headers):
        response = client.get(
            "/api/v1/admin/metricas/pedidos-por-estado",
            headers=admin_headers
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_no_admin_retorna_403(self, client, client_headers):
        response = client.get(
            "/api/v1/admin/metricas/pedidos-por-estado",
            headers=client_headers
        )
        assert response.status_code == 403

    def test_sin_token_retorna_401(self, client):
        response = client.get("/api/v1/admin/metricas/pedidos-por-estado")
        assert response.status_code == 401
