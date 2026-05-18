## Context

El backend ya tiene 448 tests unitarios usando repositorios en memoria (FakeRepository). Los tests se ejecutan sin base de datos real — el UoW inyecta repos falsos que simulan el almacenamiento. Esta arquitectura es rápida y portable, pero no valida el stack real (SQLAlchemy + PostgreSQL). El módulo `productos` es el único sin tests (directorio vacío). No existe `pytest.ini` ni `pytest-cov` — no hay forma de medir ni exigir un umbral de cobertura.

Estado actual:
- 448 tests unitarios en `backend/tests/modules/`
- `backend/tests/modules/productos/` vacío (solo `__init__.py`)
- `pytest==7.4.3`, `pytest-asyncio==0.21.1` en requirements; sin `pytest-cov` ni `httpx`
- Sin `pytest.ini` — pytest corre sin configuración explícita

## Goals / Non-Goals

**Goals:**
- Agregar `pytest-cov` y `pytest.ini` con umbral ≥ 60% (`--cov-fail-under=60`)
- Completar los tests unitarios del módulo `productos` (service + endpoints + schemas)
- Implementar una suite de integración en `backend/tests/integration/` con cliente HTTP real y SQLite en memoria
- Cubrir los flujos críticos: auth, catálogo, creación de pedido, webhook de pago, transición de estados
- Agregar `Makefile` con targets `test`, `test-cov`, `test-integration`

**Non-Goals:**
- Tests de frontend (Vitest/RTL/Playwright) — fuera del scope de este change
- Tests de carga o performance
- Configurar PostgreSQL dedicado para CI — se usa SQLite para portabilidad
- Reescribir los 448 tests existentes

## Decisions

### D1: SQLite en memoria para integración

**Decisión**: Usar `sqlite:///:memory:` en la suite de integración.

**Alternativa considerada**: PostgreSQL en Docker (`pytest-docker`) — más fiel a producción pero requiere Docker en cada entorno de desarrollo y complica el CI.

**Rationale**: SQLite es suficiente para validar la lógica de routing, serialización, autenticación y FSM. Las diferencias con PostgreSQL (tipos, CTEs recursivas) son mínimas y están cubiertas por los tests unitarios que testean el repositorio directamente contra los modelos SQLModel.

**Riesgo**: Queries específicas de PostgreSQL (por ejemplo, `JSONB`, `ARRAY`) fallarían silenciosamente. Se acepta porque ningún modelo actual las usa.

### D2: httpx.AsyncClient + ASGITransport

**Decisión**: Usar `httpx.AsyncClient(transport=ASGITransport(app=app))` — sin levantar servidor real.

**Alternativa**: `fastapi.testclient.TestClient` (síncrono). No soporta endpoints `async def` correctamente con pytest-asyncio.

**Rationale**: ASGITransport permite tests asíncronos nativos, compatible con `pytest-asyncio`, y no abre puertos de red. El cliente recibe y envía requests como si fueran HTTP reales (headers, status codes, body).

### D3: Aislamiento por transacción con rollback

**Decisión**: Cada test de integración corre dentro de una transacción SQLAlchemy que se revierte al terminar (`SAVEPOINT` / `ROLLBACK`). No se recrea la BD por test.

**Alternativa**: `CREATE TABLE ... DROP TABLE` por test — más simple pero muy lento con muchas tablas.

**Rationale**: El rollback-per-test es la técnica estándar para suites de integración en SQLAlchemy. Garantiza aislamiento sin overhead de DDL. La sesión de test se inyecta al UoW mediante override de la dependencia FastAPI.

### D4: Markers pytest para segmentar suites

**Decisión**: `@pytest.mark.unit` (implícito, ya existente) y `@pytest.mark.integration` (nuevo). En `pytest.ini` se registran ambos markers.

**Rationale**: Permite correr `pytest -m "not integration"` para el ciclo rápido de desarrollo y `pytest -m integration` para CI completo. No se rompe la suite existente.

### D5: Cobertura con pytest-cov, umbral 60%

**Decisión**: `addopts = --cov=backend --cov-report=html --cov-report=term-missing --cov-fail-under=60` en `pytest.ini`.

**Alternativa**: Script ad-hoc en Makefile — menos explícito, se puede olvidar.

**Rationale**: El umbral en `pytest.ini` hace que `pytest` falle con exit code ≠ 0 si la cobertura cae bajo 60%. Esto es el criterio de la rúbrica (+10 pts). El reporte HTML va a `htmlcov/` (gitignored).

## Risks / Trade-offs

- **[Riesgo] SQLite no soporta ciertas features de PostgreSQL** → Los tests de integración cubren paths de código comunes. Las queries específicas de PG se validan con los tests unitarios de repositorio que usan el modelo en memoria.
- **[Riesgo] El UoW actual usa repositorios en memoria (no SQLAlchemy real)** → Para integración se necesita un UoW alternativo que use sesiones SQLAlchemy. Se implementa como fixture que hace override de la dependencia FastAPI, no como cambio al UoW de producción.
- **[Trade-off] SQLite vs. PostgreSQL** → Se gana portabilidad a costo de fidelidad parcial. Aceptable para el scope académico.
- **[Riesgo] httpx no está en requirements.txt** → Se agrega como dependencia de desarrollo (`httpx>=0.27`).

## Migration Plan

1. Agregar `pytest-cov` y `httpx` a `backend/requirements.txt`
2. Crear `pytest.ini` en la raíz del proyecto con la configuración acordada
3. Crear `backend/tests/modules/productos/` tests (service, endpoints, schemas)
4. Crear `backend/tests/integration/conftest.py` con fixtures de BD y cliente HTTP
5. Crear tests de integración por flujo (auth, catálogo, pedidos, pagos)
6. Crear `Makefile` con los targets definidos
7. Verificar que `pytest` pasa con cobertura ≥ 60%

## Open Questions

- ¿Se incluye coverage del código de tests en sí (excluir `backend/tests/` del reporte)? → Sí, excluir con `omit = backend/tests/*`.
- ¿El `Makefile` es para Windows o multiplataforma? → Usar sintaxis GNU Make compatible; en Windows usar `make` vía Git Bash o WSL.
