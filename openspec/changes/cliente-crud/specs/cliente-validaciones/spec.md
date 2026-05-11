## ADDED Requirements

### Requirement: Validate client data
The system SHALL enforce validation rules on client data at API and database levels to ensure data integrity and prevent invalid states.

#### Scenario: Email is required and must be valid format
- **WHEN** POST/PATCH /clientes is called with missing or invalid email
- **THEN** system returns 400 Bad Request with validation error "Invalid email format"

#### Scenario: Name is required and must not be empty
- **WHEN** POST /clientes is called with empty name or missing name
- **THEN** system returns 400 Bad Request with validation error "Name is required"

#### Scenario: Phone format validation (optional but when provided must be valid)
- **WHEN** POST/PATCH /clientes is called with phone that doesn't match valid format (e.g., contains letters)
- **THEN** system returns 400 Bad Request with validation error "Invalid phone format"

#### Scenario: Address is required
- **WHEN** POST /clientes is called without address
- **THEN** system returns 400 Bad Request with validation error "Address is required"

#### Scenario: Email uniqueness across active clients
- **WHEN** two separate POST requests create clients with same email simultaneously
- **THEN** only first request succeeds; second receives 409 Conflict (handled by database UNIQUE constraint + application retry)

#### Scenario: Client data length constraints
- **WHEN** POST /clientes is called with name > 255 characters or email > 254 characters
- **THEN** system returns 400 Bad Request with validation error "Field exceeds maximum length"

#### Scenario: System preserves client with no phone initially set
- **WHEN** POST /clientes is called without phone field
- **THEN** client is created successfully with phone = null
