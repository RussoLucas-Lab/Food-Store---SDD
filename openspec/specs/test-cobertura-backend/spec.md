## ADDED Requirements

### Requirement: Configuración de cobertura con pytest-cov
El proyecto SHALL disponer de pytest-cov instalado y configurado en `pytest.ini` con un umbral mínimo de cobertura del 60% sobre el paquete `backend/`.

#### Scenario: pytest falla si la cobertura está bajo el umbral
- **WHEN** se ejecuta `pytest` sin flags adicionales
- **THEN** el proceso termina con exit code distinto de cero si la cobertura de `backend/` es menor al 60%

#### Scenario: pytest genera reporte HTML y terminal
- **WHEN** se ejecuta `pytest`
- **THEN** se genera el directorio `htmlcov/` con el reporte HTML y se imprime en terminal las líneas no cubiertas

#### Scenario: el directorio de tests queda excluido del reporte
- **WHEN** se ejecuta la medición de cobertura
- **THEN** los archivos en `backend/tests/` no aparecen en el reporte de cobertura

### Requirement: Tests unitarios del módulo productos — Service
El sistema SHALL contar con tests unitarios para `ProductService` que validen la lógica de negocio usando el UoW en memoria.

#### Scenario: crear producto con datos válidos
- **WHEN** se llama a `create_product` con nombre, precio, al menos una categoría y al menos un ingrediente válidos
- **THEN** el producto se almacena en el repositorio y se retorna el objeto creado

#### Scenario: crear producto sin categoría falla
- **WHEN** se llama a `create_product` sin `category_ids`
- **THEN** se lanza `ValueError` con mensaje que indica la categoría es requerida

#### Scenario: crear producto sin ingredientes falla
- **WHEN** se llama a `create_product` sin `ingredients`
- **THEN** se lanza `ValueError` con mensaje que indica que al menos un ingrediente es requerido

#### Scenario: precio negativo o cero falla
- **WHEN** se llama a `create_product` con `base_price <= 0`
- **THEN** se lanza `ValueError` con mensaje de precio inválido

#### Scenario: actualizar stock disponible
- **WHEN** se llama a `update_stock` con un delta positivo
- **THEN** el campo `stock` del producto se incrementa correctamente

#### Scenario: desactivar producto
- **WHEN** se llama a `deactivate_product` con el id de un producto activo
- **THEN** el producto queda con `disponible = False`

### Requirement: Tests unitarios del módulo productos — Endpoints
El sistema SHALL contar con tests de endpoints para el router de productos usando el cliente de tests de FastAPI.

#### Scenario: GET /api/v1/productos retorna lista de productos activos
- **WHEN** se hace GET a `/api/v1/productos`
- **THEN** se retorna HTTP 200 con un arreglo JSON de productos disponibles

#### Scenario: GET /api/v1/productos/{id} retorna producto existente
- **WHEN** se hace GET a `/api/v1/productos/{id}` con un id que existe
- **THEN** se retorna HTTP 200 con el objeto del producto

#### Scenario: GET /api/v1/productos/{id} retorna 404 para producto inexistente
- **WHEN** se hace GET a `/api/v1/productos/{id}` con un id que no existe
- **THEN** se retorna HTTP 404

#### Scenario: POST /api/v1/productos requiere autenticación admin
- **WHEN** se hace POST a `/api/v1/productos` sin token JWT válido
- **THEN** se retorna HTTP 401 o HTTP 403

#### Scenario: POST /api/v1/productos crea un producto con datos válidos
- **WHEN** se hace POST a `/api/v1/productos` con token ADMIN y payload válido
- **THEN** se retorna HTTP 201 con el producto creado

### Requirement: Makefile con targets de test
El proyecto SHALL disponer de un `Makefile` en la raíz con targets estándar para ejecutar las suites de tests.

#### Scenario: make test corre la suite unitaria
- **WHEN** se ejecuta `make test`
- **THEN** se corre `pytest backend/tests/modules/` sin la suite de integración

#### Scenario: make test-cov corre con reporte de cobertura
- **WHEN** se ejecuta `make test-cov`
- **THEN** se corre `pytest` con `--cov=backend` y se genera el reporte

#### Scenario: make test-integration corre solo pruebas de integración
- **WHEN** se ejecuta `make test-integration`
- **THEN** se corre `pytest -m integration`
