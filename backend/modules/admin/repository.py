"""
Repository para el módulo admin.

Implementa queries de agregación de solo lectura sobre el almacenamiento in-memory:
- Resumen de métricas (ventas, pedidos, usuarios, productos sin stock)
- Serie temporal de ventas por granularidad
- Top de productos más vendidos
- Distribución de pedidos por estado

También extiende el acceso a usuarios con búsqueda/filtro/paginación
reutilizando el repositorio de auth (usuarios) a través del UoW.
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from collections import defaultdict

from backend.modules.pedidos.model import EstadoPedidoEnum


# ── Estados de venta efectiva (D6) ────────────────────────────────────────────
ESTADOS_EFECTIVOS = {
    EstadoPedidoEnum.CONFIRMADO,
    EstadoPedidoEnum.EN_PREPARACION,
    EstadoPedidoEnum.EN_CAMINO,
    EstadoPedidoEnum.ENTREGADO,
}

# Valor string del enum para comparación
ESTADOS_EFECTIVOS_STR = {e.value for e in ESTADOS_EFECTIVOS}


class AdminMetricasRepository:
    """
    Repositorio de solo lectura para métricas agregadas.

    Opera directamente sobre los repositorios in-memory del UoW.
    No realiza writes ni commits.
    """

    def __init__(self, uow):
        """
        Args:
            uow: Unit of Work que provee acceso a los repositorios.
        """
        self.uow = uow

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _fecha_en_rango(self, dt: datetime, desde: Optional[date], hasta: Optional[date]) -> bool:
        """Verificar si un datetime está dentro del rango [desde, hasta]."""
        if desde and dt.date() < desde:
            return False
        if hasta and dt.date() > hasta:
            return False
        return True

    def _truncar_fecha(self, dt: datetime, granularidad: str) -> str:
        """
        Truncar un datetime según la granularidad para agrupar la serie temporal.

        Args:
            dt: datetime del pedido
            granularidad: 'dia', 'semana' o 'mes'

        Returns:
            String de la fecha truncada (ISO 8601)
        """
        if granularidad == "mes":
            return dt.strftime("%Y-%m-01")
        elif granularidad == "semana":
            # Truncar al lunes de la semana
            days_since_monday = dt.weekday()
            start_of_week = dt - __import__('datetime').timedelta(days=days_since_monday)
            return start_of_week.strftime("%Y-%m-%d")
        else:  # dia (default)
            return dt.strftime("%Y-%m-%d")

    # ── Queries de métricas ───────────────────────────────────────────────────

    def get_resumen(self) -> Dict[str, Any]:
        """
        Calcular resumen general de métricas.

        Returns:
            dict con ventas_totales, cantidad_pedidos, cantidad_usuarios, productos_sin_stock
        """
        pedidos = list(self.uow.pedidos._storage.values())
        pedidos_efectivos = [
            p for p in pedidos
            if (p.estado.value if hasattr(p.estado, 'value') else p.estado) in ESTADOS_EFECTIVOS_STR
        ]

        ventas_totales = sum(float(p.total) for p in pedidos_efectivos)
        cantidad_pedidos = len(pedidos_efectivos)

        # Contar usuarios registrados
        cantidad_usuarios = len(self.uow.usuarios._storage)

        # Contar productos sin stock
        productos = list(self.uow.productos._storage.values())
        productos_sin_stock = sum(
            1 for p in productos
            if getattr(p, 'stock', None) == 0
        )

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
        """
        Serie temporal de ventas agrupada por período.

        Args:
            desde: fecha de inicio (inclusive)
            hasta: fecha de fin (inclusive)
            granularidad: 'dia', 'semana' o 'mes'

        Returns:
            Lista ordenada de dicts {periodo, monto}
        """
        pedidos = list(self.uow.pedidos._storage.values())

        # Filtrar por estado efectivo y rango de fechas
        acum: Dict[str, float] = defaultdict(float)
        for p in pedidos:
            estado_val = p.estado.value if hasattr(p.estado, 'value') else p.estado
            if estado_val not in ESTADOS_EFECTIVOS_STR:
                continue
            if not self._fecha_en_rango(p.creado_en, desde, hasta):
                continue

            clave = self._truncar_fecha(p.creado_en, granularidad)
            acum[clave] += float(p.total)

        # Ordenar cronológicamente
        serie = [{"periodo": k, "monto": v} for k, v in sorted(acum.items())]
        return serie

    def get_top_productos(
        self,
        top: int,
        desde: Optional[date],
        hasta: Optional[date],
    ) -> List[Dict[str, Any]]:
        """
        Ranking de productos más vendidos por cantidad.

        Args:
            top: número máximo de resultados
            desde: fecha de inicio (inclusive)
            hasta: fecha de fin (inclusive)

        Returns:
            Lista de dicts {producto_id, nombre, cantidad_vendida} ordenada desc
        """
        pedidos = list(self.uow.pedidos._storage.values())

        # IDs de pedidos en estado efectivo dentro del rango
        pedidos_ids_efectivos = set()
        for p in pedidos:
            estado_val = p.estado.value if hasattr(p.estado, 'value') else p.estado
            if estado_val not in ESTADOS_EFECTIVOS_STR:
                continue
            if not self._fecha_en_rango(p.creado_en, desde, hasta):
                continue
            pedidos_ids_efectivos.add(p.id)

        # Acumular cantidades por producto sobre los detalles de esos pedidos
        acum_cantidad: Dict[int, int] = defaultdict(int)
        acum_nombre: Dict[int, str] = {}

        detalles = list(self.uow.detalles_pedido._storage.values())
        for d in detalles:
            if d.pedido_id not in pedidos_ids_efectivos:
                continue
            acum_cantidad[d.producto_id] += d.cantidad
            if d.producto_id not in acum_nombre:
                acum_nombre[d.producto_id] = d.nombre_snapshot

        # Construir ranking ordenado desc por cantidad
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
        """
        Distribución de pedidos agrupada por estado.

        Args:
            desde: fecha de inicio (inclusive, opcional)
            hasta: fecha de fin (inclusive, opcional)

        Returns:
            Lista de dicts {estado, cantidad}
        """
        pedidos = list(self.uow.pedidos._storage.values())

        acum: Dict[str, int] = defaultdict(int)
        for p in pedidos:
            if not self._fecha_en_rango(p.creado_en, desde, hasta):
                continue
            estado_val = p.estado.value if hasattr(p.estado, 'value') else str(p.estado)
            acum[estado_val] += 1

        return [{"estado": estado, "cantidad": cnt} for estado, cnt in acum.items()]


class AdminUsuariosRepository:
    """
    Repositorio para gestión de usuarios en el panel admin.

    Envuelve el repositorio de usuarios (auth) del UoW con operaciones
    adicionales de búsqueda, filtrado y paginación.
    No duplica la tabla — opera sobre self.uow.usuarios.
    """

    def __init__(self, uow):
        self.uow = uow

    def list_usuarios(
        self,
        page: int = 1,
        size: int = 20,
        q: Optional[str] = None,
        rol: Optional[str] = None,
        activo: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Listar usuarios con búsqueda, filtro y paginación.

        Args:
            page: página (1-indexed)
            size: tamaño de página
            q: término de búsqueda por nombre o email
            rol: filtrar por rol
            activo: filtrar por estado is_active

        Returns:
            dict con items (lista de usuarios), total, page, size
        """
        usuarios = self.uow.usuarios.list_all(limit=10000, offset=0)

        # Filtrar por búsqueda de texto
        if q:
            q_lower = q.lower()
            usuarios = [
                u for u in usuarios
                if q_lower in u.email.lower()
                or q_lower in (u.nombre or "").lower()
            ]

        # Filtrar por rol
        if rol:
            rol_lower = rol.lower()
            usuarios = [
                u for u in usuarios
                if (u.role.value if hasattr(u.role, 'value') else u.role).lower() == rol_lower
            ]

        # Filtrar por estado activo
        if activo is not None:
            usuarios = [u for u in usuarios if u.is_active == activo]

        total = len(usuarios)

        # Paginación
        offset = (page - 1) * size
        items = usuarios[offset: offset + size]

        return {
            "items": items,
            "total": total,
            "page": page,
            "size": size,
        }

    def find_by_id(self, user_id: int):
        """Buscar usuario por ID."""
        return self.uow.usuarios.find_by_id(user_id)

    def count_admins_activos(self) -> int:
        """Contar cuántos usuarios con rol admin están activos."""
        todos = self.uow.usuarios.list_all(limit=10000, offset=0)
        return sum(
            1 for u in todos
            if (u.role.value if hasattr(u.role, 'value') else u.role).lower() == "admin"
            and u.is_active
        )

    def update_usuario(self, user_id: int, **kwargs):
        """Actualizar campos del usuario vía el repo de usuarios."""
        return self.uow.usuarios.update(user_id, **kwargs)

    def revocar_refresh_tokens(self, user_id: int) -> None:
        """
        Revocar todos los refresh tokens del usuario.

        Usa el TokenService que almacena refresh tokens en memoria.
        Formato del store: {token: {"user_id": int, "exp": datetime}}
        """
        from backend.core.security import TokenService
        # Eliminar todos los refresh tokens del usuario del store in-memory
        tokens_a_revocar = [
            token for token, data in TokenService._refresh_token_store.items()
            if data.get("user_id") == user_id
        ]
        for token in tokens_a_revocar:
            del TokenService._refresh_token_store[token]
