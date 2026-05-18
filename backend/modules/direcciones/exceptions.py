"""
Excepciones de dominio para DireccionEntrega.

El router mapea estas excepciones a respuestas HTTP:
- DireccionNotFound   → 404
- UnauthorizedDireccionAccess → 403
"""


class DireccionNotFound(Exception):
    """Raised when a DireccionEntrega with the given id does not exist or is inactive."""

    def __init__(self, direccion_id: int):
        self.direccion_id = direccion_id
        super().__init__(f"Dirección {direccion_id} no encontrada")


class UnauthorizedDireccionAccess(Exception):
    """Raised when a user tries to access a DireccionEntrega they do not own."""

    def __init__(self, direccion_id: int, user_id: int):
        self.direccion_id = direccion_id
        self.user_id = user_id
        super().__init__(
            f"El usuario {user_id} no tiene permiso para acceder a la dirección {direccion_id}"
        )
