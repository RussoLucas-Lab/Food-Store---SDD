"""
Tests de integración para endpoints de despacho de pedidos.

Cubre:
- GET /api/v1/pedidos/gestion: acceso por rol, filtros, paginación
- PATCH /api/v1/pedidos/{id}/estado: transiciones válidas e inválidas
- GET /api/v1/pedidos/{id}: gestor ve cualquier pedido, client bloqueado en ajeno
"""

import pytest
import json
from fastapi.testclient import TestClient
from backend.main import app
import backend.modules.pedidos.router as pedidos_router_mod
from backend.modules.pedidos.model import Pedido, DetallePedido, HistorialEstadoPedido, EstadoPedidoEnum
from backend.modules.clientes.model import Cliente
from backend.modules.productos.model import Product
from datetime import datetime


@pytest.fixture
def client():
    return TestClient(app)


def _token(user_id: int, email: str, role: str) -> dict:
    """Genera headers con token JWT para el rol indicado."""
    from backend.core.security import TokenService
    token = TokenService.create_access_token(user_id=user_id, email=email, role=role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client_headers():
    return _token(1, "cliente@test.com", "CLIENT")


@pytest.fixture
def pedidos_headers():
    return _token(10, "gestor@test.com", "PEDIDOS")


@pytest.fixture
def admin_headers():
    return _token(20, "admin@test.com", "ADMIN")


@pytest.fixture(autouse=True)
def reset_uow():
    """Limpia el UoW singleton antes y después de cada test."""
    def _reset():
        uow = pedidos_router_mod.uow
        for attr in (
            '_pedidos', '_detalles_pedido', '_historial_estado',
            '_clientes', '_productos'
        ):
            if hasattr(uow, attr):
                repo = getattr(uow, attr)
                repo._storage.clear()
                repo._next_id = 1
                for idx_attr in ('_name_index', '_email_index'):
                    if hasattr(repo, idx_attr):
                        getattr(repo, idx_attr).clear()
        uow.committed = False

    _reset()
    yield
    _reset()


def _seed_base(uow_instance=None):
    """Crea un cliente (id=1) y un producto (id=1) en el UoW singleton."""
    if uow_instance is None:
        uow_instance = pedidos_router_mod.uow

    cliente = Cliente(
        id=1,
        nombre="Test Cliente",
        email="cliente@test.com",
        direccion="Av. San Martín 1234",
        telefono="+54 11 1234 5678",
        activo=True,
        user_id=1,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    uow_instance._clientes._storage[1] = cliente
    uow_instance._clientes._next_id = 2
    uow_instance._clientes._email_index["cliente@test.com"] = 1

    product = Product(id=1, nombre="Pizza", base_price=150.0, status="active")
    product.stock = 100.0
    uow_instance._productos._storage[1] = product
    uow_instance._productos._next_id = 2

    return cliente, product


def _seed_pedido_en_estado(estado: EstadoPedidoEnum, cliente_id: int = 1) -> int:
    """Crea directamente un pedido en el estado indicado y retorna su id."""
    uow = pedidos_router_mod.uow

    pedido = Pedido(
        cliente_id=cliente_id,
        estado=estado,
        total=300.0,
        costo_envio=0.0,
        direccion_snapshot=json.dumps({"calle": "Calle Falsa 123"}),
    )
    pedido = uow._pedidos.create(pedido)

    # Agregar detalle
    detalle = DetallePedido(
        pedido_id=pedido.id,
        producto_id=1,
        nombre_snapshot="Pizza",
        cantidad=2,
        precio_snapshot=150.0,
    )
    uow._detalles_pedido.create(detalle)

    # Historial inicial
    historial = HistorialEstadoPedido(
        pedido_id=pedido.id,
        estado_anterior=None,
        estado_nuevo=estado,
        usuario_id=cliente_id,
        observacion="Pedido creado",
    )
    uow._historial_estado.create(historial)

    return pedido.id


VALID_CART = {
    "items": [{"producto_id": 1, "cantidad": 2, "personalizacion": {"excluidos": []}}],
    "direccion_id": 10,
}


# ══════════════════════════════════════════════════════════════════════════════
# Task 10.5 — GET /api/v1/pedidos/gestion
# ══════════════════════════════════════════════════════════════════════════════

class TestGestionListadoEndpoint:
    """Tests para GET /api/v1/pedidos/gestion."""

    def test_pedidos_puede_acceder(self, client, pedidos_headers):
        """PEDIDOS puede acceder al listado de gestión → 200."""
        response = client.get("/api/v1/pedidos/gestion", headers=pedidos_headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_admin_puede_acceder(self, client, admin_headers):
        """ADMIN puede acceder al listado de gestión → 200."""
        response = client.get("/api/v1/pedidos/gestion", headers=admin_headers)
        assert response.status_code == 200

    def test_client_no_puede_acceder(self, client, client_headers):
        """CLIENT no puede acceder al listado de gestión → 403."""
        response = client.get("/api/v1/pedidos/gestion", headers=client_headers)
        assert response.status_code == 403

    def test_sin_auth_retorna_401(self, client):
        """Sin token → 401."""
        response = client.get("/api/v1/pedidos/gestion")
        assert response.status_code == 401

    def test_filtro_por_estado(self, client, pedidos_headers):
        """Filtro por estado devuelve solo pedidos en ese estado."""
        _seed_base()
        _seed_pedido_en_estado(EstadoPedidoEnum.CONFIRMADO)
        _seed_pedido_en_estado(EstadoPedidoEnum.PENDIENTE)

        response = client.get(
            "/api/v1/pedidos/gestion?estado=CONFIRMADO",
            headers=pedidos_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert all(p["estado"] == "CONFIRMADO" for p in data)

    def test_paginacion(self, client, admin_headers):
        """Los parámetros skip y limit funcionan correctamente."""
        _seed_base()
        for _ in range(5):
            _seed_pedido_en_estado(EstadoPedidoEnum.PENDIENTE)

        response = client.get(
            "/api/v1/pedidos/gestion?skip=0&limit=2",
            headers=admin_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


# ══════════════════════════════════════════════════════════════════════════════
# PATCH /api/v1/pedidos/{id}/estado
# ══════════════════════════════════════════════════════════════════════════════

class TestPatchEstadoEndpoint:
    """Tests para PATCH /api/v1/pedidos/{id}/estado."""

    def test_admin_avanza_estado_valido(self, client, admin_headers):
        """ADMIN avanza CONFIRMADO → EN_PREPARACION → 200."""
        _seed_base()
        pedido_id = _seed_pedido_en_estado(EstadoPedidoEnum.CONFIRMADO)

        response = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "EN_PREPARACION"},
            headers=admin_headers,
        )
        assert response.status_code == 200
        assert response.json()["estado"] == "EN_PREPARACION"

    def test_transicion_invalida_retorna_409(self, client, admin_headers):
        """Transición inválida (salto) → 409."""
        _seed_base()
        pedido_id = _seed_pedido_en_estado(EstadoPedidoEnum.CONFIRMADO)

        response = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "EN_CAMINO"},
            headers=admin_headers,
        )
        assert response.status_code == 409

    def test_rol_no_autorizado_retorna_403(self, client, pedidos_headers):
        """PEDIDOS no puede cancelar desde EN_PREPARACION → 403."""
        _seed_base()
        pedido_id = _seed_pedido_en_estado(EstadoPedidoEnum.EN_PREPARACION)

        response = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "CANCELADO", "motivo": "Test"},
            headers=pedidos_headers,
        )
        assert response.status_code == 403

    def test_cancelar_sin_motivo_retorna_422(self, client, admin_headers):
        """Cancelar sin motivo → 422 (validación Pydantic)."""
        _seed_base()
        pedido_id = _seed_pedido_en_estado(EstadoPedidoEnum.CONFIRMADO)

        response = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "CANCELADO"},
            headers=admin_headers,
        )
        assert response.status_code == 422

    def test_pedido_no_encontrado_retorna_404(self, client, admin_headers):
        """Pedido inexistente → 404."""
        response = client.patch(
            "/api/v1/pedidos/9999/estado",
            json={"nuevo_estado": "EN_PREPARACION"},
            headers=admin_headers,
        )
        assert response.status_code == 404

    def test_pendiente_a_confirmado_rechazado(self, client, admin_headers):
        """PENDIENTE → CONFIRMADO (manual) rechazado → 409 (D2)."""
        _seed_base()
        pedido_id = _seed_pedido_en_estado(EstadoPedidoEnum.PENDIENTE)

        response = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "CONFIRMADO"},
            headers=admin_headers,
        )
        assert response.status_code == 409

    def test_client_cancela_propio_pedido_pendiente(self, client, client_headers):
        """CLIENT puede cancelar su propio pedido en PENDIENTE con motivo."""
        _seed_base()
        pedido_id = _seed_pedido_en_estado(EstadoPedidoEnum.PENDIENTE, cliente_id=1)

        response = client.patch(
            f"/api/v1/pedidos/{pedido_id}/estado",
            json={"nuevo_estado": "CANCELADO", "motivo": "No me conviene"},
            headers=client_headers,
        )
        assert response.status_code == 200
        assert response.json()["estado"] == "CANCELADO"


# ══════════════════════════════════════════════════════════════════════════════
# GET /api/v1/pedidos/{id} con rol
# ══════════════════════════════════════════════════════════════════════════════

class TestGetDetalleConRol:
    """Tests para GET /api/v1/pedidos/{id} respetando el rol."""

    def test_gestor_accede_a_pedido_ajeno(self, client, pedidos_headers):
        """PEDIDOS puede ver el detalle de cualquier pedido → 200."""
        _seed_base()
        # cliente_id=1, pero el token de pedidos_headers tiene user_id=10
        pedido_id = _seed_pedido_en_estado(EstadoPedidoEnum.CONFIRMADO, cliente_id=1)

        response = client.get(f"/api/v1/pedidos/{pedido_id}", headers=pedidos_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pedido_id

    def test_client_ve_su_propio_pedido(self, client, client_headers):
        """CLIENT puede ver el detalle de su propio pedido → 200."""
        _seed_base()
        pedido_id = _seed_pedido_en_estado(EstadoPedidoEnum.PENDIENTE, cliente_id=1)

        response = client.get(f"/api/v1/pedidos/{pedido_id}", headers=client_headers)
        assert response.status_code == 200

    def test_client_bloqueado_en_pedido_ajeno(self, client):
        """CLIENT bloqueado al ver pedido de otro cliente → 403."""
        _seed_base()
        # Pedido del cliente 2
        _seed_pedido_en_estado(EstadoPedidoEnum.PENDIENTE, cliente_id=2)

        # Token del cliente 1
        headers = _token(1, "cliente@test.com", "CLIENT")
        # El segundo pedido tiene id=1 pero pertenece a cliente_id=2
        uow = pedidos_router_mod.uow
        pedidos_lista = list(uow._pedidos._storage.values())
        pedido_id = pedidos_lista[0].id

        response = client.get(f"/api/v1/pedidos/{pedido_id}", headers=headers)
        assert response.status_code == 403

    def test_pedido_inexistente_retorna_404(self, client, pedidos_headers):
        """Pedido inexistente → 404."""
        response = client.get("/api/v1/pedidos/9999", headers=pedidos_headers)
        assert response.status_code == 404
