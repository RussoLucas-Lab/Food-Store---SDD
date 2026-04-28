from uow.interfaces import IUnitOfWork
from repositories.inmemory import InMemoryRepository

class InMemoryUnitOfWork(IUnitOfWork):
    def __init__(self):
        self._repositories = {}
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.committed = False

    @property
    def repositories(self):
        return self._repositories
