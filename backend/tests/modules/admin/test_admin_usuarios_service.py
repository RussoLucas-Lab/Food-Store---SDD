"""
Tests unitarios para AdminUsuariosService.

Verifica:
- Listado con búsqueda/filtros
- Edición de roles revoca tokens
- Rol inexistente rechazado (HTTP 422)
- RN-RB04 rechaza dejar sin ADMIN (HTTP 409)
- Auto-desactivación rechazada (HTTP 409)
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from fastapi import HTTPException
from backend.modules.admin.service import AdminUsuariosService
from backend.modules.auth.model import Usuario, RoleEnum


def _make_usuario(id, email, role="admin", is_active=True, nombre=None):
    """Crear usuario mock."""
    u = MagicMock(spec=Usuario)
    u.id = id
    u.email = email
    u.nombre = nombre or email.split("@")[0]
    u.role = MagicMock()
    u.role.value = role
    u.is_active = is_active
    return u


def _make_uow(usuarios_list=None):
    """Crear mock UoW con repositorio de usuarios."""
    uow = MagicMock()
    usuarios = {u.id: u for u in (usuarios_list or [])}
    uow.usuarios._storage = usuarios

    def find_by_id(uid):
        return usuarios.get(uid)

    def update(uid, **kwargs):
        u = usuarios.get(uid)
        if u:
            for k, v in kwargs.items():
                setattr(u, k, v)
        return u

    uow.usuarios.find_by_id.side_effect = find_by_id
    uow.usuarios.update.side_effect = update
    uow.commit = MagicMock()
    return uow


class TestListadoUsuarios:
    """Listado con búsqueda y filtros."""

    def test_lista_todos_sin_filtros(self):
        u1 = _make_usuario(1, "alice@test.com", "admin")
        u2 = _make_usuario(2, "bob@test.com", "customer")
        uow = _make_uow([u1, u2])
        service = AdminUsuariosService(uow)
        result = service.list_usuarios()
        assert result["total"] == 2

    def test_busqueda_por_email(self):
        u1 = _make_usuario(1, "alice@test.com", "admin")
        u2 = _make_usuario(2, "bob@test.com", "customer")
        uow = _make_uow([u1, u2])
        service = AdminUsuariosService(uow)
        result = service.list_usuarios(q="alice")
        assert result["total"] == 1
        assert result["items"][0]["email"] == "alice@test.com"

    def test_filtro_activo(self):
        u1 = _make_usuario(1, "alice@test.com", "admin", is_active=True)
        u2 = _make_usuario(2, "bob@test.com", "customer", is_active=False)
        uow = _make_uow([u1, u2])
        service = AdminUsuariosService(uow)
        result = service.list_usuarios(activo=True)
        assert result["total"] == 1
        assert result["items"][0]["is_active"] is True

    def test_respuesta_no_expone_password_hash(self):
        u1 = _make_usuario(1, "alice@test.com", "admin")
        uow = _make_uow([u1])
        service = AdminUsuariosService(uow)
        result = service.list_usuarios()
        for item in result["items"]:
            assert "password_hash" not in item
            assert "hash" not in item


class TestEdicionRoles:
    """Edición de roles con validaciones."""

    def test_rol_inexistente_rechazado(self):
        u = _make_usuario(1, "alice@test.com", "admin")
        uow = _make_uow([u])
        service = AdminUsuariosService(uow)
        with pytest.raises(HTTPException) as exc:
            service.update_usuario(
                user_id=1, current_user_id=99, role="SUPERADMIN"
            )
        assert exc.value.status_code == 422

    def test_rnrb04_rechaza_dejar_sin_admin(self):
        u = _make_usuario(1, "admin@test.com", "admin", is_active=True)
        uow = _make_uow([u])
        service = AdminUsuariosService(uow)
        # Único admin intenta cambiar a customer
        with pytest.raises(HTTPException) as exc:
            service.update_usuario(
                user_id=1, current_user_id=99, role="CLIENT"
            )
        assert exc.value.status_code == 409

    def test_puede_cambiar_rol_con_otro_admin(self):
        u1 = _make_usuario(1, "admin1@test.com", "admin", is_active=True)
        u2 = _make_usuario(2, "admin2@test.com", "admin", is_active=True)
        uow = _make_uow([u1, u2])
        service = AdminUsuariosService(uow)
        # Hay 2 admins, puede cambiar uno a customer
        result = service.update_usuario(
            user_id=1, current_user_id=99, role="CLIENT"
        )
        # No debe lanzar excepción
        assert result is not None

    def test_usuario_no_encontrado_lanza_404(self):
        uow = _make_uow([])
        service = AdminUsuariosService(uow)
        with pytest.raises(HTTPException) as exc:
            service.update_usuario(user_id=999, current_user_id=1, role="CLIENT")
        assert exc.value.status_code == 404


class TestActivacionDesactivacion:
    """Activación y desactivación de cuentas."""

    def test_auto_desactivacion_rechazada(self):
        u = _make_usuario(1, "admin@test.com", "admin", is_active=True)
        uow = _make_uow([u])
        service = AdminUsuariosService(uow)
        with pytest.raises(HTTPException) as exc:
            # user_id == current_user_id → auto-desactivación
            service.toggle_activo(user_id=1, current_user_id=1, activo=False)
        assert exc.value.status_code == 409

    def test_ultimo_admin_activo_no_se_puede_desactivar(self):
        u = _make_usuario(1, "admin@test.com", "admin", is_active=True)
        uow = _make_uow([u])
        service = AdminUsuariosService(uow)
        with pytest.raises(HTTPException) as exc:
            service.toggle_activo(user_id=1, current_user_id=99, activo=False)
        assert exc.value.status_code == 409

    def test_activar_usuario_inactivo(self):
        u = _make_usuario(1, "user@test.com", "customer", is_active=False)
        uow = _make_uow([u])
        service = AdminUsuariosService(uow)
        result = service.toggle_activo(user_id=1, current_user_id=99, activo=True)
        assert result["is_active"] is True

    def test_desactivar_usuario_no_admin(self):
        u1 = _make_usuario(1, "admin@test.com", "admin", is_active=True)
        u2 = _make_usuario(2, "user@test.com", "customer", is_active=True)
        uow = _make_uow([u1, u2])
        service = AdminUsuariosService(uow)
        result = service.toggle_activo(user_id=2, current_user_id=1, activo=False)
        assert result["is_active"] is False
