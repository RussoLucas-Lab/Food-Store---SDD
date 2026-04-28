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
