"""
Service para operaciones de negocio de DireccionEntrega.

Responsabilidades:
- Aplicar RN-DI01: primera dirección del cliente → es_predeterminada=True forzado
- Aplicar RN-DI02: unicidad de dirección predeterminada por cliente
- Aplicar RN-DI03: ownership — solo el propietario puede operar sobre sus direcciones
- Reasignar predeterminada al eliminar (si era la predeterminada, promover la más antigua restante)

Patrón del proyecto:
- Recibe IUnitOfWork en el constructor
- Nunca llama commit() / rollback() directamente; lo hace el UoW
- Lanza DireccionNotFound (404), UnauthorizedDireccionAccess (403), ValueError (400)
"""

from typing import List, Dict, Optional
from backend.core.uow import IUnitOfWork
from .exceptions import DireccionNotFound, UnauthorizedDireccionAccess


class DireccionService:
    """
    Servicio de lógica de negocio para DireccionEntrega.
    """

    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    # ── helpers ────────────────────────────────────────────────────────────────

    def _get_or_raise(self, direccion_id: int) -> object:
        """
        Obtener dirección activa por id o lanzar DireccionNotFound.
        """
        direccion = self.uow.direcciones.get_by_id(direccion_id)
        if not direccion:
            raise DireccionNotFound(direccion_id)
        return direccion

    def _check_ownership(self, direccion, user_id: int) -> None:
        """
        Verificar que el cliente autenticado es el propietario de la dirección.
        Lanza UnauthorizedDireccionAccess si no lo es (RN-DI03).
        """
        if direccion.cliente_id != user_id:
            raise UnauthorizedDireccionAccess(direccion.id, user_id)

    # ── CRUD ───────────────────────────────────────────────────────────────────

    def create_direccion(self, user_id: int, dto) -> Dict:
        """
        Crear una nueva dirección para el cliente autenticado.

        Reglas:
        - RN-DI01: si es la primera dirección del cliente, forzar es_predeterminada=True
        - RN-DI02: si es_predeterminada=True, desmarcar las demás del cliente

        Args:
            user_id: ID del cliente autenticado (del JWT)
            dto: DireccionCreate con los campos de la dirección

        Returns:
            dict con los datos de la dirección creada
        """
        # RN-DI01: primera dirección siempre es predeterminada
        es_predeterminada = dto.es_predeterminada
        count = self.uow.direcciones.count_by_cliente(user_id)
        if count == 0:
            es_predeterminada = True

        # Crear la dirección
        direccion = self.uow.direcciones.create(
            cliente_id=user_id,
            calle=dto.calle,
            numero=dto.numero,
            ciudad=dto.ciudad,
            provincia=dto.provincia,
            codigo_postal=dto.codigo_postal,
            piso=dto.piso,
            departamento=dto.departamento,
            referencia=dto.referencia,
            es_predeterminada=es_predeterminada,
        )

        # RN-DI02: si es predeterminada, desmarcar el resto
        if es_predeterminada:
            self.uow.direcciones.set_predeterminada(direccion.id)

        self.uow.commit()
        return direccion.to_dict()

    def list_direcciones(self, user_id: int) -> List[Dict]:
        """
        Listar todas las direcciones activas del cliente autenticado.

        Args:
            user_id: ID del cliente autenticado (del JWT)

        Returns:
            lista de dicts con las direcciones activas del cliente
        """
        direcciones = self.uow.direcciones.list_by_cliente(user_id)
        return [d.to_dict() for d in direcciones]

    def update_direccion(self, user_id: int, direccion_id: int, dto) -> Dict:
        """
        Actualizar campos de una dirección del cliente autenticado.

        Reglas:
        - RN-DI03: verificar ownership antes de actualizar
        - RN-DI02: si se actualiza es_predeterminada=True, desmarcar las demás

        Args:
            user_id: ID del cliente autenticado (del JWT)
            direccion_id: ID de la dirección a actualizar
            dto: DireccionUpdate con los campos a modificar

        Returns:
            dict con los datos de la dirección actualizada
        """
        direccion = self._get_or_raise(direccion_id)
        self._check_ownership(direccion, user_id)

        # Construir kwargs solo con campos provistos (no None)
        update_data = dto.model_dump(exclude_unset=True)
        if not update_data:
            raise ValueError("No se proporcionaron campos para actualizar")

        # Si se marca como predeterminada, aplicar RN-DI02 vía set_predeterminada
        if update_data.pop("es_predeterminada", None) is True:
            self.uow.direcciones.set_predeterminada(direccion_id)
        elif "es_predeterminada" in update_data:
            # Si se envía explícitamente False, actualizar directo
            pass

        if update_data:
            self.uow.direcciones.update(direccion_id, **update_data)

        self.uow.commit()
        updated = self.uow.direcciones.get_by_id(direccion_id)
        return updated.to_dict()

    def set_predeterminada(self, user_id: int, direccion_id: int) -> Dict:
        """
        Marcar una dirección como predeterminada del cliente.

        Aplica RN-DI02: desmarca todas las demás del cliente y marca esta.

        Args:
            user_id: ID del cliente autenticado (del JWT)
            direccion_id: ID de la dirección a marcar

        Returns:
            dict con los datos de la dirección actualizada
        """
        direccion = self._get_or_raise(direccion_id)
        self._check_ownership(direccion, user_id)

        self.uow.direcciones.set_predeterminada(direccion_id)
        self.uow.commit()

        updated = self.uow.direcciones.get_by_id(direccion_id)
        return updated.to_dict()

    def delete_direccion(self, user_id: int, direccion_id: int) -> None:
        """
        Soft-delete de una dirección del cliente autenticado.

        Si la dirección eliminada era la predeterminada y quedan otras activas,
        promueve la más antigua (menor id) a predeterminada.

        Args:
            user_id: ID del cliente autenticado (del JWT)
            direccion_id: ID de la dirección a eliminar
        """
        direccion = self._get_or_raise(direccion_id)
        self._check_ownership(direccion, user_id)

        era_predeterminada = direccion.es_predeterminada

        self.uow.direcciones.soft_delete(direccion_id)

        # Si era la predeterminada, reasignar a la más antigua restante
        if era_predeterminada:
            restantes = self.uow.direcciones.list_by_cliente(user_id)
            if restantes:
                # La más antigua es la de menor id
                mas_antigua = min(restantes, key=lambda d: d.id)
                self.uow.direcciones.set_predeterminada(mas_antigua.id)

        self.uow.commit()
