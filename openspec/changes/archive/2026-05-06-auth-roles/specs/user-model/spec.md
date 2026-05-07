## MODIFIED Requirements

### Requirement: Usuario Entity Structure
The Usuario model SHALL contain the following attributes:
- `id`: Integer, primary key, auto-generated
- `email`: String, unique, not nullable, RFC 5322 compliant format
- `password_hash`: String (bcrypt hash), not nullable, min 60 characters
- `role`: Enum ("admin", "customer"), not nullable, default "customer"
- `is_active`: Boolean, default True, used to enable/disable accounts
- `created_at`: Timestamp (UTC), auto-generated
- `updated_at`: Timestamp (UTC), auto-updated

#### Scenario: Usuario created with all required fields
- **WHEN** a new Usuario is registered
- **THEN** it includes all required fields: id, email, password_hash, role, is_active, created_at, updated_at

#### Scenario: Email is unique
- **WHEN** attempting to register two users with the same email
- **THEN** the second registration fails with unique constraint violation

#### Scenario: Default role is customer
- **WHEN** a new Usuario is created during registration
- **THEN** role is automatically set to "customer"

#### Scenario: Default is_active is True
- **WHEN** a new Usuario is created
- **THEN** is_active is set to True (account is immediately usable)

### Requirement: Usuario Repository Contract
The Usuario repository SHALL support the following operations (via Unit of Work pattern):
- `create(email, password_hash, role)` → returns Usuario with id
- `find_by_email(email)` → returns Usuario or None
- `find_by_id(id)` → returns Usuario or None
- `update(id, **fields)` → updates Usuario record
- `deactivate(id)` → sets is_active=False
- `list_all()` → returns all Usuario records (pagination optional)

#### Scenario: Create Usuario via repository
- **WHEN** repository.create(email="user@example.com", password_hash="$2b$12$...", role="customer")
- **THEN** a new Usuario record is persisted and returned with auto-generated id

#### Scenario: Find by email
- **WHEN** repository.find_by_email("user@example.com")
- **THEN** the corresponding Usuario is returned (or None if not found)

#### Scenario: Deactivate user
- **WHEN** repository.deactivate(user_id=5)
- **THEN** the Usuario with id=5 has is_active set to False

### Requirement: Usuario Serialization
The system SHALL serialize Usuario records for API responses, excluding the password_hash field. The serialized form includes: id, email, role, is_active, created_at, updated_at.

#### Scenario: Usuario serialized for response
- **WHEN** `/auth/me` returns a Usuario
- **THEN** the JSON response includes id, email, role, is_active, created_at, but NOT password_hash

#### Scenario: Password hash never exposed
- **WHEN** any endpoint returns Usuario data
- **THEN** password_hash is never included in the response
