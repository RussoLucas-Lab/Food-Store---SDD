"""
Pytest configuration and fixtures for testing.

Consolidado desde:
- tests/conftest.py (original pre-refactor)
- backend/tests/conftest.py (fixtures de clientes)
"""

import pytest
from unittest.mock import Mock
from datetime import datetime

from backend.modules.clientes.model import Cliente


# Pytest hook: runs BEFORE test collection
def pytest_configure(config):
    """Configure pytest before tests are collected."""
    import slowapi
    slowapi.Limiter.limit = lambda self, *args, **kwargs: lambda f: f


def _reset_repo(repo):
    """Reset an in-memory repository to a clean state."""
    repo._storage.clear()
    repo._next_id = 1
    # Clear any name/email index if present
    for attr in ('_name_index', '_email_index'):
        if hasattr(repo, attr):
            getattr(repo, attr).clear()


@pytest.fixture(autouse=True)
def override_get_uow():
    """
    Override FastAPI's get_uow dependency with InMemoryUnitOfWork for all tests.

    This prevents endpoint tests from attempting a real PostgreSQL connection.
    Strategy:
    1. Override app.dependency_overrides on the main app (covers most endpoint tests
       that use `backend.main.app`).
    2. Patch FastAPI.__init__ so that ANY fresh FastAPI() app created inside a test
       fixture (e.g. the `simple_app` fixtures that create standalone apps) also
       gets the dependency override injected at construction time.
    3. Re-attach .uow attribute on router modules for test files that reference
       router_mod.uow directly (backwards-compatible with pre-DI tests).

    A fresh InMemoryUnitOfWork instance is created per test, guaranteeing isolation.
    """
    from fastapi import FastAPI
    from backend.main import app as main_app
    from backend.core.deps import get_uow as original_get_uow
    from backend.core.uow_inmemory import InMemoryUnitOfWork

    import backend.modules.pedidos.router as pedidos_router_mod
    import backend.modules.productos.router as prod_router_mod
    import backend.modules.clientes.router as cli_router_mod

    test_uow = InMemoryUnitOfWork()

    # Function used as override — returns the shared test_uow instance
    def _inmemory_get_uow():
        return test_uow

    # 1. Override on the main app's dependency injection system
    main_app.dependency_overrides[original_get_uow] = _inmemory_get_uow

    # 2. Patch FastAPI.__init__ so any new FastAPI() app created during this test
    #    also gets the override. This handles `simple_app` fixtures that do:
    #        app = FastAPI(); app.include_router(some_router)
    _original_fastapi_init = FastAPI.__init__

    def _patched_fastapi_init(self, *args, **kwargs):
        _original_fastapi_init(self, *args, **kwargs)
        self.dependency_overrides[original_get_uow] = _inmemory_get_uow

    FastAPI.__init__ = _patched_fastapi_init

    # 3. Re-attach .uow on router modules for backwards-compatible test references
    #    (tests that access router_mod.uow directly)
    pedidos_router_mod.uow = test_uow
    prod_router_mod.uow = test_uow
    cli_router_mod.uow = test_uow

    yield test_uow

    # Teardown: restore original FastAPI.__init__ and clean up overrides
    FastAPI.__init__ = _original_fastapi_init
    main_app.dependency_overrides.pop(original_get_uow, None)
    # Remove dynamically-attached uow from router modules
    for mod in (pedidos_router_mod, prod_router_mod, cli_router_mod):
        if 'uow' in mod.__dict__:
            try:
                delattr(mod, 'uow')
            except AttributeError:
                pass


@pytest.fixture(autouse=True)
def reset_token_service():
    """
    Reset the token service's refresh token store before each test.
    """
    from backend.core.security import TokenService
    TokenService._refresh_token_store = {}
    yield
    TokenService._refresh_token_store = {}


# --- Fixtures de Cliente ---

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
