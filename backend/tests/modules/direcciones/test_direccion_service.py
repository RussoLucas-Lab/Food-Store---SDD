"""
Tests unitarios para DireccionService.

Prueba la lógica de negocio sin dependencias de FastAPI:
- RN-DI01: primera dirección del cliente → es_predeterminada=True forzado
- RN-DI02: solo una dirección predeterminada por cliente
- RN-DI03: ownership — acceso rechazado a dirección ajena
- Reasignación de predeterminada al eliminar
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from backend.modules.direcciones.service import DireccionService
from backend.modules.direcciones.exceptions import DireccionNotFound, UnauthorizedDireccionAccess
from backend.modules.direcciones.schemas import DireccionCreate, DireccionUpdate
from backend.modules.direcciones.model import DireccionEntrega


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_direccion(id: int, cliente_id: int, es_predeterminada: bool = False, activo: bool = True) -> DireccionEntrega:
    """Construir una DireccionEntrega de prueba."""
    return DireccionEntrega(
        id=id,
        cliente_id=cliente_id,
        calle="Av. Siempreviva",
        numero="742",
        ciudad="Springfield",
        provincia="Buenos Aires",
        codigo_postal="1234",
        es_predeterminada=es_predeterminada,
        activo=activo,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def mock_uow():
    """Mock Unit of Work con repositorio de direcciones."""
    uow = Mock()
    uow.direcciones = Mock()
    uow.commit = Mock()
    uow.rollback = Mock()
    return uow


@pytest.fixture
def service(mock_uow):
    """DireccionService con mock UoW."""
    return DireccionService(mock_uow)


@pytest.fixture
def dto_create():
    """DTO válido para crear dirección."""
    return DireccionCreate(
        calle="Av. Siempreviva",
        numero="742",
        ciudad="Springfield",
        provincia="Buenos Aires",
        codigo_postal="1234",
    )


# ── Tests RN-DI01: primera dirección es predeterminada ────────────────────────

class TestRnDi01:
    """RN-DI01: primera dirección del cliente → es_predeterminada=True forzado."""

    def test_primera_direccion_es_predeterminada(self, service, mock_uow, dto_create):
        """Primera dirección del cliente → es_predeterminada=True aunque DTO diga False."""
        dir1 = _make_direccion(id=1, cliente_id=10, es_predeterminada=True)
        mock_uow.direcciones.count_by_cliente.return_value = 0
        mock_uow.direcciones.create.return_value = dir1
        mock_uow.direcciones.set_predeterminada.return_value = dir1

        dto_create.es_predeterminada = False  # cliente pide False, pero es la primera
        result = service.create_direccion(user_id=10, dto=dto_create)

        # Verificar que se creó con es_predeterminada=True
        call_kwargs = mock_uow.direcciones.create.call_args.kwargs
        assert call_kwargs["es_predeterminada"] is True
        mock_uow.commit.assert_called_once()

    def test_segunda_direccion_respeta_dto(self, service, mock_uow, dto_create):
        """Segunda dirección → usa el valor de es_predeterminada del DTO."""
        dir2 = _make_direccion(id=2, cliente_id=10, es_predeterminada=False)
        mock_uow.direcciones.count_by_cliente.return_value = 1  # ya hay una
        mock_uow.direcciones.create.return_value = dir2

        dto_create.es_predeterminada = False
        service.create_direccion(user_id=10, dto=dto_create)

        call_kwargs = mock_uow.direcciones.create.call_args.kwargs
        assert call_kwargs["es_predeterminada"] is False

    def test_segunda_direccion_con_es_predeterminada_true(self, service, mock_uow, dto_create):
        """Segunda dirección con es_predeterminada=True → se llama set_predeterminada."""
        dir2 = _make_direccion(id=2, cliente_id=10, es_predeterminada=True)
        mock_uow.direcciones.count_by_cliente.return_value = 1
        mock_uow.direcciones.create.return_value = dir2
        mock_uow.direcciones.set_predeterminada.return_value = dir2

        dto_create.es_predeterminada = True
        service.create_direccion(user_id=10, dto=dto_create)

        mock_uow.direcciones.set_predeterminada.assert_called_once_with(dir2.id)


# ── Tests RN-DI02: solo una predeterminada ────────────────────────────────────

class TestRnDi02:
    """RN-DI02: unicidad de dirección predeterminada por cliente."""

    def test_set_predeterminada_llama_repo(self, service, mock_uow):
        """set_predeterminada delega al repo que garantiza la invariante."""
        dir1 = _make_direccion(id=1, cliente_id=5, es_predeterminada=False)
        dir1_updated = _make_direccion(id=1, cliente_id=5, es_predeterminada=True)
        mock_uow.direcciones.get_by_id.side_effect = [dir1, dir1_updated]
        mock_uow.direcciones.set_predeterminada.return_value = dir1_updated

        result = service.set_predeterminada(user_id=5, direccion_id=1)

        mock_uow.direcciones.set_predeterminada.assert_called_once_with(1)
        assert result["es_predeterminada"] is True
        mock_uow.commit.assert_called_once()

    def test_crear_con_predeterminada_desmarca_otras(self, service, mock_uow, dto_create):
        """Crear dirección predeterminada → set_predeterminada desmarca las demás."""
        new_dir = _make_direccion(id=3, cliente_id=5, es_predeterminada=True)
        mock_uow.direcciones.count_by_cliente.return_value = 2
        mock_uow.direcciones.create.return_value = new_dir
        mock_uow.direcciones.set_predeterminada.return_value = new_dir

        dto_create.es_predeterminada = True
        service.create_direccion(user_id=5, dto=dto_create)

        mock_uow.direcciones.set_predeterminada.assert_called_once_with(new_dir.id)


# ── Tests RN-DI03: ownership ──────────────────────────────────────────────────

class TestRnDi03:
    """RN-DI03: ownership — usuario solo puede operar sobre sus propias direcciones."""

    def test_update_ajena_lanza_unauthorized(self, service, mock_uow):
        """Actualizar dirección ajena → UnauthorizedDireccionAccess."""
        dir_ajena = _make_direccion(id=1, cliente_id=99)  # pertenece al cliente 99
        mock_uow.direcciones.get_by_id.return_value = dir_ajena

        dto = DireccionUpdate(calle="Otra calle")
        with pytest.raises(UnauthorizedDireccionAccess):
            service.update_direccion(user_id=1, direccion_id=1, dto=dto)  # user 1, no 99

    def test_delete_ajena_lanza_unauthorized(self, service, mock_uow):
        """Eliminar dirección ajena → UnauthorizedDireccionAccess."""
        dir_ajena = _make_direccion(id=2, cliente_id=99)
        mock_uow.direcciones.get_by_id.return_value = dir_ajena

        with pytest.raises(UnauthorizedDireccionAccess):
            service.delete_direccion(user_id=1, direccion_id=2)

    def test_set_predeterminada_ajena_lanza_unauthorized(self, service, mock_uow):
        """Marcar predeterminada ajena → UnauthorizedDireccionAccess."""
        dir_ajena = _make_direccion(id=3, cliente_id=99)
        mock_uow.direcciones.get_by_id.return_value = dir_ajena

        with pytest.raises(UnauthorizedDireccionAccess):
            service.set_predeterminada(user_id=1, direccion_id=3)

    def test_operacion_propia_permitida(self, service, mock_uow):
        """Actualizar dirección propia → permitido."""
        dir_propia = _make_direccion(id=1, cliente_id=1)
        dir_actualizada = _make_direccion(id=1, cliente_id=1)
        mock_uow.direcciones.get_by_id.side_effect = [dir_propia, dir_actualizada]
        mock_uow.direcciones.update.return_value = dir_actualizada

        dto = DireccionUpdate(calle="Nueva Calle")
        service.update_direccion(user_id=1, direccion_id=1, dto=dto)

        mock_uow.direcciones.update.assert_called_once()
        mock_uow.commit.assert_called_once()


# ── Tests: NotFound ────────────────────────────────────────────────────────────

class TestNotFound:
    """Dirección inexistente lanza DireccionNotFound."""

    def test_update_inexistente(self, service, mock_uow):
        mock_uow.direcciones.get_by_id.return_value = None
        with pytest.raises(DireccionNotFound):
            service.update_direccion(user_id=1, direccion_id=999, dto=DireccionUpdate(calle="X"))

    def test_delete_inexistente(self, service, mock_uow):
        mock_uow.direcciones.get_by_id.return_value = None
        with pytest.raises(DireccionNotFound):
            service.delete_direccion(user_id=1, direccion_id=999)

    def test_set_predeterminada_inexistente(self, service, mock_uow):
        mock_uow.direcciones.get_by_id.return_value = None
        with pytest.raises(DireccionNotFound):
            service.set_predeterminada(user_id=1, direccion_id=999)


# ── Tests: reasignación de predeterminada al eliminar ─────────────────────────

class TestReasignacionPredeterminada:
    """Al eliminar la dirección predeterminada, se reasigna a la más antigua restante."""

    def test_eliminar_predeterminada_reasigna_mas_antigua(self, service, mock_uow):
        """Eliminar predeterminada → la más antigua (menor id) se convierte en predeterminada."""
        dir_pred = _make_direccion(id=5, cliente_id=10, es_predeterminada=True)
        dir_antigua = _make_direccion(id=2, cliente_id=10, es_predeterminada=False)
        dir_nueva = _make_direccion(id=8, cliente_id=10, es_predeterminada=False)

        mock_uow.direcciones.get_by_id.return_value = dir_pred
        mock_uow.direcciones.soft_delete.return_value = True
        # Después del soft_delete, quedan las dos restantes
        mock_uow.direcciones.list_by_cliente.return_value = [dir_nueva, dir_antigua]
        mock_uow.direcciones.set_predeterminada.return_value = dir_antigua

        service.delete_direccion(user_id=10, direccion_id=5)

        # Debe promoverse la de menor id (dir_antigua con id=2)
        mock_uow.direcciones.set_predeterminada.assert_called_once_with(dir_antigua.id)
        mock_uow.commit.assert_called_once()

    def test_eliminar_predeterminada_sin_restantes_no_reasigna(self, service, mock_uow):
        """Eliminar la única dirección predeterminada → no se llama set_predeterminada."""
        dir_pred = _make_direccion(id=1, cliente_id=10, es_predeterminada=True)
        mock_uow.direcciones.get_by_id.return_value = dir_pred
        mock_uow.direcciones.soft_delete.return_value = True
        mock_uow.direcciones.list_by_cliente.return_value = []  # no quedan más

        service.delete_direccion(user_id=10, direccion_id=1)

        mock_uow.direcciones.set_predeterminada.assert_not_called()
        mock_uow.commit.assert_called_once()

    def test_eliminar_no_predeterminada_no_reasigna(self, service, mock_uow):
        """Eliminar dirección que no es predeterminada → no cambia ninguna predeterminada."""
        dir_no_pred = _make_direccion(id=3, cliente_id=10, es_predeterminada=False)
        mock_uow.direcciones.get_by_id.return_value = dir_no_pred
        mock_uow.direcciones.soft_delete.return_value = True

        service.delete_direccion(user_id=10, direccion_id=3)

        mock_uow.direcciones.set_predeterminada.assert_not_called()
        mock_uow.direcciones.list_by_cliente.assert_not_called()
        mock_uow.commit.assert_called_once()

    def test_list_direcciones_devuelve_solo_propias(self, service, mock_uow):
        """list_direcciones devuelve solo las direcciones del cliente autenticado."""
        dirs = [
            _make_direccion(id=1, cliente_id=7),
            _make_direccion(id=2, cliente_id=7),
        ]
        mock_uow.direcciones.list_by_cliente.return_value = dirs

        result = service.list_direcciones(user_id=7)

        mock_uow.direcciones.list_by_cliente.assert_called_once_with(7)
        assert len(result) == 2
