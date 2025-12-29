# Asviglager Backend

FastAPI backend for the Asviglager asset management system with MongoDB database.

## Features

- **Product CRUD API** - Create, Read, Update, Delete operations for products
- **Warehouse Stock Tracking** - Track stock quantities per warehouse
- **JWT Authentication** - Secure API access with JWT tokens
- **Soft Delete** - Products are never permanently deleted
- **Flexible Schema** - Supports both MVP minimal products and full Dolibarr imports
- **MongoDB** - NoSQL database for flexible product data
- **Full-text Search** - Search products by label
- **Barcode Support** - Lookup products by barcode
- **UTF-8 Support** - Handles Danish/Swedish characters (å, ä, ö)

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── auth.py         # Authentication endpoints
│   │   └── products.py     # Product CRUD endpoints
│   ├── core/
│   │   ├── config.py       # Application configuration
│   │   └── security.py     # JWT and password utilities
│   ├── db/
│   │   ├── mongodb.py      # MongoDB connection
│   │   └── indexes.py      # Database indexes
│   ├── models/
│   │   ├── product.py      # Product data models
│   │   └── user.py         # User data models
│   └── main.py             # FastAPI application
├── scripts/
│   ├── create_admin.py             # Create admin user
│   └── import_dolibarr_products.py # Import products from JSON
├── .env                    # Environment variables (not in git)
├── .env.example            # Example environment variables
├── pyproject.toml          # Project dependencies
└── run.py                  # Server entry point
```

## Requirements

- Python 3.13+
- MongoDB (running at 172.32.0.3:27017)
- uv (Python package manager)

## Setup

### 1. Install Dependencies

```bash
cd backend
uv sync
```

### 2. Configure Environment

The `.env` file is already configured with:
- MongoDB connection: `mongodb://asviglager:Horsens2025@172.32.0.3:27017`
- JWT secret key
- CORS settings

To use different settings, copy `.env.example` and modify as needed.

### 3. Create Admin User

```bash
uv run python scripts/create_admin.py
```

This creates a user with:
- Username: `admin`
- Password: `admin123`

**⚠️ IMPORTANT: Change this password after first login!**

### 4. Import Dolibarr Products (Optional)

```bash
uv run python scripts/import_dolibarr_products.py
```

This imports 100 products from `../dcjph-products.json` into MongoDB.

### 5. Start the Server

```bash
uv run python run.py
```

Or use uvicorn directly:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## API Usage

### Authentication

1. **Login** to get an access token:

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

2. **Use the token** in subsequent requests:

```bash
export TOKEN="your-access-token-here"

curl -X GET http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer $TOKEN"
```

### Product Endpoints

All product endpoints require authentication (Bearer token).

#### Create Product (MVP)

```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ref": "TEST001",
    "label": "Test Product",
    "price": "99.99",
    "barcode": "1234567890123",
    "cost_price": "50.00",
    "description": "A test product"
  }'
```

#### List Products

```bash
# List all products (paginated)
curl -X GET "http://localhost:8000/api/v1/products?skip=0&limit=50" \
  -H "Authorization: Bearer $TOKEN"

# Search products
curl -X GET "http://localhost:8000/api/v1/products?search=hønsesalat" \
  -H "Authorization: Bearer $TOKEN"

# Filter by type
curl -X GET "http://localhost:8000/api/v1/products?type=0" \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Product by ID

```bash
curl -X GET http://localhost:8000/api/v1/products/{product_id} \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Product by Reference

```bash
curl -X GET http://localhost:8000/api/v1/products/ref/100001 \
  -H "Authorization: Bearer $TOKEN"
```

#### Get Product by Barcode

```bash
curl -X GET http://localhost:8000/api/v1/products/barcode/5733020001409 \
  -H "Authorization: Bearer $TOKEN"
```

#### Update Product

```bash
curl -X PUT http://localhost:8000/api/v1/products/{product_id} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "price": "109.99",
    "description": "Updated description"
  }'
```

#### Delete Product (Soft Delete)

```bash
curl -X DELETE http://localhost:8000/api/v1/products/{product_id} \
  -H "Authorization: Bearer $TOKEN"
```

#### List Deleted Products

```bash
curl -X GET http://localhost:8000/api/v1/products/deleted/list \
  -H "Authorization: Bearer $TOKEN"
```

### Stock Management Endpoints

#### Update Stock for a Warehouse

```bash
curl -X PUT http://localhost:8000/api/v1/products/{product_id}/stock/{warehouse_ref} \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": 32.5
  }'
```

#### Get All Stock for a Product

```bash
curl -X GET http://localhost:8000/api/v1/products/{product_id}/stock \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "Hedensted01": {"items": 32.5},
  "Copenhagen01": {"items": 15.0}
}
```

#### Get Stock for Specific Warehouse

```bash
curl -X GET http://localhost:8000/api/v1/products/{product_id}/stock/{warehouse_ref} \
  -H "Authorization: Bearer $TOKEN"
```

#### Remove Stock Data for a Warehouse

```bash
curl -X DELETE http://localhost:8000/api/v1/products/{product_id}/stock/{warehouse_ref} \
  -H "Authorization: Bearer $TOKEN"
```

## Product Data Model

### MVP Fields (Required for new products)

- `ref` (string, unique) - Product reference number
- `label` (string) - Product name
- `price` (decimal) - Sale price

### MVP Optional Fields

- `type` (string) - "0" = product, "1" = service (default: "0")
- `barcode` (string) - EAN-13 or similar barcode
- `cost_price` (decimal) - Purchase/cost price
- `description` (string) - Product description
- `status` (string) - "0" = disabled, "1" = enabled (default: "1")
- `status_buy` (string) - Can be purchased (default: "1")

### Automatic Fields

- `deleted` (boolean) - Soft delete flag (default: false)
- `deleted_at` (datetime) - When product was deleted
- `date_creation` (datetime) - Creation timestamp
- `date_modification` (datetime) - Last modification timestamp
- `stock_warehouse` (object) - Stock quantities per warehouse
  - Key: warehouse reference (e.g., "Hedensted01")
  - Value: `{"items": float}` - Number of items in stock

### Full Dolibarr Fields

Imported products retain all 160+ Dolibarr fields including:
- Tax rates, pricing variants, stock levels
- Physical dimensions, warehouse info
- Batch tracking, custom codes
- And much more...

## Database Indexes

MongoDB indexes for performance:

- `ref` - Unique index for product reference
- `barcode` - Unique sparse index (allows multiple nulls)
- `label` - Text index for full-text search
- `date_creation` - Descending index for sorting
- `deleted` - Index for filtering deleted products
- `username` - Unique index for users
- `email` - Unique sparse index for users

## Development

### Running Tests

```bash
# TODO: Add pytest tests
uv run pytest
```

### Code Style

```bash
# TODO: Add linting
uv run ruff check .
uv run black .
```

### API Documentation

Visit http://localhost:8000/docs for interactive Swagger UI documentation.

## Environment Variables

See `.env.example` for all available configuration options:

- `MONGODB_URI` - MongoDB connection string
- `MONGODB_DB_NAME` - Database name
- `JWT_SECRET_KEY` - Secret for JWT token signing
- `JWT_ALGORITHM` - JWT algorithm (default: HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - Token expiration (default: 1440 = 24h)
- `API_V1_PREFIX` - API route prefix (default: /api/v1)
- `CORS_ORIGINS` - Allowed CORS origins (JSON array)
- `ENVIRONMENT` - Environment name (development/production)

## Security Notes

1. **Change default admin password** after first login
2. **Keep `.env` file secure** - it contains database credentials
3. **Use HTTPS in production** - JWT tokens should be transmitted securely
4. **Rotate JWT secret** periodically
5. **Restrict CORS origins** in production

## Troubleshooting

### MongoDB Connection Failed

- Check if MongoDB is running at 172.32.0.3:27017
- Verify credentials: asviglager / Horsens2025
- Check network connectivity

### Import Script Fails

- Ensure `dcjph-products.json` exists in parent directory
- Check file encoding is UTF-8
- Verify JSON format is valid

### JWT Token Expired

- Tokens expire after 24 hours by default
- Login again to get a new token
- Adjust `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` if needed

## License

Private project for Asviglager asset management system.
