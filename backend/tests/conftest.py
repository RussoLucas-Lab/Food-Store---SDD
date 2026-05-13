"""
Pytest fixtures para testing de clientes.

Proporciona:
- Mock UoW y repos
- Cliente instances para testing
- Fixtures de usuarios con roles variados (ADMIN, USER, GUEST)
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from models.cliente import Cliente


@pytest.fixture
def mock_uow():
    """Mock Unit of Work con repositorios"""
    uow = Mock()
    uow.clientes = Mock()
    uow.commit = Mock()
    uow.rollback = Mock()
    return uow


@pytest.fixture
def cliente_fixture():
    """Cliente instance para testing"""
    return Cliente(
        id=1,
        nombre="Test Cliente",
        email="test@example.com",
        telefono="+54 11 1234 5678",
        direccion="Test Address 123",
        activo=True,
        user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def inactive_cliente_fixture():
    """Cliente inactivo para testing soft-delete"""
    return Cliente(
        id=2,
        nombre="Inactive Cliente",
        email="inactive@example.com",
        telefono="+54 11 9876 5432",
        direccion="Inactive Address 456",
        activo=False,
        user_id=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )


@pytest.fixture
def admin_user_fixture():
    """Usuario ADMIN para testing RBAC"""
    return {
        "id": "admin-1",
        "email": "admin@foodstore.local",
        "nombre": "Admin User",
        "role": "ADMIN"
    }


@pytest.fixture
def regular_user_fixture():
    """Usuario regular (USER) para testing RBAC"""
    return {
        "id": "user-1",
        "email": "user@foodstore.local",
        "nombre": "Regular User",
        "role": "USER"
    }


@pytest.fixture
def guest_user_fixture():
    """Usuario anónimo (GUEST) para testing"""
    return {
        "id": None,
        "email": None,
        "nombre": "Guest",
        "role": "GUEST"
    }


@pytest.fixture
def multiple_clientes_fixture():
    """Lista de clientes para testing list operations"""
    return [
        Cliente(
            id=1,
            nombre="Cliente Uno",
            email="cliente1@example.com",
            telefono="+54 11 1111 1111",
            direccion="Address 1",
            activo=True,
        ),
        Cliente(
            id=2,
            nombre="Cliente Dos",
            email="cliente2@example.com",
            telefono="+54 11 2222 2222",
            direccion="Address 2",
            activo=True,
        ),
        Cliente(
            id=3,
            nombre="Cliente Tres",
            email="cliente3@example.com",
            telefono="+54 11 3333 3333",
            direccion="Address 3",
            activo=False,  # Inactivo
        ),
    ]


@pytest.fixture
def valid_cliente_create_data():
    """Datos válidos para crear cliente"""
    return {
        "nombre": "New Cliente",
        "email": "newcliente@example.com",
        "telefono": "+54 11 5555 5555",
        "direccion": "New Address 789",
    }


@pytest.fixture
def invalid_cliente_create_data():
    """Datos inválidos para testing validación"""
    return [
        # Email inválido
        {
            "nombre": "Test",
            "email": "invalid-email",
            "telefono": "+54 11 1234 5678",
            "direccion": "Test Address",
        },
        # Nombre vacío
        {
            "nombre": "",
            "email": "test@example.com",
            "telefono": "+54 11 1234 5678",
            "direccion": "Test Address",
        },
        # Teléfono inválido (muy corto)
        {
            "nombre": "Test",
            "email": "test@example.com",
            "telefono": "123",
            "direccion": "Test Address",
        },
        # Dirección vacía
        {
            "nombre": "Test",
            "email": "test@example.com",
            "telefono": "+54 11 1234 5678",
            "direccion": "",
        },
    ]


@pytest.fixture
def rbac_test_scenarios():
    """Escenarios de testing para RBAC (Role-Based Access Control)"""
    return {
        "admin_can_create": {
            "role": "ADMIN",
            "action": "create",
            "expected": "allowed",
        },
        "user_cannot_create": {
            "role": "USER",
            "action": "create",
            "expected": "denied",
        },
        "admin_can_view_all": {
            "role": "ADMIN",
            "action": "list_all",
            "expected": "allowed",
        },
        "user_can_view_own_only": {
            "role": "USER",
            "action": "list",
            "expected": "allowed_own_only",
        },
        "user_can_edit_own": {
            "role": "USER",
            "action": "edit",
            "target": "own",
            "expected": "allowed",
        },
        "user_cannot_edit_other": {
            "role": "USER",
            "action": "edit",
            "target": "other",
            "expected": "denied",
        },
        "admin_can_delete": {
            "role": "ADMIN",
            "action": "delete",
            "expected": "allowed",
        },
        "user_cannot_delete": {
            "role": "USER",
            "action": "delete",
            "expected": "denied",
        },
    }
