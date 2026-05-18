## ADDED Requirements

### Requirement: Los datos persisten entre reinicios del servidor
El sistema SHALL almacenar todos los datos de negocio en PostgreSQL. Ninguna entidad de dominio (usuarios, productos, pedidos, pagos, etc.) SHALL perderse al reiniciar el proceso del servidor.

#### Scenario: Datos sobreviven reinicio
- **WHEN** se crea un pedido y se reinicia el servidor
- **THEN** el pedido sigue existible vía `GET /api/v1/pedidos/{id}` con el mismo estado

#### Scenario: Admin user persiste
- **WHEN** el servidor reinicia después del primer arranque
- **THEN** el usuario `admin@foodstore.com` sigue existiendo y puede autenticarse

### Requirement: Migración de schema con Alembic
El sistema SHALL gestionar el schema de la base de datos mediante Alembic. El comando `alembic upgrade head` SHALL crear todas las tablas en una BD limpia sin errores.

#### Scenario: Schema en BD limpia
- **WHEN** se ejecuta `alembic upgrade head` contra una BD PostgreSQL vacía
- **THEN** todas las tablas se crean sin errores y `alembic_version` registra la revisión actual

#### Scenario: Migración idempotente
- **WHEN** se ejecuta `alembic upgrade head` en una BD que ya tiene el schema aplicado
- **THEN** el comando termina sin errores y sin modificar la estructura existente

### Requirement: Seed idempotente sobre PostgreSQL
El sistema SHALL precargar datos iniciales (admin, seed de catálogo) en la BD real al arrancar. El seed SHALL ser idempotente.

#### Scenario: Seed en BD vacía
- **WHEN** el servidor arranca contra una BD con schema pero sin datos
- **THEN** se crea el usuario admin (`admin@foodstore.com`), categorías y productos de ejemplo

#### Scenario: Seed re-ejecutado
- **WHEN** el servidor arranca y los datos iniciales ya existen en la BD
- **THEN** no se crean duplicados; el arranque es exitoso

### Requirement: Aislamiento transaccional por request
El sistema SHALL usar una sesión de base de datos independiente por cada request HTTP. Una falla en un request NO SHALL afectar las sesiones de otros requests concurrentes.

#### Scenario: Rollback en error
- **WHEN** un request falla con excepción durante una operación de escritura
- **THEN** la transacción se hace rollback y los datos de otros requests no se ven afectados

#### Scenario: Commit en éxito
- **WHEN** un request completa exitosamente una operación de escritura
- **THEN** los datos quedan disponibles inmediatamente para requests subsiguientes
