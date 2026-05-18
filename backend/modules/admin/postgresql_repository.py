"""
Implementación PostgreSQL de métricas y gestión de usuarios admin.

Usa SQLModel Session con queries directas via sqlalchemy.text()
para las agregaciones de métricas. No duplica la tabla de usuarios
sino que delega a PostgreSQLUsuarioRepository.
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from collections import defaultdict
from sqlmodel import Session, select, text

from backend.modules.pedidos.sqlmodel_model import PedidoDB, DetallePedidoDB
from backend.modules.auth.sqlmodel_model import UsuarioDB
from backend.modules.productos.sqlmodel_model import ProductoDB


# Estados de venta efectiva (pedidos que generan revenue)
ESTADOS_EFECTIVOS = {"CONFIRMADO", "EN_PREPARACION", "EN_CAMINO", "ENTREGADO"}


class PostgreSQLAdminMetricasRepository:
    """
    Repositorio de solo lectura para métricas agregadas usando PostgreSQL.
    """

    def __init__(self, session: Session):
        self._session = session

    def get_resumen(self) -> Dict[str, Any]:
        """Calcular resumen general de métricas."""
        # Ventas totales y cantidad de pedidos efectivos
        pedidos = self._session.exec(
            select(PedidoDB).where(PedidoDB.estado.in_(list(ESTADOS_EFECTIVOS)))
        ).all()

        ventas_totales = sum(float(p.total) for p in pedidos)
        cantidad_pedidos = len(pedidos)

        # Cantidad de usuarios registrados
        cantidad_usuarios = len(self._session.exec(select(UsuarioDB)).all())

        # Productos sin stock
        productos = self._session.exec(select(ProductoDB)).all()
        productos_sin_stock = sum(1 for p in productos if getattr(p, "stock", 0) == 0)

        return {
            "ventas_totales": ventas_totales,
            "cantidad_pedidos": cantidad_pedidos,
            "cantidad_usuarios": cantidad_usuarios,
            "productos_sin_stock": productos_sin_stock,
        }

    def get_serie_temporal(
        self,
        desde: Optional[date],
        hasta: Optional[date],
        granularidad: str,
    ) -> List[Dict[str, Any]]:
        """Serie temporal de ventas agrupada por período."""
        stmt = select(PedidoDB).where(PedidoDB.estado.in_(list(ESTADOS_EFECTIVOS)))

        if desde:
            stmt = stmt.where(PedidoDB.creado_en >= datetime(desde.year, desde.month, desde.day))
        if hasta:
            end = datetime(hasta.year, hasta.month, hasta.day) + timedelta(days=1)
            stmt = stmt.where(PedidoDB.creado_en < end)

        pedidos = self._session.exec(stmt).all()

        acum: Dict[str, float] = defaultdict(float)
        for p in pedidos:
            clave = self._truncar_fecha(p.creado_en, granularidad)
            acum[clave] += float(p.total)

        return [{"periodo": k, "monto": v} for k, v in sorted(acum.items())]

    def _truncar_fecha(self, dt: datetime, granularidad: str) -> str:
        """Truncar un datetime según la granularidad."""
        if granularidad == "mes":
            return dt.strftime("%Y-%m-01")
        elif granularidad == "semana":
            days_since_monday = dt.weekday()
            start_of_week = dt - timedelta(days=days_since_monday)
            return start_of_week.strftime("%Y-%m-%d")
        else:  # dia
            return dt.strftime("%Y-%m-%d")

    def get_top_productos(
        self,
        top: int,
        desde: Optional[date],
        hasta: Optional[date],
    ) -> List[Dict[str, Any]]:
        """Ranking de productos más vendidos."""
        # Obtener IDs de pedidos efectivos en el rango
        stmt = select(PedidoDB).where(PedidoDB.estado.in_(list(ESTADOS_EFECTIVOS)))

        if desde:
            stmt = stmt.where(PedidoDB.creado_en >= datetime(desde.year, desde.month, desde.day))
        if hasta:
            end = datetime(hasta.year, hasta.month, hasta.day) + timedelta(days=1)
            stmt = stmt.where(PedidoDB.creado_en < end)

        pedidos = self._session.exec(stmt).all()
        pedidos_ids = {p.id for p in pedidos}

        if not pedidos_ids:
            return []

        # Acumular cantidades por producto
        detalles = self._session.exec(
            select(DetallePedidoDB).where(DetallePedidoDB.pedido_id.in_(list(pedidos_ids)))
        ).all()

        acum_cantidad: Dict[int, int] = defaultdict(int)
        acum_nombre: Dict[int, str] = {}
        for d in detalles:
            acum_cantidad[d.producto_id] += d.cantidad
            if d.producto_id not in acum_nombre:
                acum_nombre[d.producto_id] = d.nombre_snapshot

        ranking = [
            {
                "producto_id": pid,
                "nombre": acum_nombre.get(pid, f"Producto {pid}"),
                "cantidad_vendida": cant,
            }
            for pid, cant in acum_cantidad.items()
        ]
        ranking.sort(key=lambda x: x["cantidad_vendida"], reverse=True)
        return ranking[:top]

    def get_distribucion_estados(
        self,
        desde: Optional[date],
        hasta: Optional[date],
    ) -> List[Dict[str, Any]]:
        """Distribución de pedidos agrupada por estado."""
        stmt = select(PedidoDB)

        if desde:
            stmt = stmt.where(PedidoDB.creado_en >= datetime(desde.year, desde.month, desde.day))
        if hasta:
            end = datetime(hasta.year, hasta.month, hasta.day) + timedelta(days=1)
            stmt = stmt.where(PedidoDB.creado_en < end)

        pedidos = self._session.exec(stmt).all()
        acum: Dict[str, int] = defaultdict(int)
        for p in pedidos:
            acum[p.estado] += 1

        return [{"estado": estado, "cantidad": cnt} for estado, cnt in acum.items()]


class PostgreSQLAdminUsuariosRepository:
    """
    Repositorio para gestión de usuarios en el panel admin.
    Delega queries sobre la tabla de usuarios vía PostgreSQLUsuarioRepository.
    """

    def __init__(self, session: Session):
        self._session = session

    def list_usuarios(
        self,
        page: int = 1,
        size: int = 20,
        q: Optional[str] = None,
        rol: Optional[str] = None,
        activo: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """Listar usuarios con búsqueda, filtro y paginación."""
        stmt = select(UsuarioDB)

        if q:
            q_lower = f"%{q.lower()}%"
            stmt = stmt.filter(
                (UsuarioDB.email.ilike(q_lower)) | (UsuarioDB.nombre.ilike(q_lower))
            )

        if rol:
            stmt = stmt.where(UsuarioDB.role == rol.lower())

        if activo is not None:
            stmt = stmt.where(UsuarioDB.is_active == activo)

        all_usuarios = self._session.exec(stmt).all()
        total = len(all_usuarios)

        offset = (page - 1) * size
        items = all_usuarios[offset: offset + size]

        # Convertir a dicts para compatibilidad con service
        items_dicts = []
        for u in items:
            items_dicts.append({
                "id": u.id,
                "email": u.email,
                "nombre": u.nombre or u.email.split("@")[0],
                "role": u.role,
                "is_active": u.is_active,
                "created_at": u.created_at,
                "updated_at": u.updated_at,
            })

        return {
            "items": items_dicts,
            "total": total,
            "page": page,
            "size": size,
        }

    def find_by_id(self, user_id: int):
        """Buscar usuario por ID."""
        db_obj = self._session.get(UsuarioDB, user_id)
        if not db_obj:
            return None
        # Retornar como objeto con atributos compatibles
        return _UsuarioProxy(db_obj)

    def count_admins_activos(self) -> int:
        """Contar cuántos usuarios con rol admin están activos."""
        admins = self._session.exec(
            select(UsuarioDB).where(
                UsuarioDB.role == "admin",
                UsuarioDB.is_active == True,  # noqa: E712
            )
        ).all()
        return len(admins)

    def update_usuario(self, user_id: int, **kwargs):
        """Actualizar campos del usuario."""
        db_obj = self._session.get(UsuarioDB, user_id)
        if not db_obj:
            return None

        allowed = {"email", "nombre", "role", "is_active", "password_hash"}
        for key, value in kwargs.items():
            if key in allowed:
                # Normalizar role si tiene .value
                if key == "role" and hasattr(value, "value"):
                    value = value.value
                setattr(db_obj, key, value)

        db_obj.updated_at = datetime.utcnow()
        self._session.add(db_obj)
        self._session.flush()
        self._session.refresh(db_obj)
        return _UsuarioProxy(db_obj)

    def revocar_refresh_tokens(self, user_id: int) -> None:
        """Revocar todos los refresh tokens del usuario."""
        from backend.core.security import TokenService
        tokens_a_revocar = [
            token for token, data in TokenService._refresh_token_store.items()
            if data.get("user_id") == user_id
        ]
        for token in tokens_a_revocar:
            del TokenService._refresh_token_store[token]


class _UsuarioProxy:
    """
    Proxy que expone atributos de UsuarioDB con la misma interfaz
    que el modelo de dominio Usuario (para compatibilidad con AdminUsuariosService).
    """

    def __init__(self, db_obj: UsuarioDB):
        self.id = db_obj.id
        self.email = db_obj.email
        self.nombre = db_obj.nombre or db_obj.email.split("@")[0]
        self.role = db_obj.role
        self.is_active = db_obj.is_active
        self.created_at = db_obj.created_at
        self.updated_at = db_obj.updated_at
        # Compatibilidad con código que accede a .role.value
        self.password_hash = ""

    def to_dict(self, include_password_hash: bool = False) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "nombre": self.nombre,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }
