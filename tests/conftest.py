"""
Pytest configuration and fixtures for testing.
"""

import pytest
import sys
from unittest.mock import MagicMock
from repositories.usuario_repository import InMemoryUsuarioRepository

# Pytest hook: runs BEFORE test collection
def pytest_configure(config):
    """Configure pytest before tests are collected."""
    # Create a mock limiter that acts as a passthrough decorator
    class MockLimiter:
        def limit(self, *args, **kwargs):
            def decorator(f):
                return f
            return decorator
    
    mock_limiter = MockLimiter()
    
    # Monkeypatch the slowapi.Limiter at module level BEFORE importing routers
    import slowapi
    slowapi.Limiter.limit = lambda self, *args, **kwargs: lambda f: f


@pytest.fixture(autouse=True)
def reset_usuario_repo():
    """
    Reset the usuario repository before each test.
    This ensures tests start with a clean state.
    """
    # Clear the in-memory repository
    InMemoryUsuarioRepository._usuarios = {}
    InMemoryUsuarioRepository._id_counter = 1
    yield
    # Clean up after test
    InMemoryUsuarioRepository._usuarios = {}
    InMemoryUsuarioRepository._id_counter = 1


@pytest.fixture(autouse=True)
def reset_token_service():
    """
    Reset the token service's refresh token store before each test.
    """
    from backend.services.token_service import TokenService
    TokenService._refresh_token_store = {}
    yield
    TokenService._refresh_token_store = {}





