"""
Fixtures de infraestructura para tests de integración.

Los tests de integración de este proyecto usan TestClient(app) con el UoW
en memoria (in-memory). No requieren SQLite ni base de datos real.
El UoW es reseteado automáticamente por el autouse fixture 'reset_all_repos'
definido en backend/tests/conftest.py.

Tasks 4.2-4.6 no aplican (no hay SQLite/SQLModel) — el in-memory UoW
ya proporciona el aislamiento equivalente.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.core.security import TokenService


@pytest.fixture
def client():
    """Cliente HTTP para tests de integración."""
    return TestClient(app)


@pytest.fixture
def admin_headers():
    """Headers de autenticación para usuario ADMIN."""
    token = TokenService.create_access_token(
        user_id=1,
        email="admin@foodstore.com",
        role="ADMIN"
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client_headers():
    """Headers de autenticación para usuario CLIENT."""
    token = TokenService.create_access_token(
        user_id=2,
        email="cliente@foodstore.com",
        role="CLIENT"
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def pedidos_headers():
    """Headers de autenticación para usuario PEDIDOS."""
    token = TokenService.create_access_token(
        user_id=3,
        email="pedidos@foodstore.com",
        role="PEDIDOS"
    )
    return {"Authorization": f"Bearer {token}"}
