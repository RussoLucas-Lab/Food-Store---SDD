## ADDED Requirements

### Requirement: User Registration
The system SHALL allow a new user to create an account with email and password. The email must be unique across the system. Passwords must meet complexity requirements (minimum 8 characters, at least 1 uppercase, 1 digit, 1 special character). The password SHALL be hashed with bcrypt before storage.

#### Scenario: Successful registration
- **WHEN** a user submits `POST /auth/register` with valid email and password
- **THEN** a new Usuario record is created with role=`customer`, is_active=true, and returns `{ user_id, email, role }` with status 201

#### Scenario: Duplicate email registration
- **WHEN** a user attempts to register with an email that already exists
- **THEN** the system returns error 400 with message "Email already registered"

#### Scenario: Invalid password format
- **WHEN** a user submits a password that doesn't meet complexity requirements
- **THEN** the system returns error 400 with message listing unmet criteria

### Requirement: User Login
The system SHALL allow an authenticated user to login with email and password. Upon successful authentication, the system SHALL issue a JWT access_token (15 minutes) and refresh_token (7 days).

#### Scenario: Successful login
- **WHEN** a user submits `POST /auth/login` with correct email and password
- **THEN** the system verifies credentials, returns `{ access_token, refresh_token, token_type: "Bearer", expires_in: 900 }` with status 200

#### Scenario: Invalid credentials
- **WHEN** a user submits incorrect email or password
- **THEN** the system returns error 401 with message "Invalid credentials"

#### Scenario: Inactive user
- **WHEN** a user with is_active=false attempts to login
- **THEN** the system returns error 401 with message "Account disabled"

### Requirement: Token Refresh
The system SHALL allow a client to exchange a valid refresh_token for a new access_token. The refresh_token must not be expired and must be valid.

#### Scenario: Successful refresh
- **WHEN** a client submits `POST /auth/refresh` with valid refresh_token
- **THEN** the system returns a new `{ access_token, expires_in: 900 }` with status 200

#### Scenario: Expired or invalid refresh token
- **WHEN** a client submits an expired or malformed refresh_token
- **THEN** the system returns error 401 with message "Invalid or expired refresh token"

### Requirement: Get Current User
The system SHALL provide an endpoint to retrieve the authenticated user's profile. The request MUST include a valid access_token in the Authorization header.

#### Scenario: Authenticated user retrieves profile
- **WHEN** a user submits `GET /auth/me` with valid Authorization: Bearer <access_token>
- **THEN** the system returns `{ user_id, email, role, is_active }` with status 200

#### Scenario: Missing or invalid token
- **WHEN** a request to `/auth/me` lacks Authorization header or contains invalid token
- **THEN** the system returns error 401 with message "Unauthorized"

### Requirement: User Logout
The system SHALL allow an authenticated user to logout. Upon logout, the user's refresh_token becomes invalid for future refresh operations.

#### Scenario: Successful logout
- **WHEN** a user submits `POST /auth/logout` with valid access_token
- **THEN** the system invalidates the associated refresh_token and returns status 200 with message "Logged out"

#### Scenario: Logout without valid token
- **WHEN** a user attempts logout without valid token
- **THEN** the system returns error 401 with message "Unauthorized"

### Requirement: JWT Structure and Validation
The system SHALL use JWT tokens signed with HS256 algorithm. Each access_token SHALL contain claims: `sub` (user_id), `email`, `role`, `exp` (expiration timestamp), `iat` (issued-at timestamp). The system SHALL validate token signature, expiration, and claim presence before granting access.

#### Scenario: Valid JWT validation
- **WHEN** middleware validates a token from Authorization header
- **THEN** it verifies signature, checks expiration, and extracts claims successfully

#### Scenario: Expired token rejection
- **WHEN** a request includes a token with exp < current_timestamp
- **THEN** middleware rejects with 401 "Token expired"

#### Scenario: Tampered token rejection
- **WHEN** a request includes a token with invalid signature
- **THEN** middleware rejects with 401 "Invalid token"
