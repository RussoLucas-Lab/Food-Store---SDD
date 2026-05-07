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
