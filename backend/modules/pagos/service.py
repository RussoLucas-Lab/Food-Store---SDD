"""
Service para operaciones de negocio de Pagos (MercadoPago).

Responsabilidades:
- Validar que el pedido existe y pertenece al cliente
- Validar que el pedido está en estado PENDIENTE
- Garantizar idempotencia: no crear pagos duplicados para el mismo pedido
- Llamar al SDK de MercadoPago para crear el pago
- Persistir el Pago en el repositorio
- Procesar confirmación atómica de pago aprobado (MP webhook)

Patrón del proyecto:
- Sync (sin async/await)
- Llama self.uow.commit() después de cada grupo de mutaciones
- El Service NUNCA llama session.commit() directamente (todo por UoW)
- Lanza excepciones custom que el router mapea a HTTP
"""

import uuid
import os
from datetime import datetime
from typing import Optional

from backend.core.uow import IUnitOfWork
from .model import Pago
from .schemas import PagoCreateDTO, PagoResponse
from .exceptions import (
    PedidoNotPendiente,
    PedidoNotFound,
    PagoAlreadyExists,
    MercadoPagoError,
)
from backend.modules.pedidos.model import EstadoPedidoEnum, HistorialEstadoPedido


class PagoService:
    """
    Servicio de lógica de negocio para Pagos.

    Orquesta la creación de pagos validando estado del pedido,
    garantizando idempotencia y procesando confirmaciones de MP webhook.
    """

    def __init__(self, uow: IUnitOfWork):
        """
        Inicializar servicio.

        Args:
            uow: Unit of Work para acceso a repositorios
        """
        self.uow = uow

    def create_payment(self, cliente_id: int, dto: PagoCreateDTO) -> PagoResponse:
        """
        Crear un nuevo pago para el pedido dado.

        Flujo:
        1. Verificar que el pedido existe y pertenece al cliente (404 si no)
        2. Verificar que el pedido está en estado PENDIENTE (400 si no)
        3. Verificar si ya existe un pago para el pedido → retornar existente (idempotencia)
        4. Generar idempotency_key y external_reference (UUID v4 cada uno)
        5. Llamar al SDK de MercadoPago para crear el pago
        6. Persistir Pago con mp_status="pending"
        7. Retornar PagoResponse

        Args:
            cliente_id: ID del cliente autenticado
            dto: Datos del pago (pedido_id, token, installments, payment_method_id)

        Returns:
            PagoResponse con datos del pago creado

        Raises:
            PedidoNotFound: si el pedido no existe o no pertenece al cliente
            PedidoNotPendiente: si el pedido no está en PENDIENTE
            MercadoPagoError: si falla la comunicación con MP SDK
        """
        # 1. Verificar que el pedido existe y pertenece al cliente
        pedido = self.uow.pedidos.get_by_id(dto.pedido_id)
        if not pedido or pedido.cliente_id != cliente_id:
            raise PedidoNotFound(dto.pedido_id)

        # 2. Verificar que el pedido está en PENDIENTE
        estado = pedido.estado
        if hasattr(estado, 'value'):
            estado_str = estado.value
        else:
            estado_str = str(estado)

        if estado_str != EstadoPedidoEnum.PENDIENTE.value:
            raise PedidoNotPendiente(dto.pedido_id, estado_str)

        # 3. Verificar idempotencia: si ya existe pago para este pedido, retornar existente
        existing_pago = self.uow.pagos.get_by_pedido_id(dto.pedido_id)
        if existing_pago:
            return PagoResponse(
                id=existing_pago.id,
                pedido_id=existing_pago.pedido_id,
                mp_payment_id=existing_pago.mp_payment_id,
                mp_status=existing_pago.mp_status,
                creado_en=existing_pago.creado_en,
            )

        # 4. Generar identificadores únicos
        idempotency_key = str(uuid.uuid4())
        external_reference = str(uuid.uuid4())

        # 5. Llamar al SDK de MercadoPago
        mp_payment_id = None
        mp_status = "pending"

        try:
            mp_access_token = os.getenv("MP_ACCESS_TOKEN", "TEST-token")
            mp_result = self._call_mercadopago_sdk(
                access_token=mp_access_token,
                token=dto.token,
                pedido_id=dto.pedido_id,
                total=pedido.total,
                installments=dto.installments,
                payment_method_id=dto.payment_method_id,
                issuer_id=dto.issuer_id,
                external_reference=external_reference,
                idempotency_key=idempotency_key,
            )
            mp_payment_id = str(mp_result.get("id", "")) or None
            mp_status = mp_result.get("status", "pending")
        except MercadoPagoError:
            raise
        except Exception as e:
            raise MercadoPagoError(f"Error al comunicarse con MercadoPago: {str(e)}")

        # 6. Persistir el Pago
        pago = Pago(
            pedido_id=dto.pedido_id,
            external_reference=external_reference,
            idempotency_key=idempotency_key,
            mp_payment_id=mp_payment_id,
            mp_status=mp_status,
        )
        pago = self.uow.pagos.create(pago)
        self.uow.commit()

        return PagoResponse(
            id=pago.id,
            pedido_id=pago.pedido_id,
            mp_payment_id=pago.mp_payment_id,
            mp_status=pago.mp_status,
            creado_en=pago.creado_en,
        )

    def _call_mercadopago_sdk(
        self,
        access_token: str,
        token: str,
        pedido_id: int,
        total: float,
        installments: int,
        payment_method_id: str,
        issuer_id: Optional[str],
        external_reference: str,
        idempotency_key: str,
    ) -> dict:
        """
        Llamar al SDK de MercadoPago para crear un pago.

        Args:
            access_token: Token de acceso de MP
            token: Token de tarjeta del browser
            pedido_id: ID del pedido
            total: Monto total del pedido
            installments: Número de cuotas
            payment_method_id: Método de pago (ej: visa)
            issuer_id: ID del banco emisor (opcional)
            external_reference: Referencia externa única
            idempotency_key: Clave de idempotencia única

        Returns:
            dict con id y status del pago creado

        Raises:
            MercadoPagoError: si falla la comunicación con MP
        """
        try:
            import mercadopago
            sdk = mercadopago.SDK(access_token)

            payment_data = {
                "transaction_amount": float(total),
                "token": token,
                "description": f"Food Store - Pedido #{pedido_id}",
                "installments": installments,
                "payment_method_id": payment_method_id,
                "external_reference": external_reference,
            }

            if issuer_id:
                payment_data["issuer_id"] = issuer_id

            request_options = mercadopago.config.RequestOptions()
            request_options.custom_headers = {
                "x-idempotency-key": idempotency_key
            }

            payment_response = sdk.payment().create(payment_data, request_options)
            response_data = payment_response.get("response", {})

            if payment_response.get("status") not in (200, 201):
                error_msg = response_data.get("message", "Error desconocido de MercadoPago")
                raise MercadoPagoError(f"MercadoPago respondió con error: {error_msg}")

            return response_data

        except MercadoPagoError:
            raise
        except ImportError:
            # SDK no instalado — modo test (retorna pending)
            return {"id": None, "status": "pending"}
        except Exception as e:
            raise MercadoPagoError(f"Error en SDK de MercadoPago: {str(e)}")

    def process_approved_payment(self, mp_payment_id: str) -> bool:
        """
        Procesar confirmación atómica de un pago aprobado por MercadoPago.

        Llamado desde el webhook cuando MP confirma un pago como 'approved'.

        Flujo (atómico — todo en una sola transacción UoW):
        1. Obtener pago por mp_payment_id
        2. Verificar idempotencia: si ya está approved, retornar True sin efecto
        3. Actualizar Pago.mp_status = "approved"
        4. Actualizar pedido.estado a CONFIRMADO
        5. Decrementar stock de cada producto en DetallePedido
        6. Insertar en HistorialEstadoPedido (append-only)
        7. uow.commit()

        Args:
            mp_payment_id: ID del pago en MercadoPago

        Returns:
            True si procesado exitosamente, False si el pago no fue encontrado

        Raises:
            Exception: si falla algún paso de la transacción atómica
        """
        # 1. Obtener el pago
        pago = self.uow.pagos.get_by_mp_payment_id(mp_payment_id)
        if not pago:
            return False

        # 2. Idempotencia: si ya está approved, retornar sin efecto
        if pago.mp_status == "approved":
            return True

        # 3. Actualizar Pago.mp_status = "approved"
        self.uow.pagos.update_status(pago.id, "approved")

        # 4. Obtener y actualizar el pedido a CONFIRMADO
        pedido = self.uow.pedidos.get_by_id(pago.pedido_id)
        if not pedido:
            raise Exception(f"Pedido {pago.pedido_id} no encontrado para el pago {pago.id}")

        estado_anterior = pedido.estado
        self.uow.pedidos.update_estado(pedido.id, EstadoPedidoEnum.CONFIRMADO)

        # 5. Decrementar stock de cada producto en DetallePedido
        detalles = self.uow.detalles_pedido.list_by_pedido(pedido.id)
        for detalle in detalles:
            producto = self.uow.productos.find_by_id(detalle.producto_id)
            if producto and hasattr(producto, 'stock'):
                nuevo_stock = max(0, producto.stock - detalle.cantidad)
                producto.stock = nuevo_stock

        # 6. Insertar en HistorialEstadoPedido (append-only)
        estado_anterior_str = (
            estado_anterior.value
            if hasattr(estado_anterior, 'value')
            else str(estado_anterior)
        )
        historial = HistorialEstadoPedido(
            pedido_id=pedido.id,
            estado_anterior=EstadoPedidoEnum(estado_anterior_str),
            estado_nuevo=EstadoPedidoEnum.CONFIRMADO,
            usuario_id=None,  # Transición automática por sistema
            observacion="Pago aprobado por MercadoPago",
        )
        self.uow.historial_estado.create(historial)

        # 7. Commit atómico
        self.uow.commit()
        return True

    def update_payment_status(self, mp_payment_id: str, new_status: str) -> bool:
        """
        Actualizar solo el estado de un pago sin avanzar el pedido.

        Usado para estados pending/in_process/rejected/cancelled del webhook.

        Args:
            mp_payment_id: ID del pago en MercadoPago
            new_status: Nuevo estado de MP

        Returns:
            True si actualizado, False si el pago no fue encontrado
        """
        pago = self.uow.pagos.get_by_mp_payment_id(mp_payment_id)
        if not pago:
            return False

        self.uow.pagos.update_status(pago.id, new_status)
        self.uow.commit()
        return True
