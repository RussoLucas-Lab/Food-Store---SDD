## ADDED Requirements

### Requirement: HTTP client with axios
The system SHALL provide a centralized HTTP client for API calls.

#### Scenario: API calls include authentication token
- **WHEN** any HTTP request is made
- **THEN** the Authorization header is automatically populated with the JWT token from context/local storage

#### Scenario: 401 responses trigger token refresh
- **WHEN** backend returns 401 Unauthorized
- **THEN** HTTP client attempts to refresh the token; if successful, retries the request; if fails, redirects to login

#### Scenario: Error responses are handled consistently
- **WHEN** API request fails (4xx, 5xx)
- **THEN** error is transformed into a consistent error object with message, code, and status

#### Scenario: HTTP client is injectable
- **WHEN** components or services need to make API calls
- **THEN** they import a singleton HTTP client instance from `@/shared/services/httpClient`

### Requirement: API service factory pattern
The system SHALL support creating feature-specific API services.

#### Scenario: Features can define custom API services
- **WHEN** `src/features/auth/services/authService.ts` defines API calls for auth
- **THEN** it imports the base HTTP client and provides methods like login(), register(), logout()

#### Scenario: API services can be tested without HTTP calls
- **WHEN** unit tests run
- **THEN** HTTP client can be mocked to return test data

### Requirement: Error handling and retry logic
The system SHALL handle network errors gracefully.

#### Scenario: Network timeout is retried
- **WHEN** API request times out
- **THEN** system retries up to 3 times before returning error to user

#### Scenario: User sees error message
- **WHEN** API call fails after retries
- **THEN** error is displayed in notification/toast component
