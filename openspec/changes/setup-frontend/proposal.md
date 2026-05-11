## Why

The Food Store system requires a modern, scalable frontend architecture to support complex features like real-time inventory, role-based dashboards, and transactional workflows. Setting up the frontend infrastructure now (Vite, routing, component structure, state management) establishes the foundation for all subsequent frontend features (auth, CRUD operations, cart, payments, admin panel). Without this, future features will either be slow to develop or architecturally fragile.

## What Changes

- Scaffold a Vite-based React application with TypeScript
- Establish feature-slice architecture (each feature in `src/features/<feature>/`)
- Create a main layout component with top navigation and sidebar
- Set up client-side routing (React Router v6) with protected routes
- Configure build tooling (Vite, ESLint, Prettier, vitest for unit tests)
- Create atomic component structure (atoms, molecules, organisms)
- Establish project conventions (folder structure, naming, imports)
- Set up environment configuration (.env.local, .env.example)
- Create a base HTTP client / API service factory
- Establish testing infrastructure (vitest, React Testing Library)

## Capabilities

### New Capabilities

- `frontend-setup`: Vite + React + TypeScript configuration with build and dev scripts
- `frontend-routing`: React Router v6 setup with protected routes and nested layouts
- `frontend-architecture`: Feature-slice architecture and atomic design patterns
- `frontend-components-base`: Reusable atomic components (Button, Input, Card, Modal, Layout)
- `frontend-http-client`: Base HTTP service for API consumption with error handling and auth token injection
- `frontend-state-context`: React Context setup for global state (auth, theme, notifications)
- `frontend-testing`: Unit and component testing infrastructure (vitest + React Testing Library)

### Modified Capabilities

_(none — this is infrastructure, no spec-level requirement changes to existing capabilities)_

## Impact

- Affects: All frontend work going forward (auth, CRUD, cart, payments, admin panel)
- New dependencies: Vite, React, React Router, Axios (or Fetch API wrapper), React Context, vitest, Prettier, ESLint
- Development environment: Node.js 18+ required, npm/yarn package manager
- Breaking changes: None (this is new — no existing frontend to break)
- Integration: Frontend will consume backend API (setup-backend already complete) via HTTP client
