"""
Services para el módulo admin.

AdminMetricasService: métricas agregadas del negocio.
AdminUsuariosService: gestión de usuarios (listado, edición, activación/desactivación).

Reglas críticas:
- NUNCA llamar session.commit() directamente — todo via self.uow.commit()
- NUNCA exponer password_hash en respuestas
- RN-RB04: nunca dejar al sistema sin ningún usuario ADMIN activo
"""

from typing import Optional, List, Dict, Any
from datetime import date
from fastapi import HTTPException, status

from backend.core.uow import IUnitOfWork
from .repository import AdminMetricasRepository, AdminUsuariosRepository


# ── Roles válidos en el catálogo simbólico ────────────────────────────────────
ROLES_CATALOGO = {"ADMIN", "STOCK", "PEDIDOS", "CLIENT"}
# Mapeo al modelo interno (auth usa "admin"/"customer")
ROLE_TO_INTERNAL = {
    "ADMIN": "admin",
    "CLIENT": "customer",
    "STOCK": "stock",
    "PEDIDOS": "pedidos",
}
INTERNAL_TO_ROLE = {v: k for k, v in ROLE_TO_INTERNAL.items()}


class AdminMetricasService:
    """
    Servicio de métricas agregadas para el panel de ADMIN.

    Orquesta el AdminMetricasRepository vía UoW.
    No realiza escrituras ni commits.
    """

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    def _validar_rango(self, desde: Optional[date], hasta: Optional[date]) -> None:
        """Validar que el rango de fechas no esté invertido."""
        if desde and hasta and desde > hasta:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="El parámetro 'desde' no puede ser posterior a 'hasta'."
            )

    def get_resumen(self) -> Dict[str, Any]:
        """
        Obtener resumen general de métricas (KPIs).

        Returns:
            dict con ventas_totales, cantidad_pedidos, cantidad_usuarios, productos_sin_stock
        """
        repo = AdminMetricasRepository(self.uow)
        return repo.get_resumen()

    def get_serie_temporal(
        self,
        desde: Optional[date],
        hasta: Optional[date],
        granularidad: str,
    ) -> List[Dict[str, Any]]:
        """
        Obtener serie temporal de ventas.

        Args:
            desde: fecha de inicio
            hasta: fecha de fin
            granularidad: 'dia', 'semana' o 'mes'

        Returns:
            Lista de dicts {periodo, monto}

        Raises:
            HTTPException 422 si el rango es invertido
        """
        self._validar_rango(desde, hasta)
        repo = AdminMetricasRepository(self.uow)
        return repo.get_serie_temporal(desde, hasta, granularidad)

    def get_top_productos(
        self,
        top: int,
        desde: Optional[date],
        hasta: Optional[date],
    ) -> List[Dict[str, Any]]:
        """
        Obtener ranking de productos más vendidos.

        Args:
            top: número de resultados
            desde: fecha de inicio
            hasta: fecha de fin

        Returns:
            Lista de dicts {producto_id, nombre, cantidad_vendida}

        Raises:
            HTTPException 422 si el rango es invertido
        """
        self._validar_rango(desde, hasta)
        repo = AdminMetricasRepository(self.uow)
        return repo.get_top_productos(top, desde, hasta)

    def get_distribucion_estados(
        self,
        desde: Optional[date],
        hasta: Optional[date],
    ) -> List[Dict[str, Any]]:
        """
        Obtener distribución de pedidos por estado.

        Args:
            desde: fecha de inicio (opcional)
            hasta: fecha de fin (opcional)

        Returns:
            Lista de dicts {estado, cantidad}

        Raises:
            HTTPException 422 si el rango es invertido
        """
        self._validar_rango(desde, hasta)
        repo = AdminMetricasRepository(self.uow)
        return repo.get_distribucion_estados(desde, hasta)


class AdminUsuariosService:
    """
    Servicio de gestión de usuarios para el panel de ADMIN.

    Orquesta vía UoW el repositorio de usuarios (auth), el catálogo de roles
    y la revocación de refresh tokens.
    """

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    def _usuario_to_dict(self, usuario) -> Dict[str, Any]:
        """
        Serializar usuario sin exponer password_hash.

        Args:
            usuario: objeto Usuario del módulo auth

        Returns:
            dict seguro (sin hash)
        """
        role_val = usuario.role.value if hasattr(usuario.role, 'value') else str(usuario.role)
        # Construir lista simbólica de roles (el modelo tiene un rol único)
        rol_simbolico = INTERNAL_TO_ROLE.get(role_val, role_val.upper())
        return {
            "id": usuario.id,
            "email": usuario.email,
            "nombre": getattr(usuario, 'nombre', None),
            "role": role_val,
            "is_active": usuario.is_active,
            "roles": [rol_simbolico],
        }

    def list_usuarios(
        self,
        page: int = 1,
        size: int = 20,
        q: Optional[str] = None,
        rol: Optional[str] = None,
        activo: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Listar usuarios con búsqueda, filtros y paginación.

        Returns:
            dict con items (sin hashes), total, page, size
        """
        repo = AdminUsuariosRepository(self.uow)
        result = repo.list_usuarios(page=page, size=size, q=q, rol=rol, activo=activo)
        result["items"] = [self._usuario_to_dict(u) for u in result["items"]]
        return result

    def update_usuario(
        self,
        user_id: int,
        current_user_id: int,
        nombre: Optional[str] = None,
        email: Optional[str] = None,
        role: Optional[str] = None,
        roles: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Editar datos y/o rol de un usuario.

        Valida:
        - El usuario existe (HTTP 404)
        - El rol (si se cambia) existe en el catálogo (HTTP 422)
        - RN-RB04: no dejar al sistema sin ADMIN (HTTP 409)
        - Al cambiar rol: revocar refresh tokens del usuario

        Args:
            user_id: ID del usuario a editar
            current_user_id: ID del admin autenticado (para validar RN-RB04)
            nombre, email, role, roles: campos a actualizar

        Returns:
            dict del usuario actualizado (sin hash)
        """
        repo = AdminUsuariosRepository(self.uow)
        usuario = repo.find_by_id(user_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con id {user_id} no encontrado."
            )

        cambio_rol = False
        nuevo_role_interno = None

        # Determinar el nuevo rol (puede venir como 'role' directo o como lista 'roles')
        nuevo_rol_simbolico = role or (roles[0] if roles else None)
        if nuevo_rol_simbolico:
            # Normalizar a mayúsculas para validar en catálogo
            nuevo_rol_upper = nuevo_rol_simbolico.upper()
            if nuevo_rol_upper not in ROLES_CATALOGO:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Rol '{nuevo_rol_simbolico}' no existe en el catálogo. "
                           f"Roles válidos: {', '.join(sorted(ROLES_CATALOGO))}"
                )
            nuevo_role_interno = ROLE_TO_INTERNAL.get(nuevo_rol_upper, nuevo_rol_simbolico.lower())
            rol_actual = usuario.role.value if hasattr(usuario.role, 'value') else str(usuario.role)
            if nuevo_role_interno != rol_actual:
                cambio_rol = True

                # Validar RN-RB04: no dejar al sistema sin ADMIN
                if rol_actual == "admin" and nuevo_role_interno != "admin":
                    admins_activos = repo.count_admins_activos()
                    if admins_activos <= 1:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="No se puede quitar el rol ADMIN al último administrador activo (RN-RB04)."
                        )

        # Construir kwargs para actualizar
        kwargs = {}
        if nombre is not None:
            kwargs["nombre"] = nombre
        if email is not None:
            kwargs["email"] = email
        if nuevo_role_interno is not None:
            from backend.modules.auth.model import RoleEnum
            try:
                kwargs["role"] = RoleEnum(nuevo_role_interno)
            except ValueError:
                # Si el rol no está en el enum original, guardarlo como string
                kwargs["role"] = nuevo_role_interno

        if kwargs:
            repo.update_usuario(user_id, **kwargs)

        # Revocar tokens si cambió el rol
        if cambio_rol:
            repo.revocar_refresh_tokens(user_id)

        self.uow.commit()

        usuario_actualizado = repo.find_by_id(user_id)
        return self._usuario_to_dict(usuario_actualizado)

    def toggle_activo(
        self,
        user_id: int,
        current_user_id: int,
        activo: bool,
    ) -> Dict[str, Any]:
        """
        Activar o desactivar la cuenta de un usuario.

        Valida:
        - No auto-desactivación (HTTP 409)
        - RN-RB04: no desactivar al último ADMIN activo (HTTP 409)
        - Al desactivar: revocar refresh tokens del usuario

        Args:
            user_id: ID del usuario a modificar
            current_user_id: ID del admin autenticado
            activo: nuevo valor de is_active

        Returns:
            dict del usuario actualizado (sin hash)
        """
        repo = AdminUsuariosRepository(self.uow)
        usuario = repo.find_by_id(user_id)
        if not usuario:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuario con id {user_id} no encontrado."
            )

        # Rechazar auto-desactivación
        if not activo and user_id == current_user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="No puedes desactivar tu propia cuenta."
            )

        # Validar RN-RB04: no desactivar al último ADMIN activo
        if not activo:
            rol_val = usuario.role.value if hasattr(usuario.role, 'value') else str(usuario.role)
            if rol_val == "admin" and usuario.is_active:
                admins_activos = repo.count_admins_activos()
                if admins_activos <= 1:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="No se puede desactivar al último administrador activo (RN-RB04)."
                    )

        repo.update_usuario(user_id, is_active=activo)

        # Revocar tokens al desactivar
        if not activo:
            repo.revocar_refresh_tokens(user_id)

        self.uow.commit()

        usuario_actualizado = repo.find_by_id(user_id)
        return self._usuario_to_dict(usuario_actualizado)
