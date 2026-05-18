## 1. Fase 1 — Crear backend/core/

- [x] 1.1 Crear directorio `backend/core/` con `__init__.py`
- [x] 1.2 Crear `backend/core/config.py` copiando lógica de `config/env.py` (Settings con dotenv)
- [x] 1.3 Crear `backend/core/uow.py` copiando interfaz `IUnitOfWork` de `uow/interfaces.py`
- [x] 1.4 Crear `backend/core/uow_inmemory.py` con `InMemoryUnitOfWork` (actualizar imports desde `uow/inmemory.py`, apuntando a los futuros `backend/modules/*/repository.py`)
- [x] 1.5 Crear `backend/core/security.py` fusionando `PasswordService` (de `backend/services/password_service.py`) y `TokenService` (de `backend/services/token_service.py`)
- [x] 1.6 Verificar que `backend/core/` importa correctamente ejecutando `python -c "from backend.core.config import Settings; from backend.core.security import PasswordService, TokenService"`

## 2. Fase 2 — Crear estructura de módulos y mover modelos

- [x] 2.1 Crear directorios `backend/modules/` y los subdirectorios: `auth/`, `categorias/`, `ingredientes/`, `productos/`, `clientes/`, `pedidos/` — cada uno con `__init__.py`
- [x] 2.2 Copiar `models/usuario.py` → `backend/modules/auth/model.py` (sin cambios de contenido)
- [x] 2.3 Copiar `models/categoria.py` → `backend/modules/categorias/model.py`
- [x] 2.4 Copiar `models/ingrediente.py` → `backend/modules/ingredientes/model.py`
- [x] 2.5 Copiar `models/producto.py` → `backend/modules/productos/model.py`
- [x] 2.6 Copiar `models/cliente.py` → `backend/modules/clientes/model.py`
- [x] 2.7 Copiar `models/pedido.py` → `backend/modules/pedidos/model.py`
- [x] 2.8 Verificar: `python -c "from backend.modules.auth.model import Usuario; from backend.modules.categorias.model import Categoria"` sin errores

## 3. Fase 3 — Mover repositorios

- [x] 3.1 Crear `backend/modules/auth/repository.py` desde `repositories/usuario_repository.py` — actualizar import de `models.usuario` → `from .model import Usuario, RoleEnum`
- [x] 3.2 Crear `backend/modules/auth/postgresql_repository.py` desde `repositories/postgresql_usuario_repository.py` — actualizar import de `repositories.usuario_repository` → `from .repository import IUsuarioRepository`
- [x] 3.3 Crear `backend/modules/categorias/repository.py` desde `repositories/categoria_repository.py` — actualizar import de `models.categoria` → `from .model import Categoria`
- [x] 3.4 Crear `backend/modules/ingredientes/repository.py` desde `repositories/ingrediente_repository.py` — actualizar import de `models.ingrediente` → `from .model import Ingrediente, UnidadMedida`
- [x] 3.5 Crear `backend/modules/productos/repository.py` desde `repositories/producto_repository.py` — actualizar import de `models.producto` → `from .model import Product, ProductIngredient`
- [x] 3.6 Crear `backend/modules/clientes/repository.py` desde `repositories/cliente_repository.py` — actualizar import de `models.cliente` → `from .model import Cliente`
- [x] 3.7 Crear `backend/modules/pedidos/repository.py` desde `repositories/pedido_repository.py` — actualizar import de `models.pedido` → `from .model import Pedido, DetallePedido, HistorialEstadoPedido, EstadoPedidoEnum`
- [x] 3.8 Actualizar `backend/core/uow_inmemory.py` para importar todos los repos desde `backend.modules.*/repository`
- [x] 3.9 Verificar: `python -c "from backend.core.uow_inmemory import InMemoryUnitOfWork; uow = InMemoryUnitOfWork()"` sin errores

## 4. Fase 4 — Mover servicios

- [x] 4.1 Crear `backend/modules/categorias/service.py` desde `backend/services/categoria_service.py` — actualizar import de `uow.interfaces` → `from backend.core.uow import IUnitOfWork`
- [x] 4.2 Crear `backend/modules/ingredientes/service.py` desde `backend/services/ingrediente_service.py` — actualizar import de `uow.interfaces` → `from backend.core.uow import IUnitOfWork`
- [x] 4.3 Crear `backend/modules/productos/service.py` desde `backend/services/product_service.py` — actualizar import de `uow.interfaces` → `from backend.core.uow import IUnitOfWork`; actualizar import de `models.producto` → `from .model import Product`
- [x] 4.4 Crear `backend/modules/clientes/service.py` desde `backend/services/cliente_service.py` — actualizar import de `uow.interfaces` → `from backend.core.uow import IUnitOfWork`
- [x] 4.5 Verificar: `python -c "from backend.modules.categorias.service import CategoryService"` sin errores

## 5. Fase 5 — Mover schemas, routers y actualizar main.py

- [x] 5.1 Crear `backend/modules/auth/schemas.py` desde `backend/schemas/auth_schema.py` — actualizar import de `backend.services.password_service` → `from backend.core.security import PasswordService`
- [x] 5.2 Crear `backend/modules/categorias/schemas.py` desde `backend/schemas/categoria_schema.py`
- [x] 5.3 Crear `backend/modules/ingredientes/schemas.py` desde `backend/schemas/ingrediente_schema.py`
- [x] 5.4 Crear `backend/modules/productos/schemas.py` desde `backend/schemas/product_schema.py`
- [x] 5.5 Crear `backend/modules/clientes/schemas.py` desde `backend/schemas/cliente_schema.py`
- [x] 5.6 Crear `backend/modules/pedidos/schemas.py` desde `backend/schemas/pedido_schema.py`
- [x] 5.7 Crear `backend/modules/pedidos/exceptions.py` desde `backend/exceptions/pedido_exceptions.py`
- [x] 5.8 Crear `backend/modules/auth/router.py` desde `backend/routers/auth.py`:
  - Actualizar imports de repos → `from .repository import InMemoryUsuarioRepository`
  - Actualizar imports de model → `from .model import RoleEnum`
  - Actualizar imports de schemas → `from .schemas import ...`
  - Reemplazar instanciación directa de repo por `Depends()` con UoW (D3 del diseño)
  - Actualizar imports de security → `from backend.core.security import PasswordService, TokenService`
- [x] 5.9 Crear `backend/modules/categorias/router.py` desde `backend/routers/categorias.py`:
  - Actualizar import de `uow.inmemory` → `from backend.core.uow_inmemory import InMemoryUnitOfWork`
  - Actualizar import de service → `from .service import CategoryService`
  - Actualizar import de schemas → `from .schemas import ...`
  - Actualizar import de middleware → `from backend.middleware.jwt_middleware import ...`
- [x] 5.10 Crear `backend/modules/ingredientes/router.py` desde `backend/routers/ingredientes.py` (mismas actualizaciones que 5.9)
- [x] 5.11 Crear `backend/modules/productos/router.py` desde `backend/routers/productos.py` (mismas actualizaciones que 5.9)
- [x] 5.12 Crear `backend/modules/clientes/router.py` desde `backend/routers/clientes.py` (mismas actualizaciones que 5.9)
- [x] 5.13 Actualizar `backend/middleware/jwt_middleware.py`: cambiar import de `backend.services.token_service` → `from backend.core.security import TokenService`
- [x] 5.14 Actualizar `backend/main.py`: reemplazar imports de `backend.routers.*` por `backend.modules.*.router`
- [x] 5.15 Verificar: `uvicorn backend.main:app --reload` arranca sin errores y `GET /` retorna 200

## 6. Fase 6 — Consolidar tests y eliminar directorios viejos

- [x] 6.1 Crear `backend/tests/` (si no existe) con `conftest.py` consolidado desde `tests/conftest.py` y `backend/tests/conftest.py`
- [x] 6.2 Crear subdirectorios `backend/tests/modules/{auth,categorias,ingredientes,productos,clientes}/`
- [x] 6.3 Mover y actualizar imports de `tests/test_auth_*.py` → `backend/tests/modules/auth/`
- [x] 6.4 Mover y actualizar imports de `tests/test_categoria_*.py` + `backend/tests/test_categoria_*.py` → `backend/tests/modules/categorias/`
- [x] 6.5 Mover y actualizar imports de `tests/test_ingrediente_*.py` + `backend/tests/test_ingrediente_*.py` → `backend/tests/modules/ingredientes/`
- [x] 6.6 Mover y actualizar imports de `backend/tests/test_cliente_*.py` → `backend/tests/modules/clientes/`
- [x] 6.7 Mover y actualizar imports de tests de password, token, jwt → `backend/tests/modules/auth/`
- [x] 6.8 Ejecutar `python -m pytest backend/tests/ -v` y verificar que todos los tests pasan
- [x] 6.9 Buscar imports residuales: `grep -r "from models\." . --include="*.py"` — debe retornar vacío
- [x] 6.10 Buscar imports residuales: `grep -r "from repositories\." . --include="*.py"` — debe retornar vacío
- [x] 6.11 Buscar imports residuales: `grep -r "from uow\." . --include="*.py"` — debe retornar vacío
- [ ] 6.12 Buscar imports residuales: `grep -r "from config\." . --include="*.py"` — debe retornar vacío
- [ ] 6.13 Eliminar directorio raíz `models/`
- [ ] 6.14 Eliminar directorio raíz `repositories/`
- [ ] 6.15 Eliminar directorio raíz `uow/`
- [ ] 6.16 Eliminar directorio raíz `config/`
- [ ] 6.17 Eliminar `backend/services/`
- [ ] 6.18 Eliminar `backend/routers/`
- [ ] 6.19 Eliminar `backend/schemas/`
- [ ] 6.20 Eliminar `backend/exceptions/`
- [ ] 6.21 Eliminar `tests/` (root) — ya consolidado en `backend/tests/`
- [ ] 6.22 Ejecutar `python -m pytest backend/tests/ -v` final — todos los tests deben pasar
- [ ] 6.23 Verificar arranque final: `uvicorn backend.main:app` levanta sin errores
