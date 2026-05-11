## ADDED Requirements

### Requirement: React Router setup
The system SHALL use React Router v6 to manage client-side routing.

#### Scenario: Routes are defined
- **WHEN** application starts
- **THEN** React Router recognizes all defined routes (/, /auth, /productos, /admin, etc.)

#### Scenario: Navigation works
- **WHEN** user clicks a link or uses programmatic navigation
- **THEN** the URL changes and the corresponding component renders

### Requirement: Protected routes
The system SHALL prevent unauthorized access to protected pages.

#### Scenario: Unauthenticated user cannot access protected route
- **WHEN** unauthenticated user navigates to `/admin`
- **THEN** user is redirected to `/login`

#### Scenario: Authenticated user with insufficient role cannot access admin
- **WHEN** USER role user navigates to `/admin`
- **THEN** user is redirected to an "Unauthorized" page or home

#### Scenario: Authenticated ADMIN can access admin route
- **WHEN** ADMIN role user navigates to `/admin`
- **THEN** admin component renders successfully

### Requirement: Route organization
The system SHALL organize routes by feature.

#### Scenario: Feature routes are nested
- **WHEN** router is defined
- **THEN** routes like `/productos/*`, `/clientes/*`, `/auth/*` are grouped by feature with shared layouts
