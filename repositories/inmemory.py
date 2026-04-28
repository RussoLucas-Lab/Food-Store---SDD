from repositories.interfaces import IRepository
from typing import List, Optional, TypeVar, Generic

T = TypeVar('T')

class InMemoryRepository(IRepository[T], Generic[T]):
    def __init__(self):
        self._data: List[T] = []

    def add(self, obj: T) -> None:
        self._data.append(obj)

    def get(self, id) -> Optional[T]:
        for obj in self._data:
            if hasattr(obj, 'id') and getattr(obj, 'id') == id:
                return obj
        return None

    def list(self) -> List[T]:
        return list(self._data)

    def remove(self, obj: T) -> None:
        self._data.remove(obj)
