# Asviglager - Asset Management System

A modern warehouse inventory management system with a FastAPI backend, React web frontend, and Flutter mobile application for managing products, warehouses, inventory, and product photos.

## Project Structure

```
asviglager/
├── frontend/         # React + TypeScript web application
├── app/              # Flutter mobile application
├── backend/          # FastAPI backend with MongoDB
├── ARCHIVE/          # Legacy SQL scripts and development files
└── README.md         # This file
```

## Features

### Web Frontend (React + TypeScript)
- **Modern SPA**: Built with React 18, TypeScript, Material-UI
- **Authentication**: JWT-based login with secure token management
- **Product Management**:
  - List products with real-time search and pagination
  - View product details with photos
  - Edit products with photo management (upload/remove)
  - Delete products (soft delete)
  - Drag-and-drop photo upload
- **Warehouse Management**:
  - Full CRUD operations for warehouses
  - Search and filter warehouses
  - View warehouse details with address/contact info
  - Enable/disable warehouses
- **Responsive Design**: Works on desktop, tablet, and mobile
- **State Management**: TanStack Query for efficient data fetching and caching

### Backend (FastAPI + MongoDB)
- **JWT Authentication**: Secure token-based authentication
- **Products API**: Full CRUD operations for products
  - List products with pagination and partial-text search
  - Get product by ID, reference, or barcode
  - Create, update, and delete products
  - Auto-generated product IDs with format AA-YYMM-XXXXXX
  - Product-photo relationship management
- **Photo Management API**: Dedicated photo storage system
  - Upload photos as base64 encoded images
  - Link/unlink photos to products
  - Retrieve photo metadata and full images
  - Efficient storage with separate photo collection
- **Warehouses API**: Complete warehouse location management
  - CRUD operations with short location codes
  - Boolean status field (enabled/disabled)
  - Stock tracking per warehouse
  - Soft-delete support
- **RESTful API**: Auto-generated OpenAPI documentation
- **MongoDB Integration**: Async database operations with Motor
- **Advanced Search**: Regex-based partial text search across products

### Mobile App (Flutter)
- **Authentication**: Login with JWT token management
- **Product Listing**: Browse all products with advanced search
  - Partial word search (e.g., "Tosh" finds "Toshiba")
  - Pull-to-refresh functionality
- **Product Creation**: Add new products with:
  - Auto-generated Product IDs (AA-YYMM-XXXXXX format)
  - Camera integration for product photos with immediate upload
  - Barcode scanner with improved handling
  - Photo upload with progress indication
  - Visual confirmation when photos are uploaded
- **Modern UI**: 
  - Compact welcome screen design
  - Dark theme with Material Design 3
  - Responsive layout
- **Cross-platform**: Runs on Android, iOS, and Linux

## Quick Start

### Prerequisites
- Python 3.11+ with uv package manager
- MongoDB instance running
- Flutter SDK (for mobile app development)
- Android SDK (for building Android APK)

### Frontend Setup (Web Application)

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure API endpoint in `.env.development`:
```env
VITE_API_URL=http://vps05.asvig.com:8000/api/v1
```

4. Run the development server:
```bash
npm run dev
```

The web app will be available at `http://localhost:5173`

5. Build for production:
```bash
npm run build
npm run preview  # Preview production build
```

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
uv sync
```

3. Configure MongoDB connection in `app/core/config.py`:
```python
MONGODB_URL = "mongodb://username:password@host:port"
DATABASE_NAME = "asviglager"
```

4. Run the server:
```bash
uv run python run.py
```

The API will be available at `http://localhost:8000`
- OpenAPI docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Mobile App Setup

1. Navigate to app directory:
```bash
cd app
```

2. Install dependencies:
```bash
flutter pub get
```

3. Configure API endpoint in `lib/config/api_config.dart`:
```dart
static const String baseUrl = 'http://10.0.2.2:8000/api/v1';  // For Android emulator
// static const String baseUrl = 'http://192.168.x.x:8000/api/v1';  // For physical device
```

4. Run the app:
```bash
# For Linux desktop
flutter run -d linux

# For Android emulator/device
flutter run

# Build Android APK
flutter build apk --debug
```

### Default Credentials
- Username: `admin`
- Password: `admin123`

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login and get JWT token
- `POST /api/v1/auth/register` - Register new user

### Products
- `GET /api/v1/products` - List all products (with pagination and search)
- `GET /api/v1/products/{id}` - Get product by ID
- `GET /api/v1/products/ref/{ref}` - Get product by reference
- `GET /api/v1/products/barcode/{barcode}` - Get product by barcode
- `POST /api/v1/products` - Create new product
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Soft delete product
- `GET /api/v1/products/{id}/photos` - Get product's photo IDs
- `POST /api/v1/products/{id}/photos/{photo_id}` - Link photo to product
- `DELETE /api/v1/products/{id}/photos/{photo_id}` - Unlink photo from product

### Photos
- `POST /api/v1/photos` - Upload a new photo (base64 encoded)
- `GET /api/v1/photos` - List all photos (metadata only)
- `GET /api/v1/photos/{id}` - Get photo with full image data
- `DELETE /api/v1/photos/{id}` - Delete a photo

### Warehouses
- `GET /api/v1/warehouses` - List all warehouses
- `GET /api/v1/warehouses/{id}` - Get warehouse by ID
- `GET /api/v1/warehouses/ref/{ref}` - Get warehouse by reference
- `POST /api/v1/warehouses` - Create new warehouse
- `PUT /api/v1/warehouses/{id}` - Update warehouse
- `DELETE /api/v1/warehouses/{id}` - Soft delete warehouse
- `POST /api/v1/products/{product_id}/stock/{warehouse_ref}` - Update product stock in warehouse
- `DELETE /api/v1/products/{product_id}/stock/{warehouse_ref}` - Remove product stock from warehouse

## Technology Stack

### Backend
- **FastAPI 0.115.0+**: Modern, fast web framework
- **MongoDB + Motor**: Async NoSQL database
- **Pydantic**: Data validation and settings management
- **python-jose**: JWT token handling
- **bcrypt 4.0.1**: Password hashing
- **uvicorn**: ASGI server

### Web Frontend
- **React 18**: Modern UI library
- **TypeScript**: Type-safe JavaScript
- **Vite 5**: Fast build tool
- **Material-UI (MUI)**: Component library
- **TanStack Query**: Server state management
- **React Router v6**: Client-side routing
- **React Hook Form + Zod**: Form handling with validation
- **react-dropzone**: File upload with drag-and-drop
- **Axios**: HTTP client with JWT interceptors

### Mobile Frontend
- **Flutter 3.38.5**: Cross-platform mobile framework
- **Dart**: Programming language
- **Provider**: State management
- **http**: API communication
- **image_picker**: Camera integration
- **mobile_scanner**: Barcode scanning
- **shared_preferences**: Local storage

## Development

### Backend Development
```bash
cd backend
uv run python run.py  # Run with hot reload
```

### Web Frontend Development
```bash
cd frontend
npm run dev  # Run with hot reload
npm run build  # Build for production
npm run lint  # Run ESLint
```

### Mobile App Development
```bash
cd app
flutter run  # Run with hot reload
flutter test  # Run tests
```

## Recent Changes

### v0.2.0 (December 2024)
- Added React web frontend with TypeScript
- Implemented product management with photo upload (drag-and-drop)
- Implemented full warehouse CRUD operations
- Updated warehouse model:
  - Renamed `lieu` field to `short` (location code)
  - Renamed `statut` field to `status` with boolean type (enabled/disabled)
- Enhanced photo management with inline viewing and editing
- Added responsive Material-UI design matching Flutter app
- Integrated TanStack Query for optimized data fetching

## Data Import

The `ARCHIVE/` folder contains legacy data import scripts:
- `fetch_products_api.py`: Import products from Dolibarr API
- Various SQL files: Historical database schemas and data

## Contributing

This is a private asset management system. For any questions or issues, please contact the repository maintainer.

## License

Proprietary - All rights reserved

## Project History

Originally developed to manage physical assets and inventory, integrating with Dolibarr ERP system. The project has evolved to include a modern mobile interface for on-the-go asset management.
