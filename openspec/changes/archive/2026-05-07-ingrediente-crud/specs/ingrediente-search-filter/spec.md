## ADDED Requirements

### Requirement: Listar todos los ingredientes con filtros opcionales
El sistema SHALL permitir a cualquier usuario listar ingredientes activos con filtros opcionales por categoría y disponibilidad. Solo se devuelven ingredientes con `is_active = true`. Se devuelve un array vacío si no hay ingredientes activos. Los resultados deben ser paginados con parámetros `skip` y `limit`.

#### Scenario: Listar todos los ingredientes
- **WHEN** un usuario envía `GET /ingredientes`
- **THEN** el sistema devuelve 200 con un array de ingredientes activos, cada uno con id, nombre, unidad_medida, cantidad_stock, stock_disponible, alerta_stock_bajo, categoria_id, is_active, created_at, updated_at

#### Scenario: Listar ingredientes cuando no existen
- **WHEN** un usuario envía `GET /ingredientes` y no hay ingredientes activos en la BD
- **THEN** el sistema devuelve 200 con un array vacío `[]`

#### Scenario: Listar ingredientes con paginación
- **WHEN** un usuario envía `GET /ingredientes?skip=20&limit=10`
- **THEN** el sistema devuelve 200 con ingredientes desde posición 20, máximo 10 elementos

#### Scenario: Listar solo ingredientes disponibles
- **WHEN** un usuario envía `GET /ingredientes?disponibles_solo=true`
- **THEN** el sistema devuelve 200 con ingredientes donde `stock_disponible > 0`

#### Scenario: Listar ingredientes que generan alerta de stock bajo
- **WHEN** un usuario envía `GET /ingredientes?alerta_stock_bajo=true`
- **THEN** el sistema devuelve 200 con ingredientes donde `alerta_stock_bajo = true`

#### Scenario: Listar ingredientes filtrados por categoría
- **WHEN** un usuario envía `GET /ingredientes?categoria_id=3`
- **THEN** el sistema devuelve 200 con ingredientes que pertenecen a categoría 3

#### Scenario: Listar ingredientes con múltiples filtros
- **WHEN** un usuario envía `GET /ingredientes?categoria_id=3&disponibles_solo=true&skip=0&limit=20`
- **THEN** el sistema devuelve 200 con ingredientes de categoría 3 que están disponibles, paginados

### Requirement: Buscar ingredientes por nombre
El sistema SHALL permitir a cualquier usuario buscar ingredientes por nombre usando búsqueda parcial (contains/ILIKE). La búsqueda es case-insensitive y solo devuelve ingredientes activos.

#### Scenario: Buscar ingrediente por nombre exacto
- **WHEN** un usuario envía `GET /ingredientes/buscar?q=Harina`
- **THEN** el sistema devuelve 200 con ingredientes cuyo nombre contiene "Harina" (case-insensitive)

#### Scenario: Buscar ingrediente por nombre parcial
- **WHEN** un usuario envía `GET /ingredientes/buscar?q=harín`
- **THEN** el sistema devuelve 200 con ingredientes cuyo nombre contiene "harín" (case-insensitive)

#### Scenario: Buscar ingrediente sin resultados
- **WHEN** un usuario envía `GET /ingredientes/buscar?q=zzzzzzzzz` (término que no existe)
- **THEN** el sistema devuelve 200 con un array vacío `[]`

#### Scenario: Buscar con término vacío
- **WHEN** un usuario envía `GET /ingredientes/buscar?q=` (query string vacío)
- **THEN** el sistema rechaza con 400 Bad Request indicando "parámetro 'q' es requerido"

### Requirement: Filtrar por unidad de medida
El sistema SHALL permitir a usuarios filtrar ingredientes por unidad de medida específica (ej: solo los que están en gramos).

#### Scenario: Listar ingredientes con unidad específica
- **WHEN** un usuario envía `GET /ingredientes?unidad_medida=gramos`
- **THEN** el sistema devuelve 200 con ingredientes donde unidad_medida es "gramos"

#### Scenario: Listar ingredientes con unidad inválida
- **WHEN** un usuario envía `GET /ingredientes?unidad_medida=toneladas` (unidad no válida)
- **THEN** el sistema rechaza con 400 Bad Request indicando "unidad_medida debe ser uno de: gramos, litros, unidades, kilos, mililitros"

### Requirement: Ordenar resultados
El sistema SHALL permitir a usuarios ordenar los resultados de listado por diferentes campos: `nombre`, `cantidad_stock`, `created_at`. El orden es ascendente por defecto, pero soporta `desc` para descendente.

#### Scenario: Listar ingredientes ordenados por nombre
- **WHEN** un usuario envía `GET /ingredientes?ordenar_por=nombre`
- **THEN** el sistema devuelve 200 con ingredientes ordenados alfabéticamente por nombre

#### Scenario: Listar ingredientes ordenados por stock descendente
- **WHEN** un usuario envía `GET /ingredientes?ordenar_por=cantidad_stock&orden=desc`
- **THEN** el sistema devuelve 200 con ingredientes ordenados por stock de mayor a menor

#### Scenario: Ordenar por campo inválido
- **WHEN** un usuario envía `GET /ingredientes?ordenar_por=campo_inexistente`
- **THEN** el sistema rechaza con 400 Bad Request indicando "ordenar_por debe ser uno de: nombre, cantidad_stock, created_at"
