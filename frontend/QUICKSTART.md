# Asviglager Frontend - Quick Start Guide

## What's Been Built

A fully functional React + TypeScript SPA (Single Page Application) for managing your warehouse inventory system.

## Running the Application

### 1. Start the Backend (if not already running)

```bash
cd backend
# Activate your Python environment first if needed
uvicorn app.main:app --reload
```

Backend will be at: `http://localhost:8000`

### 2. Start the Frontend

```bash
cd frontend
npm run dev
```

Frontend will be at: `http://localhost:5173`

### 3. Login

Open `http://localhost:5173` in your browser. You'll see the login page.

**Test Credentials**: Use any username/password you've created in your backend system.

## Current Features

### ✅ Working Now

1. **Authentication**
   - Login/logout functionality
   - JWT token management
   - Automatic token refresh
   - Protected routes

2. **Dashboard**
   - Welcome page with user greeting
   - Quick access cards to Products and Warehouses
   - Clean Material Design interface

3. **Products Page**
   - View all products in a table
   - Search by name, reference, or barcode
   - See product details (price, status, type, photos)
   - Responsive layout

4. **Layout & Navigation**
   - Responsive sidebar navigation
   - Top app bar with user menu
   - Mobile-friendly drawer menu
   - Logout from user menu

### ⏳ To Be Built (Remaining Work)

1. **Product Forms**
   - Create new product dialog
   - Edit existing products
   - Photo upload with drag-and-drop
   - Delete products
   - Link/unlink photos

2. **Warehouse Management**
   - List warehouses
   - Create/edit/delete warehouses
   - Enable/disable warehouses

3. **Stock Management**
   - Update stock quantities per warehouse
   - View stock levels
   - Stock history

4. **Enhancements**
   - Dashboard statistics
   - Export to CSV
   - Bulk operations
   - Advanced filtering

## Architecture

```
Browser (http://localhost:5173)
  │
  ├─ React SPA
  │   ├─ Material-UI components
  │   ├─ TanStack Query (data fetching)
  │   ├─ React Router (navigation)
  │   └─ Axios (HTTP client with JWT)
  │
  └─ API calls ───> FastAPI Backend (http://localhost:8000/api/v1)
                     │
                     └─ MongoDB
```

## File Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   └── ProtectedRoute.tsx       # Route guard for authentication
│   │   └── layout/
│   │       └── MainLayout.tsx           # Main app layout with sidebar
│   ├── pages/
│   │   ├── LoginPage.tsx                # Login form
│   │   ├── DashboardPage.tsx            # Home dashboard
│   │   ├── ProductsPage.tsx             # Products list & search
│   │   └── WarehousesPage.tsx           # Warehouses (placeholder)
│   ├── services/
│   │   ├── api.ts                       # Axios instance with JWT
│   │   ├── authService.ts               # Login/logout API
│   │   ├── productService.ts            # Products CRUD
│   │   ├── warehouseService.ts          # Warehouses CRUD
│   │   └── photoService.ts              # Photo upload
│   ├── hooks/
│   │   └── useAuth.tsx                  # Auth context & hook
│   ├── types/
│   │   └── index.ts                     # TypeScript types
│   └── App.tsx                          # Main app with routing
├── .env.development                     # Dev API URL
└── package.json
```

## Key Technologies

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite 5** - Fast build tool (downgraded for Node 18 compatibility)
- **Material-UI** - Component library (matches your Flutter app)
- **TanStack Query** - Smart data fetching with caching
- **React Router** - Client-side routing
- **Axios** - HTTP client with interceptors
- **React Hook Form + Zod** - Forms (ready for use)

## Environment Variables

Edit `.env.development` to change the backend URL:

```env
VITE_API_URL=http://localhost:8000/api/v1
```

For production, use `.env.production`.

## Next Steps

To continue development, you can:

1. **Add Product Creation Form**
   - Create a dialog component with React Hook Form
   - Add photo upload with react-dropzone
   - Validate with Zod schema

2. **Build Warehouse Module**
   - Similar to Products page
   - CRUD operations for warehouses

3. **Implement Stock Management**
   - Add stock update dialogs
   - Show stock levels in product table
   - Create stock history view

4. **Add Dashboard Stats**
   - Query product counts
   - Show warehouse status
   - Display low stock alerts

## Troubleshooting

### Can't connect to backend?

1. Check backend is running: `http://localhost:8000/docs`
2. Verify CORS in [backend/app/core/config.py](../backend/app/core/config.py) includes `http://localhost:5173`

### Login not working?

1. Check Network tab in browser DevTools
2. Verify credentials exist in backend
3. Check backend logs for errors

### Changes not appearing?

Vite has hot module reload - just save the file. If broken, restart with `npm run dev`.

## Development Tips

- **Install React DevTools** browser extension for debugging
- **Use browser DevTools Network tab** to inspect API calls
- **Check Application > Local Storage** to see JWT token
- **Backend API docs** at `http://localhost:8000/docs` show all endpoints

## Production Build

```bash
npm run build        # Creates dist/ folder
npm run preview      # Test production build locally
```

Deploy the `dist/` folder to any static hosting (Nginx, Vercel, Netlify, S3).

---

**Status**: MVP functional - authentication, navigation, and product listing working!

**Ready for**: Login testing, product browsing, and continued development of CRUD operations.
