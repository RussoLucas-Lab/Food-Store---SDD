"""
Tests unitarios para ClienteService.

Migrado desde backend/tests/test_cliente_service.py.
Prueba toda la lógica de negocio sin dependencias de FastAPI.
Usa mocks del UoW y repositorios para aislar la lógica.
"""

import pytest
from unittest.mock import Mock, MagicMock
from backend.modules.clientes.service import ClienteService
from datetime import datetime


@pytest.fixture
def mock_uow():
    """Fixture: Mock Unit of Work con repositorios"""
    uow = Mock()
    uow.clientes = Mock()
    uow.commit = Mock()
    return uow


@pytest.fixture
def service(mock_uow):
    """Fixture: ClienteService con mock UoW"""
    return ClienteService(mock_uow)


class TestCreateCliente:
    """Tests para ClienteService.create_cliente()"""

    def test_create_cliente_valid_admin(self, service, mock_uow):
        """ADMIN crea cliente con datos válidos"""
        mock_cliente = Mock()
        mock_cliente.to_dict.return_value = {
            "id": 1,
            "nombre": "Juan Pérez",
            "email": "juan@example.com",
            "telefono": "555-1234",
            "direccion": "Calle 123, Apt 4",
            "activo": True,
            "user_id": None,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        mock_uow.clientes.find_by_email.return_value = None
        mock_uow.clientes.create.return_value = mock_cliente

        result = service.create_cliente(
            nombre="Juan Pérez",
            email="juan@example.com",
            direccion="Calle 123, Apt 4",
            telefono="555-1234",
            requesting_user_role="ADMIN"
        )

        assert result["nombre"] == "Juan Pérez"
        assert result["email"] == "juan@example.com"
        assert result["activo"] is True
        mock_uow.clientes.create.assert_called_once()
        mock_uow.commit.assert_called_once()

    def test_create_cliente_user_forbidden(self, service, mock_uow):
        """USER intenta crear cliente → PermissionError"""
        with pytest.raises(PermissionError, match="Solo ADMIN"):
            service.create_cliente(
                nombre="Juan",
                email="juan@example.com",
                direccion="Calle 123",
                requesting_user_role="USER"
            )

    def test_create_cliente_email_required(self, service, mock_uow):
        """Email vacío → ValueError"""
        with pytest.raises(ValueError, match="Email es requerido"):
            service.create_cliente(
                nombre="Juan",
                email="",
                direccion="Calle 123",
                requesting_user_role="ADMIN"
            )

    def test_create_cliente_invalid_email_format(self, service, mock_uow):
        """Email inválido → ValueError"""
        with pytest.raises(ValueError, match="Formato de email inválido"):
            service.create_cliente(
                nombre="Juan",
                email="not-an-email",
                direccion="Calle 123",
                requesting_user_role="ADMIN"
            )

    def test_create_cliente_duplicate_email(self, service, mock_uow):
        """Email duplicado → ValueError"""
        mock_existing = Mock()
        mock_uow.clientes.find_by_email.return_value = mock_existing

        with pytest.raises(ValueError, match="ya está registrado"):
            service.create_cliente(
                nombre="Juan",
                email="existing@example.com",
                direccion="Calle 123",
                requesting_user_role="ADMIN"
            )

    def test_create_cliente_nombre_required(self, service, mock_uow):
        """Nombre vacío → ValueError"""
        with pytest.raises(ValueError, match="Nombre es requerido"):
            service.create_cliente(
                nombre="",
                email="juan@example.com",
                direccion="Calle 123",
                requesting_user_role="ADMIN"
            )

    def test_create_cliente_direccion_required(self, service, mock_uow):
        """Dirección vacía → ValueError"""
        with pytest.raises(ValueError, match="Dirección es requerida"):
            service.create_cliente(
                nombre="Juan",
                email="juan@example.com",
                direccion="",
                requesting_user_role="ADMIN"
            )

    def test_create_cliente_invalid_phone_format(self, service, mock_uow):
        """Teléfono con formato inválido → ValueError"""
        with pytest.raises(ValueError, match="Formato de teléfono inválido"):
            service.create_cliente(
                nombre="Juan",
                email="juan@example.com",
                direccion="Calle 123",
                telefono="xyz",  # Inválido
                requesting_user_role="ADMIN"
            )


class TestGetCliente:
    """Tests para ClienteService.get_cliente()"""

    def test_get_cliente_admin_any_user(self, service, mock_uow):
        """ADMIN obtiene cualquier cliente"""
        mock_cliente = Mock()
        mock_cliente.to_dict.return_value = {"id": 1, "nombre": "Juan"}
        mock_uow.clientes.find_by_id.return_value = mock_cliente

        result = service.get_cliente(
            cliente_id=1,
            requesting_user_id=999,
            requesting_user_role="ADMIN"
        )

        assert result["id"] == 1
        mock_uow.clientes.find_by_id.assert_called_once_with(1)

    def test_get_cliente_user_own_profile(self, service, mock_uow):
        """USER obtiene su propio perfil"""
        mock_cliente = Mock()
        mock_cliente.to_dict.return_value = {"id": 5, "nombre": "Juan"}
        mock_uow.clientes.find_by_id.return_value = mock_cliente

        result = service.get_cliente(
            cliente_id=5,
            requesting_user_id=5,
            requesting_user_role="USER"
        )

        assert result["id"] == 5

    def test_get_cliente_user_forbidden_other(self, service, mock_uow):
        """USER intenta obtener otro cliente → PermissionError"""
        with pytest.raises(PermissionError, match="No tienes permiso"):
            service.get_cliente(
                cliente_id=10,
                requesting_user_id=5,
                requesting_user_role="USER"
            )

    def test_get_cliente_not_found(self, service, mock_uow):
        """Cliente no existe → ValueError"""
        mock_uow.clientes.find_by_id.return_value = None

        with pytest.raises(ValueError, match="no existe"):
            service.get_cliente(
                cliente_id=999,
                requesting_user_role="ADMIN"
            )


class TestUpdateCliente:
    """Tests para ClienteService.update_cliente()"""

    def test_update_cliente_admin_any_user(self, service, mock_uow):
        """ADMIN actualiza cualquier cliente"""
        mock_cliente = Mock()
        mock_cliente.id = 1
        mock_updated = Mock()
        mock_updated.to_dict.return_value = {"id": 1, "nombre": "Juan Updated"}

        mock_uow.clientes.find_by_id.return_value = mock_cliente
        mock_uow.clientes.find_by_email.return_value = None
        mock_uow.clientes.update.return_value = mock_updated

        result = service.update_cliente(
            cliente_id=1,
            nombre="Juan Updated",
            requesting_user_role="ADMIN"
        )

        assert result["nombre"] == "Juan Updated"
        mock_uow.commit.assert_called_once()

    def test_update_cliente_user_own(self, service, mock_uow):
        """USER actualiza su propio perfil"""
        mock_cliente = Mock()
        mock_cliente.id = 5
        mock_updated = Mock()
        mock_updated.to_dict.return_value = {"id": 5, "nombre": "Juan"}

        mock_uow.clientes.find_by_id.return_value = mock_cliente
        mock_uow.clientes.update.return_value = mock_updated

        result = service.update_cliente(
            cliente_id=5,
            nombre="Juan",
            requesting_user_id=5,
            requesting_user_role="USER"
        )

        assert result["id"] == 5

    def test_update_cliente_user_forbidden_other(self, service, mock_uow):
        """USER intenta actualizar otro cliente → PermissionError"""
        with pytest.raises(PermissionError, match="No tienes permiso"):
            service.update_cliente(
                cliente_id=10,
                nombre="Someone else",
                requesting_user_id=5,
                requesting_user_role="USER"
            )

    def test_update_cliente_not_found(self, service, mock_uow):
        """Cliente no existe → ValueError"""
        mock_uow.clientes.find_by_id.return_value = None

        with pytest.raises(ValueError, match="no existe"):
            service.update_cliente(
                cliente_id=999,
                nombre="Juan",
                requesting_user_role="ADMIN"
            )

    def test_update_cliente_duplicate_email(self, service, mock_uow):
        """Email ya usado por otro cliente → ValueError"""
        mock_cliente = Mock()
        mock_cliente.id = 1
        mock_existing = Mock()
        mock_existing.id = 2

        mock_uow.clientes.find_by_id.return_value = mock_cliente
        mock_uow.clientes.find_by_email.return_value = mock_existing

        with pytest.raises(ValueError, match="ya está registrado"):
            service.update_cliente(
                cliente_id=1,
                email="taken@example.com",
                requesting_user_role="ADMIN"
            )


class TestSoftDeleteCliente:
    """Tests para ClienteService.soft_delete_cliente()"""

    def test_soft_delete_admin(self, service, mock_uow):
        """ADMIN soft-deleta cliente"""
        mock_cliente = Mock()
        mock_uow.clientes.find_by_id.return_value = mock_cliente
        mock_uow.clientes.soft_delete.return_value = True

        result = service.soft_delete_cliente(
            cliente_id=1,
            requesting_user_role="ADMIN"
        )

        assert result["status"] == "inactivo"
        mock_uow.commit.assert_called_once()

    def test_soft_delete_user_forbidden(self, service, mock_uow):
        """USER intenta soft-deleta → PermissionError"""
        with pytest.raises(PermissionError, match="Solo ADMIN"):
            service.soft_delete_cliente(
                cliente_id=1,
                requesting_user_role="USER"
            )

    def test_soft_delete_not_found(self, service, mock_uow):
        """Cliente no existe → ValueError"""
        mock_uow.clientes.find_by_id.return_value = None

        with pytest.raises(ValueError, match="no existe"):
            service.soft_delete_cliente(
                cliente_id=999,
                requesting_user_role="ADMIN"
            )


class TestReactivateCliente:
    """Tests para ClienteService.reactivate_cliente()"""

    def test_reactivate_admin(self, service, mock_uow):
        """ADMIN reactiva cliente"""
        mock_cliente = Mock()
        mock_cliente.to_dict.return_value = {"id": 1, "activo": True}
        mock_uow.clientes.reactivate.return_value = mock_cliente

        result = service.reactivate_cliente(
            cliente_id=1,
            requesting_user_role="ADMIN"
        )

        assert result["activo"] is True
        mock_uow.commit.assert_called_once()

    def test_reactivate_user_forbidden(self, service, mock_uow):
        """USER intenta reactivar → PermissionError"""
        with pytest.raises(PermissionError, match="Solo ADMIN"):
            service.reactivate_cliente(
                cliente_id=1,
                requesting_user_role="USER"
            )


class TestSearchClientes:
    """Tests para ClienteService.search_clientes()"""

    def test_search_admin(self, service, mock_uow):
        """ADMIN busca clientes"""
        mock_cliente = Mock()
        mock_cliente.to_dict.return_value = {"id": 1, "nombre": "Juan"}
        mock_uow.clientes.search.return_value = [mock_cliente]

        result = service.search_clientes(
            query="Juan",
            requesting_user_role="ADMIN"
        )

        assert len(result) == 1
        assert result[0]["nombre"] == "Juan"

    def test_search_user_forbidden(self, service, mock_uow):
        """USER intenta buscar → PermissionError"""
        with pytest.raises(PermissionError, match="Solo ADMIN"):
            service.search_clientes(
                query="Juan",
                requesting_user_role="USER"
            )

    def test_search_empty_query(self, service, mock_uow):
        """Búsqueda vacía → ValueError"""
        with pytest.raises(ValueError, match="Consulta de búsqueda requerida"):
            service.search_clientes(
                query="",
                requesting_user_role="ADMIN"
            )
