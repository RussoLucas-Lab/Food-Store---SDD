## ADDED Requirements

### Requirement: Estructura de carpetas en capas
El sistema backend SHALL seguir una estructura de carpetas basada en arquitectura clean/hexagonal, dividiendo claramente config, models, repositories, unit-of-work y tests.

#### Scenario: Organizar carpetas base
- **WHEN** el repositorio es clonado y el backend inicializado
- **THEN** existen al menos las carpetas config/, models/, repositories/, uow/, tests/ en la raíz de backend

### Requirement: Implementación de patrón Repository y Unit of Work
El sistema backend SHALL proveer un contrato base y una implementación para Repository y Unit of Work reutilizable en todas las features siguientes.

#### Scenario: Definir contratos base
- **WHEN** se desarrollan features posteriores que requieren persistencia o transacciones
- **THEN** pueden reutilizar las interfaces/implementaciones Repository y UoW creadas en este change sin duplicación

### Requirement: Modelos base minimalistas
El sistema backend SHALL incluir la definición de modelos de dominio esenciales: categoría, ingrediente, producto, usuario, cliente, en estructura de clases/archivos aparte, sin lógica de negocio específica.

#### Scenario: Modelos creados
- **WHEN** se inspeccionan los archivos en models/
- **THEN** existe un archivo/clase para cada entidad nombrada, con atributos principales vacíos o de ejemplo

### Requirement: Configuración de entorno segura y documentada
El backend SHALL incluir mecanismo de configuración por ambiente (dev, prod, test) usando archivos .env y carpeta config/; variables sensibles NO quedan expuestas en el repo.

#### Scenario: Usar configuración por entorno
- **WHEN** se inicializa el backend en un entorno diferente
- **THEN** puede configurarse cambiando variables en .env o subcarpetas de config/ sin modificar el código fuente

### Requirement: Semilla de datos mínima para desarrollo
El backend SHALL proveer mecanismo/documentación para generar datos semilla (categorías, productos de ejemplo, usuario admin base) para local/dev/test, sin interferir con producción.

#### Scenario: Ejecutar seed de datos
- **WHEN** se corre el script/documentación de seed
- **THEN** el entorno de desarrollo queda listo para tests y pruebas manuales sin intervención externa

### Requirement: Estructura de tests lista para extensibilidad
El backend SHALL incluir carpeta y runner de test automatizado, aunque sin casos de test funcionales implementados en este change.

#### Scenario: Carpeta de test inicial
- **WHEN** se inicializan los tests backend
- **THEN** existe la carpeta tests/ y puede correrse un test runner aunque sólo con ejemplo vacío
