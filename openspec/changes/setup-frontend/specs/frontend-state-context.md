## ADDED Requirements

### Requirement: AuthContext for authentication state
The system SHALL provide global authentication state.

#### Scenario: AuthContext stores user and token
- **WHEN** user is authenticated
- **THEN** AuthContext provides user object, JWT token, and role (ADMIN/USER/GUEST)

#### Scenario: Components can subscribe to auth changes
- **WHEN** component uses `useAuth()` hook
- **THEN** it receives current user, token, and login/logout functions

#### Scenario: Authentication state persists on page reload
- **WHEN** user refreshes page
- **THEN** token is restored from localStorage; user remains authenticated

### Requirement: ThemeContext for UI customization
The system SHALL support light/dark mode via ThemeContext.

#### Scenario: Theme can be toggled
- **WHEN** user clicks theme toggle button
- **THEN** entire application switches between light and dark themes; preference is saved to localStorage

#### Scenario: Components respond to theme changes
- **WHEN** theme changes
- **THEN** all components re-render with appropriate colors/styles

### Requirement: NotificationContext for user feedback
The system SHALL provide a centralized notification system.

#### Scenario: Toast notifications can be triggered
- **WHEN** code calls `notify({ message: 'Success', type: 'success' })`
- **THEN** a toast appears in corner of screen and auto-dismisses after 3 seconds

#### Scenario: Multiple notifications can stack
- **WHEN** multiple notifications are triggered rapidly
- **THEN** they stack vertically and can be dismissed individually

### Requirement: Context providers are composed
The system SHALL wrap the application with all context providers.

#### Scenario: App is wrapped with providers
- **WHEN** application renders
- **THEN** AuthProvider, ThemeProvider, and NotificationProvider wrap the root App component
