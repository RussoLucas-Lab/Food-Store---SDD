## Why

El proyecto cuenta con 448 tests unitarios basados en repositorios en memoria, pero el módulo `productos` no tiene ningún test, no hay configuración de cobertura (pytest-cov), y no existen pruebas de integración que validen flujos críticos contra una base de datos real. La rúbrica otorga +10 pts extra si la cobertura supera el 60%, y para eso se necesita completar los gaps y medir con herramientas concretas.

## What Changes

- **Configurar pytest-cov**: agregar `pytest-cov` a `requirements.txt`, crear `pytest.ini` con umbral mínimo de cobertura del 60% y reporte HTML.
- **Tests unitarios del módulo productos**: completar el directorio vacío `backend/tests/modules/productos/` con tests de service, endpoints y schemas (el único módulo sin cobertura).
- **Tests de integración end-to-end**: nueva suite con `httpx.AsyncClient` + SQLite en memoria que valide los flujos críticos completos (auth, catálogo, pedido, pago webhook) de punta a punta contra el stack real (router → service → UoW → repositorio → BD).
- **Makefile targets**: `make test`, `make test-cov`, `make test-integration` para estandarizar la ejecución.

## Capabilities

### New Capabilities

- `test-cobertura-backend`: Configuración de pytest-cov, pytest.ini con umbral ≥ 60%, y tests unitarios del módulo productos que cierran el último gap de cobertura.
- `test-integracion-e2e`: Suite de pruebas de integración con `httpx.AsyncClient` + base de datos SQLite en memoria (Alembic aplicado al inicio). Cubre flujos end-to-end: registro/login, catálogo, creación de pedido, webhook de pago y transición de estados.

### Modified Capabilities

## Impact

- `backend/requirements.txt` — agregar `pytest-cov`, `httpx`
- `pytest.ini` (nuevo) — configuración de pytest con addopts, markers y umbral de cobertura
- `backend/tests/modules/productos/` — tests unitarios de service, endpoints y schemas
- `backend/tests/integration/` (nuevo) — suite de integración con fixtures de BD y flows
- `Makefile` (nuevo) — targets `test`, `test-cov`, `test-integration`
