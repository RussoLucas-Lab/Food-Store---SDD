## Context

The Food Store project has a production-ready backend (Python/FastAPI with Repository + UoW + Service Layer pattern) waiting for a frontend to consume it. The frontend must:
- Support role-based access control (ADMIN, USER, GUEST)
- Integrate with JWT authentication (tokens in Authorization header)
- Handle async operations (API calls) with error states
- Scale across multiple feature modules (auth, CRUD, cart, payments, admin)
- Maintain type safety with TypeScript
- Follow component reusability patterns (atomic design)

Current state: No frontend exists. Starting from scratch.

## Goals / Non-Goals

**Goals:**
- Establish Vite + React + TypeScript as the frontend tech stack
- Create a scalable folder structure (feature-slice architecture + atomic design)
- Implement React Router v6 with protected routes for role-based access
- Set up a base HTTP client with automatic token injection and error handling
- Create reusable atomic components (Button, Input, Card, Modal, Layout)
- Establish testing infrastructure (vitest + React Testing Library)
- Configure build tools (ESLint, Prettier, environment variables)
- Document conventions and patterns for future developers

**Non-Goals:**
- Implement actual feature pages (auth, CRUD, cart, etc.) — those come in subsequent changes
- Design UI/UX (use basic, functional styling; design refinement is a separate change)
- Implement backend API calls for specific features — just the HTTP client skeleton
- Full E2E testing or Cypress setup — that's a later change

## Decisions

### 1. **Vite over Create React App**
**Why**: Vite is faster (instant HMR, faster builds), has lower overhead, and is modern. CRA is bloated and outdated.
**Alternative**: Next.js — overkill for this SPA; we don't need SSR.

### 2. **Feature-Slice Architecture + Atomic Design**
**Why**: Enables parallel feature development, clear separation of concerns, scalability.
**Structure**:
```
src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   └── services/
│   ├── productos/
│   ├── clientes/
│   └── ...
├── shared/
│   ├── components/
│   │   ├── atoms/ (Button, Input, Label, etc.)
│   │   ├── molecules/ (FormField, Card, etc.)
│   │   └── organisms/ (Layout, Header, etc.)
│   ├── hooks/
│   ├── services/ (HTTP client, utils)
│   └── context/
└── App.tsx
```

### 3. **React Context for Global State (initial setup)**
**Why**: Simpler than Redux/Zustand for bootstrap phase. Avoids over-engineering. We'll add Zustand/Redux if state complexity grows.
**Context layers**:
- AuthContext (token, user, role)
- ThemeContext (light/dark mode)
- NotificationContext (toasts/alerts)

### 4. **React Router v6 with Protected Routes**
**Why**: Modern, hooks-based, supports nested layouts naturally.
**Implementation**: 
- ProtectedRoute wrapper component checks user role/token
- Route structure mirrors features (e.g., `/auth/*`, `/productos/*`, `/admin/*`)
- Redirect to login if not authenticated

### 5. **Axios + Interceptors for HTTP Client**
**Why**: Cleaner than fetch; interceptors allow automatic token injection, error handling, retries.
**Alternative**: Fetch API wrapper — lighter but requires manual interceptor logic.

### 6. **TypeScript with strict mode**
**Why**: Catches errors at compile time, improves IDE autocomplete, essential for large teams.
**Config**: `strict: true`, `noImplicitAny: true`, `esModuleInterop: true`

### 7. **Vitest + React Testing Library**
**Why**: Vite-native testing (fast), similar to Jest but lighter. React Testing Library enforces testing from user perspective.
**Alternative**: Jest + RTL — slower, not Vite-optimized.

### 8. **Environment Configuration**
**Why**: Separate dev/test/prod configs without rebuilding.
**Implementation**: `.env.local`, `.env.example` (checked into git); Vite's `import.meta.env` for type-safe access.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| **State complexity grows**: Context becomes inefficient if state tree deepens | Move to Zustand (minimal API, Redux devtools support) when needed — easy migration |
| **HTTP client grows complex**: Interceptors become hard to maintain | Document interceptor patterns; refactor into plugin architecture if needed |
| **Routing complexity**: Protected routes + nested layouts can become tangled | Keep ProtectedRoute simple; use layout routes (React Router v6.4+) for nested layouts |
| **Component library inconsistency**: Atoms/molecules diverge in style/naming | Establish component conventions upfront; enforce via Storybook + lint rules (later change) |
| **Slow dev startup**: Vite plugin overhead | Monitor startup time; lazy-load plugins if needed |

## Migration Plan

1. **Phase 1**: Scaffold Vite project, basic folder structure, minimal components
2. **Phase 2**: Set up routing, authentication context, protected routes
3. **Phase 3**: Create HTTP client, test its integration with backend
4. **Phase 4**: Build atomic components (atoms → molecules → organisms)
5. **Phase 5**: Test infrastructure, CI/CD hooks

No rollback needed — this is new infrastructure. If it fails, we revert to CRA or another approach, but there's no existing frontend to protect.

## Open Questions

- **CSS Framework**: Tailwind vs Styled Components vs CSS Modules? → Decision deferred to style/theme change
- **State management finalization**: Does Context suffice, or do we need Zustand upfront? → Observe during auth implementation
- **Component library**: Build custom atoms or use Material-UI / shadcn? → Design later; use custom for now
- **API mocking**: Should we mock the backend during dev? → Optional; real backend is running locally
