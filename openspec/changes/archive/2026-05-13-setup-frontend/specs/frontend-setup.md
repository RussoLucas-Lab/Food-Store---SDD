## ADDED Requirements

### Requirement: Vite build process
The system SHALL use Vite as the build tool and development server for the React frontend.

#### Scenario: Development server starts successfully
- **WHEN** developer runs `npm run dev`
- **THEN** Vite starts a dev server at http://localhost:5173 with hot module replacement enabled

#### Scenario: Production build completes
- **WHEN** developer runs `npm run build`
- **THEN** Vite compiles React components and outputs optimized bundles to `dist/` directory

#### Scenario: TypeScript compilation
- **WHEN** Vite builds the project
- **THEN** TypeScript strict mode validates all `.tsx` and `.ts` files with no implicit any

### Requirement: Environment configuration
The system SHALL support multiple environments (dev, test, production) via `.env` files.

#### Scenario: Environment variables are accessible
- **WHEN** code accesses `import.meta.env.VITE_API_URL`
- **THEN** it reads the value from `.env.local` or `.env` without runtime errors

#### Scenario: Git ignores sensitive env files
- **WHEN** developer creates `.env.local` file
- **THEN** `.gitignore` prevents it from being committed; only `.env.example` is checked in

### Requirement: Package scripts
The system SHALL provide npm scripts for dev, build, test, and lint.

#### Scenario: Developers can run all common tasks
- **WHEN** developer runs `npm run dev`, `npm run build`, `npm run test`, `npm run lint`
- **THEN** each command executes successfully and completes its intended task
