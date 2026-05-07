## ADDED Requirements

### Requirement: Rate Limiting on Login Endpoint
The system SHALL implement rate limiting on `/auth/login` to protect against brute-force attacks. The limit SHALL be 5 failed login attempts per 15 minutes per client IP address. After exceeding the limit, subsequent requests SHALL return error 429 (Too Many Requests).

#### Scenario: Successful login within limit
- **WHEN** a user makes up to 5 login attempts from IP 192.168.1.1 within 15 minutes and succeeds
- **THEN** the request succeeds with 200 OK and token response

#### Scenario: Exceeded rate limit
- **WHEN** a user makes 6 requests to `/auth/login` from the same IP within 15 minutes
- **THEN** the 6th request returns error 429 with message "Rate limit exceeded: 5 attempts per 15 minutes"

#### Scenario: Rate limit reset after time window
- **WHEN** 15 minutes pass after the first request from an IP
- **THEN** the attempt counter resets and the user can attempt login again

### Requirement: Failed vs Successful Attempts
The rate limiting logic SHALL count all login attempts (both successful and failed) equally. Failed attempts do NOT reset the counter.

#### Scenario: Failed attempts increment counter
- **WHEN** a user makes 3 failed login attempts (wrong password) from an IP
- **THEN** the counter increments to 3

#### Scenario: Successful login still counts against limit
- **WHEN** a user makes 2 failed attempts, then 1 successful attempt from an IP
- **THEN** the counter is at 3; 2 more attempts allowed before hitting limit of 5

### Requirement: Rate Limit by IP Address
The system SHALL track rate limits per client IP address. Different IPs SHALL have independent counters.

#### Scenario: Different IPs have separate counters
- **WHEN** IP 192.168.1.1 makes 5 attempts and IP 192.168.1.2 makes 3 attempts within 15 minutes
- **THEN** IP 192.168.1.1 is rate-limited at 429, but IP 192.168.1.2 can continue

#### Scenario: Requests from same IP share counter
- **WHEN** user A and user B both request from the same IP (e.g., corporate network)
- **THEN** their attempts count against the same IP's counter

### Requirement: Rate Limit Response Format
When a rate limit is exceeded, the system SHALL return a 429 response with appropriate headers and message.

#### Scenario: 429 response with retry information
- **WHEN** a request is rate-limited
- **THEN** the response includes:
  - Status code: 429
  - `Retry-After` header indicating seconds until retry is allowed
  - JSON body: `{ "error": "Rate limit exceeded: 5 attempts per 15 minutes" }`

### Requirement: Slow-API Integration
The system SHALL use the slowapi library to implement rate limiting as a middleware/decorator in FastAPI. slowapi SHALL track IP-based counters and enforce limits transparently.

#### Scenario: slowapi middleware intercepts login requests
- **WHEN** a request reaches `/auth/login`
- **THEN** slowapi checks the IP counter and either allows or returns 429

#### Scenario: slowapi configuration
- **WHEN** the application starts
- **THEN** slowapi is configured with 5 requests per 15 minutes on the login endpoint
