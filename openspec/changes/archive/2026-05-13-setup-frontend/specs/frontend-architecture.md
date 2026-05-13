## ADDED Requirements

### Requirement: Feature-slice architecture
The system SHALL organize code into feature modules using feature-slice architecture.

#### Scenario: Each feature has its own folder
- **WHEN** developer inspects `src/features/`
- **THEN** each major feature (auth, productos, clientes, etc.) has its own folder with `components/`, `pages/`, `hooks/`, and `services/` subdirectories

#### Scenario: Shared components are centralized
- **WHEN** developer needs a reusable component (Button, Input, Card)
- **THEN** it is located in `src/shared/components/` and imported from there

### Requirement: Atomic design pattern
The system SHALL use atomic design (atoms, molecules, organisms) for component hierarchy.

#### Scenario: Atoms are basic building blocks
- **WHEN** developer creates a Button or Input component
- **THEN** it lives in `src/shared/components/atoms/` and has no dependencies on business logic

#### Scenario: Molecules compose atoms
- **WHEN** developer creates a FormField (Label + Input)
- **THEN** it lives in `src/shared/components/molecules/` and imports from atoms

#### Scenario: Organisms compose molecules
- **WHEN** developer creates a Layout or Header
- **THEN** it lives in `src/shared/components/organisms/` and imports from molecules

### Requirement: Consistent folder structure
The system SHALL enforce a predictable structure across all features.

#### Scenario: All features follow the same pattern
- **WHEN** developer adds a new feature folder
- **THEN** it contains `components/`, `pages/`, `hooks/`, `services/`, and `index.ts` (barrel exports)

#### Scenario: Imports are clean
- **WHEN** code imports from a feature
- **THEN** it uses `from '@/features/auth'` or `from '@/features/auth/components'`, not deep nested paths
