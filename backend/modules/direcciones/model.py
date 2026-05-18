from datetime import datetime
from typing import Optional


class DireccionEntrega:
    """
    Modelo de DireccionEntrega para el sistema Food Store.

    Atributos:
        id: Identificador único (PK autoincremental gestionado por el repositorio)
        cliente_id: FK al cliente propietario (coincide con user_id del JWT)
        calle: Nombre de la calle (requerido)
        numero: Número de puerta (str para admitir "S/N", "1234 bis", etc.)
        ciudad: Ciudad (requerido)
        provincia: Provincia (requerido)
        codigo_postal: Código postal (requerido)
        piso: Piso (opcional)
        departamento: Departamento/unidad (opcional)
        referencia: Referencia o indicación adicional (opcional)
        es_predeterminada: Si es la dirección por defecto del cliente
        activo: Soft delete (True = activo)
        created_at: Timestamp de creación
        updated_at: Timestamp de última actualización
    """

    def __init__(
        self,
        id: int,
        cliente_id: int,
        calle: str,
        numero: str,
        ciudad: str,
        provincia: str,
        codigo_postal: str,
        piso: Optional[str] = None,
        departamento: Optional[str] = None,
        referencia: Optional[str] = None,
        es_predeterminada: bool = False,
        activo: bool = True,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.cliente_id = cliente_id
        self.calle = calle
        self.numero = numero
        self.ciudad = ciudad
        self.provincia = provincia
        self.codigo_postal = codigo_postal
        self.piso = piso
        self.departamento = departamento
        self.referencia = referencia
        self.es_predeterminada = es_predeterminada
        self.activo = activo
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def __repr__(self) -> str:
        return (
            f"<DireccionEntrega id={self.id} cliente_id={self.cliente_id} "
            f"calle='{self.calle}' numero='{self.numero}' activo={self.activo} "
            f"es_predeterminada={self.es_predeterminada}>"
        )

    def to_dict(self) -> dict:
        """Serializa DireccionEntrega a diccionario."""
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "calle": self.calle,
            "numero": self.numero,
            "ciudad": self.ciudad,
            "provincia": self.provincia,
            "codigo_postal": self.codigo_postal,
            "piso": self.piso,
            "departamento": self.departamento,
            "referencia": self.referencia,
            "es_predeterminada": self.es_predeterminada,
            "activo": self.activo,
            "created_at": self.created_at.isoformat() if isinstance(self.created_at, datetime) else self.created_at,
            "updated_at": self.updated_at.isoformat() if isinstance(self.updated_at, datetime) else self.updated_at,
        }
