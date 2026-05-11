## ADDED Requirements

### Requirement: Soft-delete clients
The system SHALL allow ADMIN users to mark clients as inactive (soft-delete). Soft-deleted clients are preserved in the database for historical integrity, especially for referenced orders.

#### Scenario: Admin soft-deletes a client
- **WHEN** ADMIN sends DELETE /clientes/{id}
- **THEN** client is marked as inactive (activo = false) and returns 204 No Content

#### Scenario: Soft-deleted client is excluded from active lists
- **WHEN** client is soft-deleted and ADMIN lists active clients
- **THEN** deleted client does NOT appear in response

#### Scenario: Attempt to delete non-existent client
- **WHEN** ADMIN sends DELETE /clientes/{invalidId}
- **THEN** system returns 404 Not Found

#### Scenario: Non-admin attempts to delete client
- **WHEN** USER sends DELETE /clientes/{id}
- **THEN** system returns 403 Forbidden

#### Scenario: Deleted client data is preserved for audit
- **WHEN** client is soft-deleted
- **THEN** original client record remains in database with unchanged data except activo flag

#### Scenario: Reactivate a soft-deleted client
- **WHEN** ADMIN sends PATCH /clientes/{id}/reactivar
- **THEN** client is marked as active (activo = true) and returns 200 OK with reactivated client
