## 1. Project Setup & Dependencies

- [x] 1.1 Create Vite React TypeScript project with `npm create vite@latest` (or use existing frontend folder)
- [x] 1.2 Install core dependencies: react, react-dom, react-router-dom
- [x] 1.3 Install dev dependencies: vite, @vitejs/plugin-react, typescript, tsx
- [x] 1.4 Install utility dependencies: axios, dotenv
- [x] 1.5 Install testing dependencies: vitest, @vitest/ui, @testing-library/react, @testing-library/user-event, jsdom
- [x] 1.6 Install dev tools: eslint, prettier, @typescript-eslint/parser, @typescript-eslint/eslint-plugin
- [x] 1.7 Configure npm scripts: dev, build, test, lint, preview in package.json

## 2. Build & Environment Configuration

- [x] 2.1 Create vite.config.ts with React plugin and TypeScript configuration
- [x] 2.2 Create tsconfig.json with strict mode enabled and path aliases (@/* → src/*)
- [x] 2.3 Create .env.example with VITE_API_URL, VITE_API_TIMEOUT, VITE_APP_NAME
- [x] 2.4 Create .env.local (git-ignored) with actual development values
- [x] 2.5 Create .eslintrc.json for TypeScript and React linting
- [x] 2.6 Create .prettierrc for code formatting
- [x] 2.7 Verify vite dev server starts with `npm run dev`

## 3. Folder Structure & Architecture

- [x] 3.1 Create `src/` directory with subdirectories: features/, shared/, types/
- [x] 3.2 Create `src/shared/components/` with subdirectories: atoms/, molecules/, organisms/
- [x] 3.3 Create `src/shared/hooks/` for custom React hooks
- [x] 3.4 Create `src/shared/services/` for HTTP client and utilities
- [x] 3.5 Create `src/shared/context/` for React Context providers
- [x] 3.6 Create placeholder feature folders: `src/features/auth/`, `src/features/productos/`, `src/features/clientes/`, `src/features/admin/`
- [x] 3.7 Each feature folder has: components/, pages/, hooks/, services/, index.ts (barrel export)

## 4. Core HTTP Client

- [x] 4.1 Create `src/shared/services/httpClient.ts` with Axios instance
- [x] 4.2 Add request interceptor to inject Authorization header with JWT token
- [x] 4.3 Add response interceptor to handle 401 errors and token refresh
- [x] 4.4 Add error handler to transform API errors into consistent format
- [x] 4.5 Configure retry logic for network failures (max 3 retries)
- [x] 4.6 Create `src/shared/services/index.ts` to export httpClient singleton

## 5. React Context & Global State

- [x] 5.1 Create `src/shared/context/AuthContext.tsx` with user, token, role, login, logout
- [x] 5.2 Create `useAuth()` custom hook to consume AuthContext
- [x] 5.3 Implement localStorage persistence for auth token
- [x] 5.4 Create `src/shared/context/ThemeContext.tsx` with light/dark mode support
- [x] 5.5 Create `useTheme()` custom hook to consume ThemeContext
- [x] 5.6 Create `src/shared/context/NotificationContext.tsx` for toast notifications
- [x] 5.7 Create `useNotification()` custom hook to trigger notifications
- [x] 5.8 Create `src/shared/context/index.ts` to export all providers as ContextProviders wrapper component

## 6. Atomic Components (Atoms)

- [x] 6.1 Create Button component (props: variant, size, onClick, disabled, children)
- [x] 6.2 Create Input component (props: type, placeholder, value, onChange, error, name)
- [x] 6.3 Create Label component (props: htmlFor, children)
- [x] 6.4 Create Text component for typography (props: variant, children, className)
- [x] 6.5 Add JSDoc comments and TypeScript props to all atoms

## 7. Composite Components (Molecules)

- [x] 7.1 Create FormField component (Label + Input + error message)
- [x] 7.2 Create Card component (container with title, padding, shadow; props: title, children, className)
- [x] 7.3 Create LoadingSpinner component
- [x] 7.4 Create ErrorMessage component (displays error text with icon)
- [x] 7.5 Create SuccessMessage component (displays success text with icon)

## 8. Layout Components (Organisms)

- [x] 8.1 Create Header component (logo, navigation links, user menu, theme toggle)
- [x] 8.2 Create Sidebar component (navigation menu with role-based visibility)
- [x] 8.3 Create Footer component (copyright, links)
- [x] 8.4 Create Layout component (combines Header, Sidebar, main content area, Footer)
- [x] 8.5 Create Modal component (overlay, dialog box, close button; props: isOpen, onClose, title, children)

## 9. Routing & Protected Routes

- [x] 9.1 Create Router configuration in `src/router.tsx` with BrowserRouter
- [x] 9.2 Create ProtectedRoute component wrapper (checks auth + role, redirects to login if needed)
- [x] 9.3 Define public routes (/, /login, /register, /about)
- [x] 9.4 Define protected routes (/profile, /productos, /clientes, /admin) with role checks
- [x] 9.5 Create error page component (NotFound 404, Unauthorized 403)
- [x] 9.6 Set up Layout route for nested pages (header, sidebar, footer persist across routes)

## 10. Test Infrastructure

- [x] 10.1 Create vitest.config.ts with jsdom environment and @testing-library setup
- [x] 10.2 Create `src/test/setup.ts` with global test setup (mocks, fixtures)
- [x] 10.3 Create test utilities: renderWithProviders(), mockHttpClient()
- [x] 10.4 Create sample component test for Button.test.tsx
- [x] 10.5 Create sample context test for AuthContext.test.tsx
- [x] 10.6 Configure coverage thresholds in vitest.config.ts

## 11. Root App Component & Providers

- [x] 11.1 Create `src/App.tsx` with Router and context providers
- [x] 11.2 Wrap App with ContextProviders (Auth, Theme, Notification)
- [x] 11.3 Create `src/main.tsx` entry point
- [x] 11.4 Create `public/index.html` with root div and script tag
- [x] 11.5 Verify app renders at http://localhost:5173 with hot reload

## 12. Documentation & Conventions

- [x] 12.1 Create `FRONTEND_SETUP.md` documenting folder structure, conventions, and patterns
- [x] 12.2 Create `COMPONENT_GUIDE.md` with examples of how to create atoms/molecules/organisms
- [x] 12.3 Create `ROUTING_GUIDE.md` with examples of public, protected, and admin routes
- [x] 12.4 Create `HTTP_CLIENT_GUIDE.md` with examples of using httpClient and creating feature services
- [x] 12.5 Add inline comments to all shared components and services

## 13. Verification & Testing

- [x] 13.1 Run `npm run build` and verify no errors; check dist/ output
- [x] 13.2 Run `npm run test` and verify test infrastructure works (at least 2-3 sample tests pass)
- [x] 13.3 Run `npm run lint` and fix any linting errors
- [ ] 13.4 Verify `npm run dev` starts server with HMR working
- [ ] 13.5 Manual test: reload page, verify auth persists; toggle theme, verify change persists
- [ ] 13.6 Manual test: navigate to protected route without auth, verify redirect to login
- [ ] 13.7 Create basic integration test: login flow (if auth endpoint available)

## 14. Final Polish

- [ ] 14.1 Update project README.md with frontend setup instructions
- [ ] 14.2 Add CONTRIBUTING.md for frontend contribution guidelines
- [ ] 14.3 Create git hooks (pre-commit: lint, pre-push: test)
- [ ] 14.4 Verify all npm scripts work (dev, build, test, lint, preview)
- [ ] 14.5 Document edge cases in FRONTEND_TROUBLESHOOTING.md
