# cliente-edicion Specification

## Purpose
TBD - created by archiving change cliente-crud. Update Purpose after archive.
## Requirements
### Requirement: Edit client information
The system SHALL allow ADMIN users to edit any client's data, and USER users to edit only their own client data. Email must remain unique after edit.

#### Scenario: Admin edits any client's data
- **WHEN** ADMIN sends PATCH /clientes/{id} with updated fields (name, phone, address)
- **THEN** client data is updated and returns 200 OK with updated client

#### Scenario: User edits own client data
- **WHEN** USER (authenticated) sends PATCH /clientes/{ownId} with updated fields
- **THEN** user's client data is updated and returns 200 OK

#### Scenario: User attempts to edit another client
- **WHEN** USER sends PATCH /clientes/{otherId} where otherId != ownId
- **THEN** system returns 403 Forbidden

#### Scenario: Email change causes conflict
- **WHEN** ADMIN sends PATCH /clientes/{id} with email already used by another client
- **THEN** system returns 409 Conflict with error message "Email already in use"

#### Scenario: Client ID not found
- **WHEN** ADMIN sends PATCH /clientes/{invalidId}
- **THEN** system returns 404 Not Found

#### Scenario: Partial update with invalid data
- **WHEN** user sends PATCH /clientes/{id} with invalid phone format (non-numeric where required)
- **THEN** system returns 400 Bad Request with validation error

