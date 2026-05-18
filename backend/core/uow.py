from abc import ABC, abstractmethod
from typing import Any

class IUnitOfWork(ABC):
    @abstractmethod
    def commit(self) -> None:
        pass

    @abstractmethod
    def rollback(self) -> None:
        pass

    @property
    @abstractmethod
    def repositories(self) -> Any:
        """Retorna un contenedor de repos, ej: dict o namespace."""
        pass

    @property
    @abstractmethod
    def usuarios(self):
        """Repositorio de usuarios"""
        pass

    @property
    @abstractmethod
    def categorias(self):
        """Repositorio de categorías"""
        pass

    @property
    @abstractmethod
    def ingredientes(self):
        """Repositorio de ingredientes"""
        pass

    @property
    @abstractmethod
    def productos(self):
        """Repositorio de productos"""
        pass

    @property
    @abstractmethod
    def product_ingredients(self):
        """Repositorio de relaciones producto-ingrediente"""
        pass

    @property
    @abstractmethod
    def pedidos(self):
        """Repositorio de pedidos"""
        pass

    @property
    @abstractmethod
    def detalles_pedido(self):
        """Repositorio de detalles de pedido"""
        pass

    @property
    @abstractmethod
    def historial_estado(self):
        """Repositorio de historial de estado de pedido (append-only)"""
        pass

    @property
    @abstractmethod
    def direcciones(self):
        """Repositorio de direcciones de entrega"""
        pass

    @property
    @abstractmethod
    def pagos(self):
        """Repositorio de pagos (MercadoPago)"""
        pass
