from uow.interfaces import IUnitOfWork
from repositories.inmemory import InMemoryRepository
from repositories.usuario_repository import InMemoryUsuarioRepository
from repositories.categoria_repository import InMemoryCategoriaRepository
from repositories.ingrediente_repository import InMemoryIngredienteRepository
from repositories.producto_repository import InMemoryProductRepository, InMemoryProductIngredientRepository

class InMemoryUnitOfWork(IUnitOfWork):
    def __init__(self):
        self._repositories = {}
        self._usuarios = InMemoryUsuarioRepository()
        self._categorias = InMemoryCategoriaRepository()
        self._ingredientes = InMemoryIngredienteRepository()
        self._productos = InMemoryProductRepository()
        self._product_ingredients = InMemoryProductIngredientRepository()
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        self.committed = False

    @property
    def repositories(self):
        return self._repositories
    
    @property
    def usuarios(self):
        """Repositorio de usuarios"""
        return self._usuarios
    
    @property
    def categorias(self):
        """Repositorio de categorías"""
        return self._categorias
    
    @property
    def ingredientes(self):
        """Repositorio de ingredientes"""
        return self._ingredientes
    
    @property
    def productos(self):
        """Repositorio de productos"""
        return self._productos
    
    @property
    def product_ingredients(self):
        """Repositorio de relaciones producto-ingrediente"""
        return self._product_ingredients
