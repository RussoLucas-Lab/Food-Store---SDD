## 1. Setup & Dependencies

- [x] 1.1 Create `backend/` folder structure (routers/, schemas/, services/, middleware/)
- [x] 1.2 Add dependencies to requirements.txt: FastAPI, python-jose, passlib[bcrypt], slowapi, pydantic
- [x] 1.3 Update `.env` with: `SECRET_KEY`, `JWT_ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`, `REFRESH_TOKEN_EXPIRE_DAYS`
- [x] 1.4 Create `backend/main.py` with FastAPI app scaffold
- [x] 1.5 Integrate slowapi middleware in FastAPI app for rate limiting

## 2. Usuario Model & Repository

- [x] 2.1 Expand `models/usuario.py` with: email, password_hash, role (Enum), is_active, created_at, updated_at
- [x] 2.2 Create database migration script (or seed script) to add usuario table with correct schema
- [x] 2.3 Implement `repositories/usuario_repository.py` with methods: create(), find_by_email(), find_by_id(), update(), deactivate(), list_all()
- [x] 2.4 Integrate UsuarioRepository into Unit of Work (update `uow/` to include `usuarios` property)
- [x] 2.5 Create inmemory or PostgreSQL implementation of UsuarioRepository (match existing DB approach)

## 3. Password Security Services

- [x] 3.1 Create `backend/services/password_service.py` with:
  - `hash_password(plaintext: str) -> str` using Passlib + bcrypt
  - `verify_password(plaintext: str, hash: str) -> bool`
  - `validate_password_strength(password: str) -> list[str]` (returns list of unmet criteria)
- [x] 3.2 Unit test password_service: hash, verify, validation logic
- [x] 3.3 Ensure password never logged or exposed in errors

## 4. JWT Token Services

- [x] 4.1 Create `backend/services/token_service.py` with:
  - `create_access_token(user_id: int, email: str, role: str, expires_delta: timedelta) -> str`
  - `create_refresh_token(user_id: int, expires_delta: timedelta) -> str`
  - `decode_token(token: str) -> dict` (returns claims or raises exception if invalid)
  - `validate_token(token: str) -> bool`
- [x] 4.2 Store/track refresh tokens in-memory dict (key: token, value: {user_id, expiration}) for logout invalidation
- [x] 4.3 Unit test token service: creation, validation, expiration, tampered tokens
- [x] 4.4 Configure JWT algorithm (HS256) and secret from Settings

## 5. Pydantic Schemas

- [x] 5.1 Create `backend/schemas/auth_schema.py` with:
  - `RegisterRequest`: email, password (both validated)
  - `LoginRequest`: email, password
  - `TokenResponse`: access_token, refresh_token, token_type, expires_in
  - `RefreshRequest`: refresh_token
  - `UserOut`: id, email, role, is_active, created_at, updated_at (no password_hash)
- [x] 5.2 Add Pydantic validators for email format (RFC 5322) and password strength
- [x] 5.3 Unit test schema validation: valid inputs, invalid inputs, edge cases

## 6. Authentication Endpoints

- [x] 6.1 Create `backend/routers/auth.py` with endpoint: `POST /auth/register`
  - Validate input (email format, password strength)
  - Check for duplicate email
  - Hash password, create Usuario record via repository
  - Return UserOut + status 201
- [x] 6.2 Create endpoint: `POST /auth/login`
  - Extract email/password from request
  - Find Usuario by email
  - Verify password against hash
  - Generate access_token + refresh_token
  - Return TokenResponse + status 200
- [x] 6.3 Integrate slowapi rate limiting on `/auth/login` (5 attempts / 15 min per IP)
- [x] 6.4 Create endpoint: `POST /auth/refresh`
  - Validate refresh_token (not expired, in valid store)
  - Generate new access_token
  - Return TokenResponse
- [x] 6.5 Create endpoint: `GET /auth/me` (protected)
  - Extract JWT from Authorization header
  - Validate token
  - Return authenticated user profile (UserOut)
- [x] 6.6 Create endpoint: `POST /auth/logout` (protected)
  - Invalidate refresh_token in store
  - Return success message

## 7. JWT Middleware & Decorators

- [x] 7.1 Create `backend/middleware/jwt_middleware.py`:
  - Extract Authorization header (Bearer <token>)
  - Validate token signature, expiration, claims
  - Attach user context to request (request.user with id, email, role)
  - Return 401 if invalid
- [x] 7.2 Create `@require_role(role: str)` decorator to enforce role-based access on endpoints
  - Check request.user.role against required role
  - Return 403 if insufficient permissions
- [x] 7.3 Test middleware: valid tokens, expired tokens, tampered tokens, missing headers

## 8. Integration & Configuration

- [x] 8.1 Update `backend/main.py` to register auth router
- [x] 8.2 Add JWT middleware to FastAPI app
- [x] 8.3 Ensure JWT_ALGORITHM, SECRET_KEY loaded from Settings in config/env.py
- [x] 8.4 Add CORS configuration if needed for frontend
- [x] 8.5 Create `/health` or `/docs` public endpoints for testing

## 9. Testing

- [x] 9.1 Create `tests/test_auth_endpoints.py`:
  - Test registration: success, duplicate email, weak password
  - Test login: success, wrong password, inactive user
  - Test token refresh: valid token, expired token
  - Test GET /auth/me: valid token, invalid token
  - Test logout: invalidates refresh token
- [x] 9.2 Create `tests/test_password_service.py`:
  - Test hash/verify round trip
  - Test password strength validation (all edge cases)
  - Test hashes are unique (different salts)
- [x] 9.3 Create `tests/test_token_service.py`:
  - Test JWT creation and decoding
  - Test expiration validation
  - Test tampered token rejection
  - Test refresh token store operations
- [x] 9.4 Create `tests/test_rate_limiting.py`:
  - Test 5 attempts within 15 min succeeds
  - Test 6th attempt returns 429
  - Test counter resets after 15 min
  - Test different IPs have separate counters

## 10. Documentation

- [x] 10.1 Document auth flow in README: register → login → token → use token → refresh → logout
- [x] 10.2 Add OpenAPI (Swagger) documentation with examples for each endpoint
- [x] 10.3 Document role requirements for future CRUD endpoints (marked as @require_role("admin") or @require_role("customer"))
- [x] 10.4 Add environment variable documentation (SECRET_KEY, JWT_ALGORITHM, etc.)
- [x] 10.5 Create a postman collection or curl examples for testing endpoints

## 11. Final Verification

- [ ] 11.1 All endpoint tests passing (pytest)
- [ ] 11.2 Password service tests passing
- [ ] 11.3 Token service tests passing
- [ ] 11.4 Rate limiting verified: 429 after 5 attempts
- [ ] 11.5 Manual test: register → login → get token → call /me → logout
- [ ] 11.6 Verify password_hash never appears in logs or responses
- [ ] 11.7 Run linter/formatter (if configured)
- [ ] 10.3 Document role requirements for future CRUD endpoints (marked as @require_role("admin") or @require_role("customer"))
- [ ] 10.4 Add environment variable documentation (SECRET_KEY, JWT_ALGORITHM, etc.)
- [ ] 10.5 Create a postman collection or curl examples for testing endpoints

## 11. Final Verification

- [ ] 11.1 All endpoint tests passing (pytest)
- [ ] 11.2 Password service tests passing
- [ ] 11.3 Token service tests passing
- [ ] 11.4 Rate limiting verified: 429 after 5 attempts
- [ ] 11.5 Manual test: register → login → get token → call /me → logout
- [ ] 11.6 Verify password_hash never appears in logs or responses
- [ ] 11.7 Run linter/formatter (if configured)
