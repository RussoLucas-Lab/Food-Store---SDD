# autenticacion Specification

## Purpose
TBD - created by archiving change cliente-crud. Update Purpose after archive.
## Requirements
### Requirement: Role-based access control for client endpoints
Endpoints that manage client data (POST, PATCH, DELETE /clientes) SHALL require authentication and role validation. ADMIN role SHALL be able to perform all operations; USER role SHALL only access their own client profile (GET and PATCH on own ID); GUEST SHALL have no access.

#### Scenario: Admin token grants full access
- **WHEN** authenticated request contains valid JWT with ADMIN role
- **THEN** user can POST, PATCH, DELETE any client, GET all clients, search

#### Scenario: User token grants limited access
- **WHEN** authenticated USER sends POST /clientes to create new client
- **THEN** system returns 403 Forbidden (only ADMIN can create)

#### Scenario: User can view and edit own profile
- **WHEN** authenticated USER sends GET or PATCH /clientes/{ownId} where {ownId} matches token's user_id
- **THEN** request succeeds and returns 200 OK

#### Scenario: User cannot access other client profiles
- **WHEN** authenticated USER sends GET or PATCH /clientes/{otherId} where {otherId} != ownId
- **THEN** system returns 403 Forbidden

#### Scenario: Missing token denies access
- **WHEN** request to /clientes endpoint is sent without Authorization header or invalid token
- **THEN** system returns 401 Unauthorized

#### Scenario: Guest cannot access client endpoints
- **WHEN** unauthenticated request is sent to any /clientes endpoint
- **THEN** system returns 401 Unauthorized

