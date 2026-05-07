## ADDED Requirements

### Requirement: Listar categorías con paginación
El sistema SHALL permitir paginar listados de categorías usando parámetros `skip` y `limit`. El parámetro `skip` especifica cuántos registros saltar (default 0), `limit` especifica cuántos devolver (default 20, máximo 100). Solo se incluyen categorías activas.

#### Scenario: Listar categorías con skip y limit
- **WHEN** un usuario envía `GET /categorias?skip=20&limit=10`
- **THEN** el sistema devuelve 200 con 10 categorías activas a partir del registro 20, en orden ascendente por id

#### Scenario: Listar categorías sin parámetros (defaults)
- **WHEN** un usuario envía `GET /categorias` sin parámetros
- **THEN** el sistema devuelve 200 con las primeras 20 categorías activas

#### Scenario: Limit exceede máximo permitido
- **WHEN** un usuario envía `GET /categorias?limit=200` (máximo permitido es 100)
- **THEN** el sistema devuelve 200 pero limita el resultado a 100 registros (o rechaza con 422 dependiendo implementación)

#### Scenario: Skip o limit negativo
- **WHEN** un usuario envía `GET /categorias?skip=-1` o `limit=-5`
- **THEN** el sistema rechaza con 422 indicando "skip y limit deben ser mayores o iguales a 0"

### Requirement: Filtrar categorías por estado
El sistema SHALL permitir filtrar categorías por estado (`is_active`). Por defecto, solo se devuelven activas. Un parámetro opcional `include_inactive` permite a admins ver también inactivas.

#### Scenario: Listar solo categorías activas (default)
- **WHEN** un usuario envía `GET /categorias`
- **THEN** solo se devuelven categorías con `is_active = true`

#### Scenario: Admin solicita incluir inactivas
- **WHEN** un admin envía `GET /categorias?include_inactive=true`
- **THEN** el sistema devuelve categorías activas e inactivas

#### Scenario: Cliente intenta ver inactivas
- **WHEN** un cliente intenta enviar `GET /categorias?include_inactive=true`
- **THEN** el sistema rechaza con 403 Forbidden, o ignora el parámetro y devuelve solo activas

### Requirement: Ordenar categorías
El sistema SHALL devolver categorías ordenadas de forma predecible. Por defecto se ordenan por `id` ascendente, pero se permite especificar ordenamiento por `nombre` o `created_at`.

#### Scenario: Listar ordenadas por nombre (alphabetical)
- **WHEN** un usuario envía `GET /categorias?sort=nombre`
- **THEN** el sistema devuelve categorías ordenadas alfabéticamente por nombre (A-Z)

#### Scenario: Listar ordenadas por fecha de creación descendente
- **WHEN** un usuario envía `GET /categorias?sort=created_at&order=desc`
- **THEN** el sistema devuelve categorías más recientes primero

#### Scenario: Ordenamiento por field inválido
- **WHEN** un usuario envía `GET /categorias?sort=campo_inexistente`
- **THEN** el sistema rechaza con 422 indicando "sort debe ser: id, nombre, o created_at"
