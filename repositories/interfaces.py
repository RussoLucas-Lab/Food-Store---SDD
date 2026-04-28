from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
    @abstractmethod
    def add(self, obj: T) -> None:
        pass

    @abstractmethod
    def get(self, id) -> Optional[T]:
        pass

    @abstractmethod
    def list(self) -> List[T]:
        pass

    @abstractmethod
    def remove(self, obj: T) -> None:
        pass
