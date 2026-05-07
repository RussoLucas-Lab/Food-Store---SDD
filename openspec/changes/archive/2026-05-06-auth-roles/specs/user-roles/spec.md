## ADDED Requirements

### Requirement: Role-Based Access Control (RBAC)
The system SHALL enforce role-based access control on protected endpoints. Each Usuario has a role: `admin` or `customer`. Protected endpoints SHALL verify the user's role and deny access if the role doesn't match the required permission.

#### Scenario: Admin accesses admin-only endpoint
- **WHEN** a user with role=`admin` submits request to an admin-only endpoint (e.g., `/api/admin/users`)
- **THEN** the endpoint processes the request and returns status 200 (or appropriate success status)

#### Scenario: Customer denied admin access
- **WHEN** a user with role=`customer` attempts to access an admin-only endpoint
- **THEN** the system returns error 403 with message "Forbidden: insufficient permissions"

#### Scenario: Admin accesses customer endpoints
- **WHEN** a user with role=`admin` accesses a customer endpoint (e.g., `/api/cart`)
- **THEN** the system allows access (admins inherit customer permissions)

### Requirement: Role Definition
The system SHALL define exactly two roles with the following permissions:

**admin**: 
- Full access to all CRUD operations (users, products, categories, ingredients, orders)
- Access to administrative endpoints and reports
- Can create, modify, delete any resource

**customer**:
- Create and manage own orders
- View own order history
- View public product catalog
- Cannot access admin endpoints
- Cannot modify other users' data

#### Scenario: Admin role capabilities
- **WHEN** a request is made with role=`admin` to any endpoint
- **THEN** the endpoint checks for admin-specific decorators and allows access

#### Scenario: Customer role capabilities
- **WHEN** a request is made with role=`customer` to non-admin endpoints (products, cart, orders)
- **THEN** the endpoint allows access; if endpoint is admin-only, returns 403

### Requirement: Endpoint-Level Authorization
The system SHALL support decorators like `@require_role("admin")` to declare role requirements on endpoints. Middleware SHALL check the user's role from JWT claims before executing the endpoint.

#### Scenario: Decorator enforcement
- **WHEN** an endpoint is decorated with `@require_role("admin")`
- **THEN** only requests with role=`admin` in JWT claims proceed; others return 403

#### Scenario: Unprotected endpoint
- **WHEN** an endpoint has no role decorator
- **THEN** all authenticated users can access it (if they pass JWT validation)

### Requirement: Role Assignment
The system SHALL assign roles upon user creation. During registration, new users are assigned role=`customer` by default. Admins can only be created via direct database operations or a separate privileged endpoint (out of scope for this change).

#### Scenario: New user gets customer role
- **WHEN** a user registers via `/auth/register`
- **THEN** the new Usuario record is created with role=`customer`

#### Scenario: Role cannot be self-assigned
- **WHEN** a user attempts to change their own role via any endpoint
- **THEN** the system returns error 403 with message "Cannot modify role" (no self-promotion)

### Requirement: Role Validation on Every Request
The system SHALL validate the user's role from JWT claims on every protected request. The role SHALL be extracted from the token, checked against the endpoint's `@require_role` decorator, and access SHALL be granted or denied accordingly.

#### Scenario: Role extracted and validated
- **WHEN** a protected endpoint receives a request with valid JWT
- **THEN** middleware extracts role from token claims and validates against endpoint requirements

#### Scenario: Missing role in token
- **WHEN** a token lacks a role claim
- **THEN** the system treats the request as unauthorized (401) or grants minimal access (dependent on endpoint design)
