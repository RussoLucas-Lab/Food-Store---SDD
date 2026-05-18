"""
Tests de integración para endpoints de DireccionEntrega.

Prueba los endpoints HTTP completos: autenticación, códigos de respuesta,
mapeo de errores a HTTP (201, 200, 204, 400, 401, 403, 404).

Usa el test_uow provisto por el fixture autouse override_get_uow (conftest.py).
Los datos se pre-populan directamente en el repositorio en memoria en lugar de
usar patch sobre atributos de módulo que ya no existen (post-refactor DI).
Para casos de error de dominio se parchea el método de la clase de servicio.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from datetime import datetime

from backend.main import app
from backend.modules.direcciones.exceptions import DireccionNotFound, UnauthorizedDireccionAccess


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    """FastAPI TestClient."""
    return TestClient(app)


@pytest.fixture
def client_token():
    """JWT con rol 'client' y user_id=1."""
    from backend.core.security import TokenService
    token = TokenService.create_access_token(user_id=1, email="client@test.com", role="client")
    return f"Bearer {token}"


@pytest.fixture
def admin_token():
    """JWT con rol 'admin' y user_id=99."""
    from backend.core.security import TokenService
    token = TokenService.create_access_token(user_id=99, email="admin@test.com", role="admin")
    return f"Bearer {token}"


@pytest.fixture
def create_payload():
    """Body válido para POST /clientes/me/direcciones."""
    return {
        "calle": "Av. Siempreviva",
        "numero": "742",
        "ciudad": "Springfield",
        "provincia": "Buenos Aires",
        "codigo_postal": "1234",
    }


BASE = "/api/v1/clientes/me/direcciones"


# ── POST /clientes/me/direcciones ──────────────────────────────────────────────

class TestCreateDireccion:
    """Tests para POST /clientes/me/direcciones"""

    def test_create_con_client_token_201(self, client, client_token, create_payload):
        """Cliente autenticado crea dirección → 201."""
        response = client.post(BASE, json=create_payload, headers={"Authorization": client_token})
        assert response.status_code == 201
        assert response.json()["calle"] == "Av. Siempreviva"

    def test_create_con_admin_token_201(self, client, admin_token, create_payload):
        """ADMIN puede crear dirección → 201."""
        response = client.post(BASE, json=create_payload, headers={"Authorization": admin_token})
        assert response.status_code == 201

    def test_create_sin_token_401(self, client, create_payload):
        """Sin token → 401."""
        response = client.post(BASE, json=create_payload)
        assert response.status_code == 401

    def test_create_datos_invalidos_422(self, client, client_token):
        """Cuerpo inválido (campo requerido faltante) → 422."""
        response = client.post(
            BASE,
            json={"calle": "Av. Siempreviva"},  # faltan numero, ciudad, provincia, codigo_postal
            headers={"Authorization": client_token},
        )
        assert response.status_code == 422

    def test_create_valor_error_400(self, client, client_token, create_payload):
        """Servicio lanza ValueError → 400."""
        with patch("backend.modules.direcciones.service.DireccionService.create_direccion") as mock_create:
            mock_create.side_effect = ValueError("campo inválido")
            response = client.post(BASE, json=create_payload, headers={"Authorization": client_token})
        assert response.status_code == 400


# ── GET /clientes/me/direcciones ───────────────────────────────────────────────

class TestListDirecciones:
    """Tests para GET /clientes/me/direcciones"""

    def test_list_retorna_200(self, client, client_token, override_get_uow):
        """Lista de direcciones → 200."""
        # Pre-populate con una dirección para el user_id=1 (del token client)
        override_get_uow.direcciones.create(
            cliente_id=1,
            calle="Av. Siempreviva",
            numero="742",
            ciudad="Springfield",
            provincia="Buenos Aires",
            codigo_postal="1234",
        )
        response = client.get(BASE, headers={"Authorization": client_token})
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        assert len(response.json()) == 1

    def test_list_sin_token_401(self, client):
        """Sin token → 401."""
        response = client.get(BASE)
        assert response.status_code == 401

    def test_list_vacia_200(self, client, client_token):
        """Sin direcciones → 200 con lista vacía."""
        response = client.get(BASE, headers={"Authorization": client_token})
        assert response.status_code == 200
        assert response.json() == []


# ── PUT /clientes/me/direcciones/{id} ─────────────────────────────────────────

class TestUpdateDireccion:
    """Tests para PUT /clientes/me/direcciones/{id}"""

    def test_update_exitoso_200(self, client, client_token, override_get_uow):
        """Actualización exitosa → 200."""
        # Crear dirección con cliente_id=1 (mismo que el token)
        override_get_uow.direcciones.create(
            cliente_id=1,
            calle="Av. Siempreviva",
            numero="742",
            ciudad="Springfield",
            provincia="Buenos Aires",
            codigo_postal="1234",
        )
        response = client.put(
            f"{BASE}/1",
            json={"calle": "Nueva Calle"},
            headers={"Authorization": client_token},
        )
        assert response.status_code == 200

    def test_update_sin_token_401(self, client):
        response = client.put(f"{BASE}/1", json={"calle": "X"})
        assert response.status_code == 401

    def test_update_no_propietario_403(self, client, client_token, override_get_uow):
        """Intentar actualizar dirección ajena (cliente_id=2) → 403."""
        # Crear dirección con cliente_id=2 (diferente al token user_id=1)
        override_get_uow.direcciones.create(
            cliente_id=2,
            calle="Calle Ajena",
            numero="1",
            ciudad="Ciudad",
            provincia="Provincia",
            codigo_postal="0000",
        )
        response = client.put(
            f"{BASE}/1",
            json={"calle": "X"},
            headers={"Authorization": client_token},
        )
        assert response.status_code == 403

    def test_update_inexistente_404(self, client, client_token):
        """Dirección no encontrada → 404."""
        response = client.put(
            f"{BASE}/999",
            json={"calle": "X"},
            headers={"Authorization": client_token},
        )
        assert response.status_code == 404


# ── DELETE /clientes/me/direcciones/{id} ──────────────────────────────────────

class TestDeleteDireccion:
    """Tests para DELETE /clientes/me/direcciones/{id}"""

    def test_delete_exitoso_204(self, client, client_token, override_get_uow):
        """Soft-delete exitoso → 204."""
        override_get_uow.direcciones.create(
            cliente_id=1,
            calle="Av. Siempreviva",
            numero="742",
            ciudad="Springfield",
            provincia="Buenos Aires",
            codigo_postal="1234",
        )
        response = client.delete(f"{BASE}/1", headers={"Authorization": client_token})
        assert response.status_code == 204

    def test_delete_sin_token_401(self, client):
        response = client.delete(f"{BASE}/1")
        assert response.status_code == 401

    def test_delete_no_propietario_403(self, client, client_token, override_get_uow):
        """Intentar eliminar dirección ajena (cliente_id=2) → 403."""
        override_get_uow.direcciones.create(
            cliente_id=2,
            calle="Calle Ajena",
            numero="1",
            ciudad="Ciudad",
            provincia="Provincia",
            codigo_postal="0000",
        )
        response = client.delete(f"{BASE}/1", headers={"Authorization": client_token})
        assert response.status_code == 403

    def test_delete_inexistente_404(self, client, client_token):
        response = client.delete(f"{BASE}/999", headers={"Authorization": client_token})
        assert response.status_code == 404


# ── PUT /clientes/me/direcciones/{id}/predeterminada ─────────────────────────

class TestSetPredeterminada:
    """Tests para PUT /clientes/me/direcciones/{id}/predeterminada"""

    def test_marcar_predeterminada_200(self, client, client_token, override_get_uow):
        """Marcar predeterminada exitosamente → 200."""
        override_get_uow.direcciones.create(
            cliente_id=1,
            calle="Av. Siempreviva",
            numero="742",
            ciudad="Springfield",
            provincia="Buenos Aires",
            codigo_postal="1234",
        )
        response = client.put(
            f"{BASE}/1/predeterminada",
            headers={"Authorization": client_token},
        )
        assert response.status_code == 200
        assert response.json()["es_predeterminada"] is True

    def test_marcar_predeterminada_sin_token_401(self, client):
        response = client.put(f"{BASE}/1/predeterminada")
        assert response.status_code == 401

    def test_marcar_predeterminada_ajena_403(self, client, client_token, override_get_uow):
        """Intentar marcar predeterminada en dirección ajena (cliente_id=2) → 403."""
        override_get_uow.direcciones.create(
            cliente_id=2,
            calle="Calle Ajena",
            numero="1",
            ciudad="Ciudad",
            provincia="Provincia",
            codigo_postal="0000",
        )
        response = client.put(
            f"{BASE}/1/predeterminada",
            headers={"Authorization": client_token},
        )
        assert response.status_code == 403

    def test_marcar_predeterminada_inexistente_404(self, client, client_token):
        response = client.put(
            f"{BASE}/999/predeterminada",
            headers={"Authorization": client_token},
        )
        assert response.status_code == 404
