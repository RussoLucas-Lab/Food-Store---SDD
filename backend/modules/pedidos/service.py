"""
Service para operaciones de negocio de Pedidos.

Responsabilidades:
- Validar carrito (items, stock, dirección)
- Capturar snapshots de nombre, precio y dirección al momento de la compra
- Crear Pedido, DetallePedido y HistorialEstadoPedido dentro de una transacción
- Listar y obtener pedidos del cliente autenticado

Patrón del proyecto:
- Sync (sin async/await)
- Llama self.uow.commit() después de cada grupo de mutaciones
- Igual a backend/modules/categorias/service.py
- Lanza excepciones custom que el router mapea a HTTP
"""

import json
from typing import List, Optional
from datetime import date
from backend.core.uow import IUnitOfWork
from .model import Pedido, DetallePedido, HistorialEstadoPedido, EstadoPedidoEnum
from .schemas import CartCreateDTO
from .exceptions import (
    CartEmptyError,
    StockInsufficient,
    PedidoNotFound,
    UnauthorizedPedidoAccess,
    DireccionNotFound,
    TransicionInvalida,
    RolNoAutorizadoParaTransicion,
)


# ── FSM: mapa de transiciones manuales ─────────────────────────────────────────
# PENDIENTE→CONFIRMADO se omite deliberadamente (es exclusivamente automática, D2).
TRANSICIONES = {
    EstadoPedidoEnum.PENDIENTE:      {EstadoPedidoEnum.CANCELADO},
    EstadoPedidoEnum.CONFIRMADO:     {EstadoPedidoEnum.EN_PREPARACION, EstadoPedidoEnum.CANCELADO},
    EstadoPedidoEnum.EN_PREPARACION: {EstadoPedidoEnum.EN_CAMINO, EstadoPedidoEnum.CANCELADO},
    EstadoPedidoEnum.EN_CAMINO:      {EstadoPedidoEnum.ENTREGADO},
    EstadoPedidoEnum.ENTREGADO:      set(),   # terminal
    EstadoPedidoEnum.CANCELADO:      set(),   # terminal
}

# ── FSM: mapa de autorización rol→transición (D3) ──────────────────────────────
# Clave: (estado_actual, estado_destino), Valor: set de roles autorizados.
# CLIENT tiene restricción adicional de ownership (validada en advance_estado).
AUTORIZACION_TRANSICION = {
    (EstadoPedidoEnum.PENDIENTE,      EstadoPedidoEnum.CANCELADO):       {"CLIENT", "PEDIDOS", "ADMIN"},
    (EstadoPedidoEnum.CONFIRMADO,     EstadoPedidoEnum.EN_PREPARACION):  {"PEDIDOS", "ADMIN"},
    (EstadoPedidoEnum.CONFIRMADO,     EstadoPedidoEnum.CANCELADO):       {"PEDIDOS", "ADMIN"},
    (EstadoPedidoEnum.EN_PREPARACION, EstadoPedidoEnum.EN_CAMINO):       {"PEDIDOS", "ADMIN"},
    (EstadoPedidoEnum.EN_PREPARACION, EstadoPedidoEnum.CANCELADO):       {"ADMIN"},
    (EstadoPedidoEnum.EN_CAMINO,      EstadoPedidoEnum.ENTREGADO):       {"PEDIDOS", "ADMIN"},
}

# Estados desde los que el stock ya fue decrementado → hay que restaurar al cancelar
ESTADOS_CON_STOCK_DECREMENTADO = {
    EstadoPedidoEnum.CONFIRMADO,
    EstadoPedidoEnum.EN_PREPARACION,
}


class PedidoService:
    """
    Servicio de lógica de negocio para Pedidos.

    Orquesta la creación de pedidos validando stock, capturando snapshots
    y registrando el historial inicial. Gestiona el acceso a pedidos por
    cliente autenticado.
    """

    def __init__(self, uow: IUnitOfWork):
        """
        Inicializar servicio.

        Args:
            uow: Unit of Work para acceso a repositorios
        """
        self.uow = uow

    def create_order(self, cliente_id: int, carrito_dto: CartCreateDTO) -> dict:
        """
        Crear un nuevo pedido desde el carrito.

        Flujo:
        1. Validar que el carrito no esté vacío
        2. Validar stock y capturar snapshots de nombre/precio por item
        3. Validar y capturar snapshot de dirección del cliente
        4. Calcular total
        5. Crear Pedido, DetallePedido(s), HistorialEstadoPedido inicial
        6. Commit y retornar dict del pedido

        Args:
            cliente_id: ID del cliente autenticado
            carrito_dto: DTO con los items del carrito y dirección

        Returns:
            dict con datos del pedido creado

        Raises:
            CartEmptyError: si el carrito está vacío
            ValueError: si un producto no existe
            StockInsufficient: si no hay stock suficiente
            DireccionNotFound: si la dirección no existe o no pertenece al cliente
        """
        # 1. Validar que el carrito no esté vacío
        if not carrito_dto.items:
            raise CartEmptyError()

        # 2. Validar stock y capturar snapshots
        detalles_data = []
        for item in carrito_dto.items:
            producto = self.uow.productos.find_by_id(item.producto_id)
            if not producto:
                raise ValueError(f"Producto {item.producto_id} no encontrado")

            # Obtener stock disponible (el modelo Product usa calculate_available_stock)
            stock_disponible = getattr(producto, "stock", None)
            if stock_disponible is None:
                # Intentar con calculate_available_stock si el modelo lo tiene
                if hasattr(producto, "calculate_available_stock"):
                    stock_disponible = producto.calculate_available_stock()
                else:
                    stock_disponible = 9999  # Sin restricción si no hay campo de stock

            if stock_disponible < item.cantidad:
                raise StockInsufficient(
                    f"Stock insuficiente para '{getattr(producto, 'nombre', str(item.producto_id))}'. "
                    f"Disponible: {stock_disponible}, solicitado: {item.cantidad}"
                )

            detalles_data.append({
                "producto_id": item.producto_id,
                "nombre_snapshot": getattr(producto, "nombre", str(item.producto_id)),
                "precio_snapshot": getattr(producto, "base_price", getattr(producto, "precio", 0.0)),
                "cantidad": item.cantidad,
                "personalizacion": item.personalizacion.excluidos,
            })

        # 3. Validar y capturar snapshot de dirección
        # El modelo actual de Cliente tiene una dirección string por cliente.
        # Buscamos el cliente y usamos su dirección como snapshot.
        cliente = self.uow.clientes.find_by_id(cliente_id)
        if not cliente:
            raise DireccionNotFound(carrito_dto.direccion_id)

        # Construir el snapshot de dirección como JSON
        direccion_snapshot = json.dumps({
            "cliente_id": cliente.id,
            "nombre": cliente.nombre,
            "direccion": cliente.direccion,
            "telefono": cliente.telefono or "",
        }, ensure_ascii=False)

        # 4. Calcular total
        total = sum(d["cantidad"] * d["precio_snapshot"] for d in detalles_data)

        # 5. Crear el Pedido
        pedido = Pedido(
            cliente_id=cliente_id,
            estado=EstadoPedidoEnum.PENDIENTE,
            direccion_snapshot=direccion_snapshot,
            total=total,
            costo_envio=0.0,  # Sin costo de envío en esta versión
        )
        pedido = self.uow.pedidos.create(pedido)

        # 6. Crear DetallePedido (con snapshots — inmutables)
        for d in detalles_data:
            detalle = DetallePedido(
                pedido_id=pedido.id,
                producto_id=d["producto_id"],
                nombre_snapshot=d["nombre_snapshot"],
                precio_snapshot=d["precio_snapshot"],
                cantidad=d["cantidad"],
                personalizacion=d["personalizacion"],
            )
            self.uow.detalles_pedido.create(detalle)

        # 7. Registrar historial inicial (append-only, estado_anterior=None)
        historial = HistorialEstadoPedido(
            pedido_id=pedido.id,
            estado_anterior=None,
            estado_nuevo=EstadoPedidoEnum.PENDIENTE,
            usuario_id=cliente_id,
            observacion="Pedido creado",
        )
        self.uow.historial_estado.create(historial)

        self.uow.commit()
        return pedido.to_dict()

    def list_orders(self, cliente_id: int, skip: int = 0, limit: int = 10) -> List[dict]:
        """
        Listar pedidos del cliente autenticado con paginación.

        Args:
            cliente_id: ID del cliente autenticado
            skip: registros a saltar
            limit: máximo de registros

        Returns:
            Lista de dicts con resumen de cada pedido
        """
        pedidos = self.uow.pedidos.list_by_cliente(cliente_id, skip=skip, limit=limit)
        return [p.to_dict() for p in pedidos]

    def advance_estado(
        self,
        pedido_id: int,
        nuevo_estado_str: str,
        usuario_id: int,
        rol: str,
        motivo: Optional[str] = None,
    ) -> dict:
        """
        Avanzar el estado de un pedido aplicando las reglas de la FSM.

        Flujo:
        1. Validar que el pedido exista.
        2. Validar que nuevo_estado sea un valor válido del enum.
        3. Validar que la transición sea permitida (TRANSICIONES).
        4. Validar que el rol esté autorizado para esa transición (AUTORIZACION_TRANSICION).
        5. Si el rol es CLIENT, validar ownership del pedido.
        6. Si la transición lleva a CANCELADO y el estado origen tiene stock decrementado,
           restaurar stock de todos los detalles.
        7. Actualizar estado del pedido.
        8. Insertar registro en HistorialEstadoPedido (append-only).
        9. uow.commit() único al final.

        Args:
            pedido_id: ID del pedido a avanzar
            nuevo_estado_str: Nombre del estado destino (e.g. "EN_PREPARACION")
            usuario_id: ID del usuario autenticado
            rol: Rol del usuario (e.g. "CLIENT", "PEDIDOS", "ADMIN")
            motivo: Motivo del cambio (obligatorio al cancelar, ya validado por schema)

        Returns:
            dict con el pedido actualizado

        Raises:
            PedidoNotFound: pedido no existe
            TransicionInvalida: transición no permitida por la FSM
            RolNoAutorizadoParaTransicion: rol sin permiso para esa transición
            UnauthorizedPedidoAccess: CLIENT intenta operar pedido ajeno
            ValueError: nuevo_estado no es un valor válido del enum
        """
        # 1. Validar existencia del pedido
        pedido = self.uow.pedidos.get_by_id(pedido_id)
        if not pedido:
            raise PedidoNotFound(pedido_id)

        # 2. Validar que nuevo_estado sea un estado válido del enum
        try:
            nuevo_estado = EstadoPedidoEnum(nuevo_estado_str)
        except ValueError:
            raise ValueError(f"Estado '{nuevo_estado_str}' no es válido.")

        estado_actual = pedido.estado

        # 3. Validar transición en el mapa FSM
        destinos_validos = TRANSICIONES.get(estado_actual, set())
        if nuevo_estado not in destinos_validos:
            raise TransicionInvalida(estado_actual.value, nuevo_estado.value)

        # 4. Validar autorización del rol para esta transición
        clave = (estado_actual, nuevo_estado)
        roles_autorizados = AUTORIZACION_TRANSICION.get(clave, set())
        if rol not in roles_autorizados:
            raise RolNoAutorizadoParaTransicion(rol, estado_actual.value, nuevo_estado.value)

        # 5. Si CLIENT, validar ownership
        if rol == "CLIENT" and pedido.cliente_id != usuario_id:
            raise UnauthorizedPedidoAccess(
                "No estás autorizado para modificar este pedido."
            )

        # 6. Restaurar stock si corresponde (D5)
        if nuevo_estado == EstadoPedidoEnum.CANCELADO and estado_actual in ESTADOS_CON_STOCK_DECREMENTADO:
            detalles = self.uow.detalles_pedido.list_by_pedido(pedido_id)
            for detalle in detalles:
                self.uow.productos.restore_stock(detalle.producto_id, detalle.cantidad)

        # 7. Actualizar estado del pedido
        self.uow.pedidos.update_estado(pedido_id, nuevo_estado)

        # 8. Registrar en historial (append-only, D6)
        observacion = motivo or f"Transición de estado: {estado_actual.value} → {nuevo_estado.value}"
        historial = HistorialEstadoPedido(
            pedido_id=pedido_id,
            estado_anterior=estado_actual,
            estado_nuevo=nuevo_estado,
            usuario_id=usuario_id,
            observacion=observacion,
        )
        self.uow.historial_estado.create(historial)

        # 9. Commit único
        self.uow.commit()

        # Retornar pedido actualizado
        pedido_actualizado = self.uow.pedidos.get_by_id(pedido_id)
        return pedido_actualizado.to_dict()

    def list_gestion(
        self,
        estado: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[dict]:
        """
        Listar todos los pedidos del sistema con filtros opcionales (para gestores).

        Args:
            estado: filtrar por estado (e.g. "CONFIRMADO")
            fecha_desde: fecha mínima de creación (inclusive)
            fecha_hasta: fecha máxima de creación (inclusive)
            skip: registros a saltar
            limit: máximo de registros

        Returns:
            Lista de dicts con resumen de cada pedido
        """
        pedidos = self.uow.pedidos.list_all_filtered(
            estado=estado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            skip=skip,
            limit=limit,
        )
        return [p.to_dict() for p in pedidos]

    def get_order_detail(self, pedido_id: int, cliente_id: int, rol: str = "CLIENT") -> dict:
        """
        Obtener detalle completo de un pedido.

        Si el rol es PEDIDOS o ADMIN, omite la validación de ownership (D8).
        Si el rol es CLIENT, valida que el pedido pertenezca al cliente.

        Args:
            pedido_id: ID del pedido a obtener
            cliente_id: ID del usuario autenticado
            rol: Rol del usuario ("CLIENT", "PEDIDOS", "ADMIN")

        Returns:
            dict con pedido + detalles + historial

        Raises:
            PedidoNotFound: si el pedido no existe
            UnauthorizedPedidoAccess: si CLIENT intenta ver un pedido ajeno
        """
        pedido = self.uow.pedidos.get_by_id(pedido_id)
        if not pedido:
            raise PedidoNotFound(pedido_id)
        # Gestores (PEDIDOS, ADMIN) pueden ver cualquier pedido; CLIENT solo el propio
        if rol not in ("PEDIDOS", "ADMIN") and pedido.cliente_id != cliente_id:
            raise UnauthorizedPedidoAccess()

        detalles = self.uow.detalles_pedido.list_by_pedido(pedido_id)
        historial = self.uow.historial_estado.list_by_pedido(pedido_id)

        result = pedido.to_dict()

        # Parsear direccion_snapshot de JSON a dict para la response
        try:
            result["direccion_snapshot"] = json.loads(result["direccion_snapshot"])
        except (json.JSONDecodeError, TypeError):
            result["direccion_snapshot"] = {"raw": result.get("direccion_snapshot", "")}

        result["detalles"] = [d.to_dict() for d in detalles]
        result["historial"] = [h.to_dict() for h in historial]
        return result
