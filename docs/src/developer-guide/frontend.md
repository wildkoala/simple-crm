# Frontend

The frontend is a React 18 single-page application built with TypeScript, Vite, Tailwind CSS, and shadcn/ui.

## Project Setup

```bash
cd frontend
npm install
npm run dev     # Start development server on :5173
npm run build   # Production build to dist/
npm run lint    # ESLint
npm test        # Vitest + React Testing Library
```

## Key Files

| File | Purpose |
|------|---------|
| `src/App.tsx` | Route definitions, lazy loading, provider tree |
| `src/main.tsx` | React entry point |
| `src/lib/api.ts` | API client -- all backend communication |
| `src/lib/badges.ts` | Badge color/label helpers for statuses |
| `src/contexts/AuthContext.tsx` | Authentication state management |
| `src/components/Layout.tsx` | Sidebar navigation, page layout |
| `src/components/ProtectedRoute.tsx` | Auth guards for routes |

## Routing

All routes are defined in `App.tsx` using React Router v6:

- **Public routes**: `/login`, `/forgot-password`, `/reset-password`
- **Protected routes**: Wrapped in `<ProtectedRoute>` -- redirect to login if unauthenticated.
- **Admin routes**: Wrapped in `<AdminProtectedRoute>` -- require admin role.

All page components are lazy-loaded with `React.lazy()` and wrapped in `<Suspense>` with a spinner fallback.

## API Client

`src/lib/api.ts` provides typed functions for every backend endpoint:

```typescript
// All API calls go through fetchApi() which handles:
// - Auth token injection (Bearer header)
// - 401 handling (clear token, dispatch auth:unauthorized event)
// - Timeout (30 seconds)
// - Error message extraction from response JSON

export async function getContacts(): Promise<Contact[]> {
  return fetchApi<Contact[]>('/contacts');
}
```

Auth token is stored in `localStorage` under the key `auth_token`.

## Authentication Flow

1. `AuthContext` checks `localStorage` for an existing token on mount.
2. If found, calls `GET /auth/me` to validate and load user data.
3. On login (email/password or Google), stores the JWT and loads user data.
4. On 401 response from any API call, clears token and dispatches `auth:unauthorized` event.
5. `AuthContext` listens for the event and redirects to login.

## UI Components

The project uses [shadcn/ui](https://ui.shadcn.com/) components built on Radix UI primitives:

- `Button`, `Card`, `Input`, `Label`, `Textarea`
- `Select`, `Checkbox`, `Switch`
- `Dialog`, `AlertDialog`
- `Tooltip`, `Badge`
- `Sonner` (toast notifications)

Components are in `src/components/ui/` and can be customized directly.

## Styling

- **Tailwind CSS** for utility-first styling.
- **CSS variables** for theming (defined in `index.css`).
- **clsx** and **tailwind-merge** for conditional class composition.
- **class-variance-authority** for component variants.

## Icons

[Lucide React](https://lucide.dev/) provides all icons. Import as needed:

```typescript
import { Plus, Trash2, Edit } from 'lucide-react';
```

## Environment Variables

Frontend environment variables must be prefixed with `VITE_` for Vite to expose them:

| Variable | Description |
|----------|-------------|
| `VITE_API_BASE_URL` | Backend API URL (`/api` in Docker, `http://localhost:8000` for local dev) |
| `VITE_GOOGLE_CLIENT_ID` | Google client ID for Sign-In button (auto-set from `GOOGLE_CLIENT_ID` in Docker) |

Set in `frontend/.env.local` for local development outside Docker. In Docker, `GOOGLE_CLIENT_ID` from the root `.env` is mapped to `VITE_GOOGLE_CLIENT_ID` automatically by the Dockerfile.
