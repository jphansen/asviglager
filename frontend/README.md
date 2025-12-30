# Asviglager Frontend

React + TypeScript frontend for the Asviglager warehouse inventory management system.

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Material-UI (MUI)** - Component library
- **TanStack Query** - Server state management
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **React Hook Form + Zod** - Form handling and validation

## Getting Started

### Prerequisites

- Node.js 18+ (Note: Vite 7 requires Node 20+, but works on Node 18 with warnings)
- Backend API running at `http://localhost:8000` (or update `.env.development`)

### Installation

```bash
# Install dependencies
npm install
```

### Environment Configuration

The frontend uses different API URLs for development and production:

- **Development**: `http://localhost:8000/api/v1` (from `.env.development`)
- **Production**: `http://vps05.asvig.com:8000/api/v1` (from `.env.production`)

To override, create a `.env.local` file:

```env
VITE_API_URL=http://your-backend-url:8000/api/v1
```

### Development

```bash
# Start development server
npm run dev
```

The app will be available at `http://localhost:5173`

### Build

```bash
# Build for production
npm run build

# Preview production build
npm run preview
```

## Features

### Implemented ✅

- JWT authentication with login/logout
- Dashboard with quick access cards
- Products list with search functionality
- Responsive Material Design layout
- Protected routes

### To Be Implemented ⏳

- Create/edit product forms with photo upload
- Warehouse management
- Stock tracking and updates
- Reporting and analytics

## API Integration

The frontend communicates with the FastAPI backend at `/api/v1`. CORS has been configured in the backend to allow `http://localhost:5173`.

### Authentication Flow

1. User enters credentials on `/login`
2. Frontend sends `POST /auth/token` with form data
3. Backend returns JWT access token
4. Token stored in localStorage
5. Axios interceptor adds `Bearer {token}` to all requests
6. On 401 error, token is cleared and user redirected to login

## Troubleshooting

### CORS Errors

If you see CORS errors:
1. Ensure backend is running
2. Check `VITE_API_URL` in `.env.development`
3. Verify backend CORS configuration includes `http://localhost:5173`

### 401 Unauthorized

If API calls fail with 401:
1. Check if you're logged in
2. Token may have expired (24-hour expiration) - re-login
3. Check backend logs for authentication errors

---

## Original Vite Template Notes


This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
