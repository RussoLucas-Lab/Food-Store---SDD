## ADDED Requirements

### Requirement: List clients
The system SHALL provide endpoints to list clients. ADMIN can list all active clients; USER can only list their own profile (for consistency with the API structure).

#### Scenario: Admin lists all active clients
- **WHEN** ADMIN sends GET /clientes
- **THEN** system returns 200 OK with paginated list of all active clients (sorted by created_at descending)

#### Scenario: Admin filters clients by search query
- **WHEN** ADMIN sends GET /clientes/search?q=john
- **THEN** system returns 200 OK with clients matching "john" in name or email

#### Scenario: Admin retrieves specific client by ID
- **WHEN** ADMIN sends GET /clientes/{id}
- **THEN** system returns 200 OK with full client data (if active)

#### Scenario: User retrieves their own client profile
- **WHEN** USER sends GET /clientes/{ownId}
- **THEN** system returns 200 OK with their own client data

#### Scenario: User attempts to retrieve another client
- **WHEN** USER sends GET /clientes/{otherId} where otherId != ownId
- **THEN** system returns 403 Forbidden

#### Scenario: Inactive clients are excluded from list
- **WHEN** ADMIN lists all clients and database contains inactive clients
- **THEN** inactive clients do NOT appear in the response

#### Scenario: Pagination with limit and offset
- **WHEN** ADMIN sends GET /clientes?limit=10&offset=20
- **THEN** system returns 200 OK with up to 10 clients starting at offset 20
