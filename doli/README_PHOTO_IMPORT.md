# Photo Import Guide

## Overview

This guide explains how to import product photos from the `downloaded_documents` directory into the Asviglager backend.

## Directory Structure

Photos should be organized in subdirectories named after their product reference:

```
doli/downloaded_documents/
├── AV-2411-000001/
│   ├── product-image-1.jpg
│   └── product-image-2.png
├── AV-2411-000002/
│   └── photo.webp
└── AV-2411-000003/
    ├── front.jpg
    ├── back.jpg
    └── detail.gif
```

## Supported Image Formats

- JPG/JPEG (.jpg, .jpeg)
- PNG (.png)
- WebP (.webp)
- GIF (.gif)

## Import Methods

### Method 1: Import Products with Photos (Recommended for New Imports)

If you're importing products for the first time, use the `import_products.py` script which imports both products and their photos:

```bash
cd doli
python import_products.py <username> <password>
```

This script will:
1. Import all products from `products.json`
2. Set up stock levels based on `product_categories.txt`
3. Upload all photos from `downloaded_documents/` and link them to products

### Method 2: Import Photos Only (For Existing Products)

If products are already imported but photos are missing, use the dedicated `import_photos.py` script:

```bash
cd doli
python import_photos.py <username> <password>
```

#### Custom Paths

You can specify custom paths for photos directory and backend URL:

```bash
python import_photos.py <username> <password> [photos_dir] [backend_url]
```

Example:
```bash
python import_photos.py admin mypassword ./downloaded_documents https://stock.asvig.com/api/v1
```

## What the Photo Import Script Does

1. **Scans** the `downloaded_documents` directory for product folders
2. **Finds** all image files in each product folder
3. **Looks up** each product in the backend by its reference (e.g., AV-2411-000001)
4. **Uploads** each photo to the backend's photo storage
5. **Links** the uploaded photos to their corresponding products
6. **Skips** products that already have photos assigned

## Features

- ✓ Automatically detects image files by extension
- ✓ Converts images to base64 for API upload
- ✓ Skips products that already have photos
- ✓ Provides detailed progress reporting
- ✓ Shows summary statistics at the end
- ✓ Handles errors gracefully

## Output Example

```
Photo Import Tool
================================================================================
Photos directory: downloaded_documents
Backend URL: https://stock.asvig.com/api/v1

✓ Authentication successful
Found 150 product directories

  [1/150] AV-2411-000001: Found 3 photo(s)
    Uploading photo1.jpg... ✓
    Uploading photo2.jpg... ✓
    Uploading photo3.png... ✓
    Uploaded 3/3 photos for AV-2411-000001
  [2/150] AV-2411-000002: Found 1 photo(s)
    Uploading front.webp... ✓
    Uploaded 1/1 photos for AV-2411-000002
  [3/150] AV-2411-000003: Already has 2 photo(s), skipping ⊘
  ...

================================================================================
IMPORT SUMMARY
================================================================================
Total product directories: 150
✓ Products processed: 145
⊘ Skipped (no photos or already have photos): 3
✗ Products not found in backend: 2

✓ Photos successfully uploaded: 287
✗ Photos failed: 0

✓ Import completed!
```

## Troubleshooting

### Product not found in backend

If you see "Product not found in backend", it means the product hasn't been imported yet. Run `import_products.py` first to import the products.

### Photos failed to upload

- Check that the image files are valid and not corrupted
- Verify that the file sizes are reasonable (very large files may cause timeouts)
- Ensure your backend has enough storage space

### Authentication failed

- Verify your username and password are correct
- Check that the backend URL is accessible
- Ensure you have proper permissions to upload photos

## Backend API Used

The script uses the following API endpoints:

- `POST /api/v1/photos` - Upload a photo
- `POST /api/v1/products/{product_id}/photos/{photo_id}` - Link photo to product
- `GET /api/v1/products` - Retrieve products to find by reference

See [PHOTO_API.md](../backend/PHOTO_API.md) for complete API documentation.
