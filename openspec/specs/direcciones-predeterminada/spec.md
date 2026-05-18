# direcciones-predeterminada Specification

## Purpose
TBD - created by archiving change direcciones-entrega. Update Purpose after archive.
## Requirements
### Requirement: Primera dirección es predeterminada automáticamente

El sistema SHALL marcar como predeterminada la primera dirección de entrega que un cliente crea, sin que el cliente deba indicarlo explícitamente (RN-DI01).

#### Scenario: Primera dirección creada

- **WHEN** un cliente sin direcciones registradas crea su primera dirección de entrega
- **THEN** el sistema marca esa dirección con `es_predeterminada = true`

#### Scenario: Direcciones posteriores no son predeterminadas por defecto

- **WHEN** un cliente que ya tiene al menos una dirección crea una nueva sin solicitar que sea predeterminada
- **THEN** el sistema crea la nueva dirección con `es_predeterminada = false` y mantiene la predeterminada anterior

### Requirement: Solo una dirección predeterminada por cliente

El sistema SHALL garantizar que como máximo una dirección de entrega esté marcada como predeterminada por cliente en todo momento (RN-DI02).

#### Scenario: Marcar otra dirección como predeterminada

- **WHEN** un cliente con varias direcciones marca una dirección no predeterminada como predeterminada vía `PUT /api/v1/clientes/me/direcciones/{id}/predeterminada`
- **THEN** el sistema marca esa dirección como predeterminada y desmarca automáticamente la que era predeterminada anteriormente

#### Scenario: Crear dirección solicitando que sea predeterminada

- **WHEN** un cliente con direcciones existentes crea una nueva dirección indicando que sea predeterminada
- **THEN** el sistema marca la nueva dirección como predeterminada y desmarca la predeterminada anterior

### Requirement: Reasignación de predeterminada al eliminar

El sistema SHALL reasignar la dirección predeterminada cuando se elimina la dirección que tenía ese rol, de modo que el cliente nunca quede con direcciones activas pero sin predeterminada.

#### Scenario: Eliminar la dirección predeterminada con otras direcciones disponibles

- **WHEN** un cliente elimina su dirección predeterminada y aún conserva otras direcciones activas
- **THEN** el sistema marca como predeterminada otra de las direcciones activas restantes

#### Scenario: Eliminar la única dirección

- **WHEN** un cliente elimina su única dirección de entrega
- **THEN** el sistema completa la eliminación y el cliente queda sin direcciones, sin predeterminada pendiente

