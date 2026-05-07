## ADDED Requirements

### Requirement: Password Hashing with Bcrypt
The system SHALL hash all passwords using Passlib with bcrypt algorithm before storage. The password SHALL never be stored in plaintext. When a user registers or changes their password, the plaintext password SHALL be immediately hashed and only the hash SHALL be persisted.

#### Scenario: Password hashed on registration
- **WHEN** a user submits registration with password "MyPassword123!"
- **THEN** Passlib bcrypt hashes it to a salted hash (e.g., `$2b$12$...`), and only the hash is stored in password_hash column

#### Scenario: Password hash is irreversible
- **WHEN** an admin examines the database password_hash column
- **THEN** they see hashes like `$2b$12$...`, NOT plaintext passwords

### Requirement: Password Verification
The system SHALL use Passlib to verify login passwords against stored hashes. The verification process SHALL compare the provided plaintext password against the stored hash without ever storing or transmitting the plaintext.

#### Scenario: Correct password verification
- **WHEN** a user logs in with email and plaintext password "MyPassword123!"
- **THEN** Passlib verifies against the stored hash and returns True if match

#### Scenario: Incorrect password fails verification
- **WHEN** a user provides wrong password
- **THEN** Passlib verification returns False, login fails

#### Scenario: Password never logged
- **WHEN** a password verification occurs (success or failure)
- **THEN** the plaintext password is never written to logs; only "login attempted" is logged

### Requirement: Password Complexity Requirements
The system SHALL validate password complexity upon registration. A password is valid if it:
- Minimum 8 characters
- At least 1 uppercase letter (A-Z)
- At least 1 digit (0-9)
- At least 1 special character (!@#$%^&*)

The validation error SHALL list specific criteria that were not met.

#### Scenario: Strong password accepted
- **WHEN** a user submits password "Secure@Pass123"
- **THEN** validation passes (8+ chars, uppercase, digit, special char)

#### Scenario: Weak password rejected
- **WHEN** a user submits password "weak"
- **THEN** validation fails with error "Password too short; requires uppercase; requires digit; requires special character"

#### Scenario: Almost-strong password rejected
- **WHEN** a user submits password "Secure@pass" (missing digit)
- **THEN** validation fails with error "Password requires at least one digit"

### Requirement: No Password in Transit
The system SHALL transmit passwords only via HTTPS POST with request body (never in URL query params, headers, or logs). The password field SHALL be cleared from memory immediately after hashing and verification.

#### Scenario: Password sent via HTTPS POST
- **WHEN** client sends POST `/auth/register` with password in JSON body over HTTPS
- **THEN** the system receives it securely

#### Scenario: Password not in logs
- **WHEN** request logging occurs
- **THEN** the password field is masked or excluded from logs

#### Scenario: Password not in URL
- **WHEN** a user attempts to send password as query parameter (e.g., `/auth/login?password=...`)
- **THEN** the system rejects or ignores it; only POST body is accepted
