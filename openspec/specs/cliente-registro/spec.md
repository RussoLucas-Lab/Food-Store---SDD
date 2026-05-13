# cliente-registro Specification

## Purpose
TBD - created by archiving change cliente-crud. Update Purpose after archive.
## Requirements
### Requirement: Create a new client
The system SHALL allow authorized users (ADMIN role) to create new clients with validated data. All required fields must be present and email must be unique across the system.

#### Scenario: Admin successfully creates a new client
- **WHEN** ADMIN sends POST /clientes with valid name, email, phone, address
- **THEN** client is created, assigned unique ID, marked as active, and returned with 201 Created

#### Scenario: Email already exists
- **WHEN** ADMIN sends POST /clientes with email that already exists in active clients
- **THEN** system returns 409 Conflict with error message "Email already registered"

#### Scenario: Required field missing
- **WHEN** ADMIN sends POST /clientes missing required field (name or email)
- **THEN** system returns 400 Bad Request with validation error

#### Scenario: Invalid email format
- **WHEN** ADMIN sends POST /clientes with malformed email (e.g., "not-an-email")
- **THEN** system returns 400 Bad Request with validation error

#### Scenario: Non-admin user attempts to create client
- **WHEN** USER role sends POST /clientes with valid data
- **THEN** system returns 403 Forbidden

#### Scenario: Unauthenticated user attempts to create client
- **WHEN** request sent without auth token to POST /clientes
- **THEN** system returns 401 Unauthorized

