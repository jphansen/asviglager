# Asviglager Mobile App

Flutter mobile application for the Asviglager asset management system.

## Features

- **Authentication**: JWT-based login with token storage
- **Product Listing**: View all products with search functionality
- **Create Product**: Add new products with:
  - Product ID/Reference
  - Product name
  - Photo capture using camera
  - Barcode scanning
  - Selling price (optional)
  - Description (optional)

## Prerequisites

- Flutter SDK (3.0.0 or higher)
- Android Studio or VS Code with Flutter extensions
- Android SDK for Android development
- Backend API running at `http://localhost:8000` (or configure in `lib/config/api_config.dart`)

## Setup

1. **Install Flutter dependencies:**
   ```bash
   cd /home/jph/SRC/asviglager/app
   export PATH="$PATH:/tmp/flutter/bin"
   flutter pub get
   ```

2. **Configure API endpoint:**
   - For Android Emulator: Uses `http://10.0.2.2:8000/api/v1` (already configured)
   - For physical device: Edit `lib/config/api_config.dart` and replace with your computer's IP

3. **Check Flutter setup:**
   ```bash
   flutter doctor
   ```

## Running the App

### Android Emulator
```bash
flutter run
```

### Physical Android Device
1. Enable USB debugging on your device
2. Connect via USB
3. Run: `flutter run`

## Default Login

Use the credentials configured in your backend:
- Username: `admin`
- Password: `admin123`

## Project Structure

```
lib/
├── main.dart                 # App entry point
├── config/
│   └── api_config.dart      # API configuration
├── models/
│   └── product.dart         # Product data model
├── services/
│   ├── auth_service.dart    # Authentication service
│   └── product_service.dart # Product API service
└── screens/
    ├── login_screen.dart    # Login screen
    ├── home_screen.dart     # Main menu
    ├── products_screen.dart # Product list
    └── new_product_screen.dart # Create product
```

## Dependencies

- `provider`: State management
- `http`: API requests
- `shared_preferences`: Token storage
- `image_picker`: Camera functionality
- `mobile_scanner`: Barcode scanning
- `permission_handler`: Camera permissions

## Permissions

The app requires the following Android permissions:
- `INTERNET`: API communication
- `CAMERA`: Photo capture and barcode scanning

## Backend API

Ensure the FastAPI backend is running:
```bash
cd /home/jph/SRC/asviglager/backend
uv run python run.py
```

API should be accessible at `http://localhost:8000`

## Troubleshooting

### Cannot connect to backend
- Emulator: Verify backend is running on `http://localhost:8000`
- Physical device: Use your computer's local IP address in `api_config.dart`

### Camera not working
- Grant camera permissions when prompted
- Check `AndroidManifest.xml` has camera permissions

### Build errors
- Run `flutter clean && flutter pub get`
- Verify Flutter SDK path in `android/local.properties`

## Development Status

All core features have been implemented and tested:
- ✅ Authentication with JWT tokens
- ✅ Product listing with search
- ✅ Product creation with camera and barcode scanner
- ✅ API integration with FastAPI backend

### Tasks Completed

- [x] Project scaffolding and structure
- [x] Authentication flow
- [x] Product screens
- [x] Camera and barcode scanner integration
- [x] Flutter extensions setup
- [x] Dependencies installation
- [x] Tasks configuration for running the app
- [x] App launched and tested in debug mode
- [x] Documentation complete

## Future Enhancements

- Product editing
- Product deletion
- Warehouse management
- Offline mode
- Image upload to backend
- Product history
