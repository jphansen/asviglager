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
- **Modern Dark Theme**: Sleek dark UI with deep blue gradients and cyan accents
- **Modern SPA**: Built with React 18, TypeScript, Material-UI
- **Authentication**: JWT-based login with secure token management
- **Product Management**:
  - List products with real-time search and pagination
  - View product details with photos
  - Edit products with photo management (upload/remove)
  - Delete products with confirmation dialog (soft delete)
  - Drag-and-drop photo upload
  - Barcode support (accepts any format)
- **Warehouse Management**:
  - Full CRUD operations for warehouses
  - Search and filter warehouses
  - View warehouse details with address/contact info
  - Enable/disable warehouses
- **Stock Management**:
  - View all products with stock levels across warehouses
  - Add/update/remove stock for products at specific warehouse locations
  - Real-time stock totals and location breakdown
  - Search products by reference, name, or barcode
  - Visual stock indicators and location chips
- **Modern UI/UX**:
  - Professional dark theme with custom styling
  - Enhanced shadows, borders, and hover effects
  - CORS Configuration**: Flexible cross-origin support for development
- **Products API**: Full CRUD operations for products
  - List products with pagination and partial-text search
  - Get product by ID, reference, or barcode
  - Create, update, and delete products
  - Auto-generated product IDs with format AA-YYMM-XXXXXX
  - Flexible barcode validation (accepts any format) fetching and caching

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
  - Batch loading (100 products at a time) to handle large inventories
- **Product Creation**: Add new products with:
  - Auto-generated Product IDs (AA-YYMM-XXXXXX format)
  - Camera integration for product photos with immediate upload
  - Barcode scanner (accepts any format - no validation)
  - Photo upload with progress indication
  - Visual confirmation when photos are uploaded
- **Stock Management**:
  - View all products with stock levels
  - Add/update/remove stock at warehouse locations
  - Batch loading to avoid API limits
  - Real-time stock totals per warehouse
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
VITE_API_URL=https://stock.asvig.com/api/v1
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
- `GET /api/v1/products/{id}/stock` - Get all stock for a product
- `GET /api/v1/products/{id}/stock/{warehouse_ref}` - Get stock at specific warehouse
- `PUT /api/v1/products/{id}/stock/{warehouse_ref}` - Update stock at warehouse
- `DELETE /api/v1/products/{id}/stock/{warehouse_ref}` - Remove stock from warehouse
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

### v0.4.0 (January 2026)
- **JWT Refresh Token System**:
  - Added 30-day refresh tokens alongside 24-hour access tokens
  - Implemented automatic token refresh on 401 errors
  - Created ApiClient wrapper in Flutter for seamless token management
  - Updated backend `/auth/refresh` endpoint
  - Refactored all Flutter service classes to use ApiClient
- **UI Improvements**:
  - Redesigned Flutter home screen with button-style menu layout
  - Added clickable user info card with server health status
  - Connected health check to `/health` endpoint
- **Pagination & Search Enhancements**:
  - Added server-side pagination (50 items per page) to Products and Stock pages
  - Implemented debounced search with backend queries
  - Search now queries entire database (not just loaded records)
  - Added page navigation controls with prev/next buttons
  - Fixed stock page to match products page pagination
- **Dolibarr Data Migration**:
  - Created complete migration pipeline from Dolibarr to Asviglager
  - `fetch_products_api.py`: Export products, categories, and documents
  - `fetch_product_categories.py`: Extract product-category mappings
  - `download_documents.py`: Download and decode document files
  - `import_categories.py`: Import categories as warehouses
  - `import_products.py`: Import products with stock and photos
  - Successful import of 198 products with stock and images

### v0.3.1 (January 2025)
- **README Updates**: Enhanced documentation with detailed feature descriptions
  - Added comprehensive feature breakdown for web frontend
  - Updated mobile app features with batch loading and stock management details
  - Fixed markdown formatting issues
- **Flutter Model Improvements**: 
  - Added `_parseDouble` helper method in `product.dart` for robust stock item parsing
  - Better handling of numeric values from API responses
- **Android Build Configuration**:
  - Updated Gradle wrapper to version 8.12 for compatibility
  - Added NOTICE file for Android build
- **Documentation Cleanup**: Fixed broken sections and improved overall README structure

### v0.3.0 (January 2025)
- **Modern Dark Theme**: Applied professional dark theme to web frontend
  - Deep blue gradient backgrounds (#0A0E27, #141B3D)
  - Bright cyan primary color (#00E5FF)
  - Enhanced shadows, borders, and hover effects
  - Custom styled scrollbars
  - Improved typography with Inter font
- **Enhanced Product Management**:
  - Added delete product functionality with confirmation dialog
  - Success/error notifications with Snackbars
  - Removed barcode validation constraints (accepts any format)
- **CORS Configuration**: Fixed cross-origin issues for remote API access
- **Flutter Stock Management**: 
  - Implemented complete stock management in mobile app
  - Fixed 422 errors with batch loading (100 products per request)
- **Bug Fixes**:
  - Fixed photo upload MongoDB `_id` field handling
  - Fixed Flutter stock screen pagination issues
  - Improved error handling across all platforms

### v0.2.0 (December 2024)
- Added React web frontend with TypeScript
- Implemented product management with photo upload (drag-and-drop)
- Implemented full warehouse CRUD operations
- **Added stock management system**:
  - View all products with stock levels across warehouses
  - Add/update/remove stock at specific warehouse locations
  - Stock tracking with `stock_warehouse` field structure
  - Real-time stock totals and location breakdown
- Updated warehouse model:
  - Renamed `lieu` field to `short` (location code)
  - Renamed `statut` field to `status` with boolean type (enabled/disabled)
- Enhanced photo management with inline viewing and editing
- Fixed photo upload issue with MongoDB `_id` field handling
- Added responsive Material-UI design matching Flutter app
- Integrated TanStack Query for optimized data fetching

### v0.3.1 (January 2025)
- **README Updates**: Enhanced documentation with detailed feature descriptions
  - Added comprehensive feature breakdown for web frontend
  - Updated mobile app features with batch loading and stock management details
  - Fixed markdown formatting issues
- **Flutter Model Improvements**: 
  - Added `_parseDouble` helper method in `product.dart` for robust stock item parsing
  - Better handling of numeric values from API responses
- **Android Build Configuration**:
  - Updated Gradle wrapper to version 8.12 for compatibility
  - Added NOTICE file for Android build
- **Documentation Cleanup**: Fixed broken sections and improved overall README structure

## Data Migration from Dolibarr

The `doli/` directory contains scripts for migrating data from Dolibarr ERP to Asviglager:

1. **Export from Dolibarr**:
   ```bash
   cd doli
   python fetch_products_api.py  # Exports products, categories, documents
   python fetch_product_categories.py  # Extracts category mappings
   python download_documents.py  # Downloads product photos
   ```

2. **Import to Asviglager**:
   ```bash
   python import_categories.py <username> <password>  # Import categories as warehouses
   python import_products.py <username> <password>    # Import products with stock and photos
   ```

The `ARCHIVE/` folder contains legacy SQL scripts and development files.
- `fetch_products_api.py`: Import products from Dolibarr API
- Various SQL files: Historical database schemas and data

## Contributing

This is a private asset management system. For any questions or issues, please contact the repository maintainer.

## License

Proprietary - All rights reserved

## Project History

Originally developed to manage physical assets and inventory, integrating with Dolibarr ERP system. The project has evolved to include a modern mobile interface for on-the-go asset management.