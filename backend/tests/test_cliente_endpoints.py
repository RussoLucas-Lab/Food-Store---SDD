"""
Tests de integración para endpoints de Cliente.

Prueba los endpoints HTTP completos: validación, auth, mappeo de errores a HTTP.

Coverage target: > 90%
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from backend.main import app
from backend.schemas.cliente_schema import ClienteResponse
from datetime import datetime


@pytest.fixture
def client():
    """Fixture: TestClient para FastAPI"""
    return TestClient(app)


@pytest.fixture
def mock_admin_token():
    """Token JWT simulado para ADMIN"""
    return "Bearer mock-admin-token"


@pytest.fixture
def mock_user_token():
    """Token JWT simulado para USER"""
    return "Bearer mock-user-token"


@pytest.fixture
def sample_cliente():
    """Datos de cliente de prueba"""
    return {
        "id": 1,
        "nombre": "Juan Pérez",
        "email": "juan@example.com",
        "telefono": "555-1234",
        "direccion": "Calle 123, Apt 4",
        "activo": True,
        "user_id": None,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }


class TestCreateCliente:
    """Tests para POST /clientes"""
    
    def test_create_cliente_admin_success(self, client, mock_admin_token, sample_cliente):
        """✓ ADMIN crea cliente exitosamente → 201"""
        with patch("backend.routers.clientes.cliente_service.create_cliente") as mock_create:
            mock_create.return_value = sample_cliente
            
            response = client.post(
                "/clientes",
                json={
                    "nombre": "Juan Pérez",
                    "email": "juan@example.com",
                    "telefono": "555-1234",
                    "direccion": "Calle 123, Apt 4"
                },
                headers={"Authorization": mock_admin_token}
            )
            
            assert response.status_code == 201
            assert response.json()["email"] == "juan@example.com"
    
    def test_create_cliente_duplicate_email(self, client, mock_admin_token):
        """❌ Email duplicado → 409"""
        with patch("backend.routers.clientes.cliente_service.create_cliente") as mock_create:
            mock_create.side_effect = ValueError("Email 'juan@example.com' ya está registrado")
            
            response = client.post(
                "/clientes",
                json={
                    "nombre": "Juan Pérez",
                    "email": "juan@example.com",
                    "telefono": "555-1234",
                    "direccion": "Calle 123, Apt 4"
                },
                headers={"Authorization": mock_admin_token}
            )
            
            assert response.status_code == 409
    
    def test_create_cliente_invalid_email(self, client, mock_admin_token):
        """❌ Email inválido → 400"""
        response = client.post(
            "/clientes",
            json={
                "nombre": "Juan Pérez",
                "email": "not-an-email",  # Pydantic lo rechaza
                "telefono": "555-1234",
                "direccion": "Calle 123, Apt 4"
            },
            headers={"Authorization": mock_admin_token}
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_cliente_user_forbidden(self, client, mock_user_token):
        """❌ USER intenta crear → 403"""
        with patch("backend.routers.clientes.cliente_service.create_cliente") as mock_create:
            mock_create.side_effect = PermissionError("Solo ADMIN puede crear clientes")
            
            response = client.post(
                "/clientes",
                json={
                    "nombre": "Juan Pérez",
                    "email": "juan@example.com",
                    "telefono": "555-1234",
                    "direccion": "Calle 123, Apt 4"
                },
                headers={"Authorization": mock_user_token}
            )
            
            assert response.status_code == 403


class TestGetClienteList:
    """Tests para GET /clientes"""
    
    def test_list_clientes_admin(self, client, mock_admin_token, sample_cliente):
        """✓ ADMIN obtiene lista completa → 200"""
        with patch("backend.routers.clientes.cliente_service.list_clientes") as mock_list:
            mock_list.return_value = [sample_cliente]
            with patch("backend.routers.clientes.uow.clientes.find_all") as mock_find_all:
                mock_find_all.return_value = [Mock()]
                
                response = client.get(
                    "/clientes",
                    headers={"Authorization": mock_admin_token}
                )
                
                assert response.status_code == 200
                assert "items" in response.json()
    
    def test_list_clientes_pagination(self, client, mock_admin_token, sample_cliente):
        """✓ Paginación funciona → 200 con skip/limit"""
        with patch("backend.routers.clientes.cliente_service.list_clientes") as mock_list:
            mock_list.return_value = [sample_cliente]
            with patch("backend.routers.clientes.uow.clientes.find_all") as mock_find_all:
                mock_find_all.return_value = [Mock()]
                
                response = client.get(
                    "/clientes?skip=0&limit=10",
                    headers={"Authorization": mock_admin_token}
                )
                
                assert response.status_code == 200
                mock_list.assert_called_once()


class TestGetCliente:
    """Tests para GET /clientes/{id}"""
    
    def test_get_cliente_admin(self, client, mock_admin_token, sample_cliente):
        """✓ ADMIN obtiene cliente → 200"""
        with patch("backend.routers.clientes.cliente_service.get_cliente") as mock_get:
            mock_get.return_value = sample_cliente
            
            response = client.get(
                "/clientes/1",
                headers={"Authorization": mock_admin_token}
            )
            
            assert response.status_code == 200
            assert response.json()["id"] == 1
    
    def test_get_cliente_user_own(self, client, mock_user_token, sample_cliente):
        """✓ USER obtiene su propio cliente → 200"""
        with patch("backend.routers.clientes.cliente_service.get_cliente") as mock_get:
            mock_get.return_value = sample_cliente
            
            response = client.get(
                "/clientes/1",
                headers={"Authorization": mock_user_token}
            )
            
            assert response.status_code == 200
    
    def test_get_cliente_not_found(self, client, mock_admin_token):
        """❌ Cliente no existe → 404"""
        with patch("backend.routers.clientes.cliente_service.get_cliente") as mock_get:
            mock_get.side_effect = ValueError("Cliente 999 no existe")
            
            response = client.get(
                "/clientes/999",
                headers={"Authorization": mock_admin_token}
            )
            
            assert response.status_code == 404


class TestUpdateCliente:
    """Tests para PATCH /clientes/{id}"""
    
    def test_update_cliente_admin(self, client, mock_admin_token, sample_cliente):
        """✓ ADMIN actualiza cliente → 200"""
        updated = sample_cliente.copy()
        updated["nombre"] = "Juan Updated"
        
        with patch("backend.routers.clientes.cliente_service.update_cliente") as mock_update:
            mock_update.return_value = updated
            
            response = client.patch(
                "/clientes/1",
                json={"nombre": "Juan Updated"},
                headers={"Authorization": mock_admin_token}
            )
            
            assert response.status_code == 200
            assert response.json()["nombre"] == "Juan Updated"
    
    def test_update_cliente_duplicate_email(self, client, mock_admin_token):
        """❌ Email duplicado → 409"""
        with patch("backend.routers.clientes.cliente_service.update_cliente") as mock_update:
            mock_update.side_effect = ValueError("Email 'taken@example.com' ya está registrado")
            
            response = client.patch(
                "/clientes/1",
                json={"email": "taken@example.com"},
                headers={"Authorization": mock_admin_token}
            )
            
            assert response.status_code == 409


class TestDeleteCliente:
    """Tests para DELETE /clientes/{id}"""
    
    def test_delete_cliente_admin(self, client, mock_admin_token):
        """✓ ADMIN soft-deleta cliente → 204"""
        with patch("backend.routers.clientes.cliente_service.soft_delete_cliente") as mock_delete:
            mock_delete.return_value = {"id": 1, "status": "inactivo"}
            
            response = client.delete(
                "/clientes/1",
                headers={"Authorization": mock_admin_token}
            )
            
            assert response.status_code == 204
    
    def test_delete_cliente_user_forbidden(self, client, mock_user_token):
        """❌ USER intenta eliminar → 403"""
        with patch("backend.routers.clientes.cliente_service.soft_delete_cliente") as mock_delete:
            mock_delete.side_effect = PermissionError("Solo ADMIN puede eliminar clientes")
            
            response = client.delete(
                "/clientes/1",
                headers={"Authorization": mock_user_token}
            )
            
            assert response.status_code == 403


class TestSearchClientes:
    """Tests para GET /clientes/search"""
    
    def test_search_clientes_admin(self, client, mock_admin_token, sample_cliente):
        """✓ ADMIN busca clientes → 200"""
        with patch("backend.routers.clientes.cliente_service.search_clientes") as mock_search:
            mock_search.return_value = [sample_cliente]
            
            response = client.get(
                "/clientes/search?q=Juan",
                headers={"Authorization": mock_admin_token}
            )
            
            assert response.status_code == 200
            assert len(response.json()["items"]) == 1
    
    def test_search_clientes_user_forbidden(self, client, mock_user_token):
        """❌ USER intenta buscar → 403"""
        with patch("backend.routers.clientes.cliente_service.search_clientes") as mock_search:
            mock_search.side_effect = PermissionError("Solo ADMIN puede buscar clientes")
            
            response = client.get(
                "/clientes/search?q=Juan",
                headers={"Authorization": mock_user_token}
            )
            
            assert response.status_code == 403
    
    def test_search_clientes_empty_query(self, client, mock_admin_token):
        """❌ Búsqueda vacía → 400"""
        response = client.get(
            "/clientes/search",
            headers={"Authorization": mock_admin_token}
        )
        
        assert response.status_code == 422  # Validation error (q is required)


class TestReactivateCliente:
    """Tests para PATCH /clientes/{id}/reactivar"""
    
    def test_reactivate_cliente_admin(self, client, mock_admin_token, sample_cliente):
        """✓ ADMIN reactiva cliente → 200"""
        with patch("backend.routers.clientes.cliente_service.reactivate_cliente") as mock_reactivate:
            mock_reactivate.return_value = sample_cliente
            
            response = client.patch(
                "/clientes/1/reactivar",
                headers={"Authorization": mock_admin_token}
            )
            
            assert response.status_code == 200
            assert response.json()["activo"] == True
    
    def test_reactivate_cliente_user_forbidden(self, client, mock_user_token):
        """❌ USER intenta reactivar → 403"""
        with patch("backend.routers.clientes.cliente_service.reactivate_cliente") as mock_reactivate:
            mock_reactivate.side_effect = PermissionError("Solo ADMIN puede reactivar clientes")
            
            response = client.patch(
                "/clientes/1/reactivar",
                headers={"Authorization": mock_user_token}
            )
            
            assert response.status_code == 403
