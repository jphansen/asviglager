#!/usr/bin/env python3
"""
Import photos for products from downloaded_documents directory to backend.

This script:
1. Scans the downloaded_documents directory for product folders
2. For each folder, finds the corresponding product in the backend
3. Uploads all photos (jpg, png, webp, gif) found in that folder
4. Links the photos to the product

Usage:
    python import_photos.py <username> <password> [photos_dir] [backend_url]
"""

import os
import sys
import base64
import requests
from typing import List, Tuple, Optional


def authenticate(backend_url: str, username: str, password: str) -> str:
    """Authenticate with backend and return access token."""
    login_url = f"{backend_url}/auth/login"
    try:
        response = requests.post(
            login_url,
            data={'username': username, 'password': password},
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=30
        )
        response.raise_for_status()
        token_data = response.json()
        access_token = token_data['access_token']
        print("✓ Authentication successful")
        return access_token
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        raise


def get_product_by_ref(
    backend_url: str, ref: str, headers: dict
) -> Optional[dict]:
    """Get product from backend by ref."""
    products_url = f"{backend_url}/products"
    try:
        # Search for product by ref
        response = requests.get(
            products_url,
            headers=headers,
            timeout=30
        )
        if response.status_code == 200:
            products = response.json()
            for product in products:
                if product.get('ref') == ref:
                    return product
        return None
    except Exception as e:
        print(f"    Error fetching product {ref}: {e}")
        return None


def get_photo_files(directory: str) -> List[Tuple[str, str]]:
    """Get all image files in a directory."""
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    photo_files = []
    
    try:
        if not os.path.exists(directory):
            return []
        
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in image_extensions:
                    photo_files.append((file, file_path))
    except Exception as e:
        print(f"    Error reading directory {directory}: {e}")
        return []
    
    return photo_files


def upload_photo(
    backend_url: str,
    filename: str,
    file_path: str,
    product_ref: str,
    headers: dict
) -> Optional[str]:
    """Upload a photo to backend and return photo ID."""
    try:
        # Read and encode file
        with open(file_path, 'rb') as f:
            file_content = f.read()
        base64_content = base64.b64encode(file_content).decode('utf-8')
        
        # Determine content type
        ext = os.path.splitext(filename)[1].lower()
        content_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        content_type = content_type_map.get(ext, 'image/jpeg')
        
        # Upload photo
        photos_url = f"{backend_url}/photos"
        photo_data = {
            'filename': filename,
            'content_type': content_type,
            'data': base64_content,
            'description': f'Product photo for {product_ref}'
        }
        
        response = requests.post(
            photos_url,
            json=photo_data,
            headers=headers,
            timeout=60
        )
        
        if response.status_code == 201:
            photo_response = response.json()
            photo_id = photo_response.get('id') or photo_response.get('_id')
            return photo_id
        else:
            error_msg = f"      Failed to upload {filename}: "
            error_msg += f"HTTP {response.status_code}"
            print(error_msg)
            return None
            
    except Exception as e:
        print(f"      Error uploading {filename}: {e}")
        return None


def link_photo_to_product(
    backend_url: str, product_id: str, photo_id: str, headers: dict
) -> bool:
    """Link a photo to a product."""
    try:
        link_url = f"{backend_url}/products/{product_id}/photos/{photo_id}"
        response = requests.post(
            link_url,
            headers=headers,
            timeout=30
        )
        
        return response.status_code == 204
        
    except Exception as e:
        print(f"      Error linking photo: {e}")
        return False


def import_photos(
    photos_dir: str, backend_url: str, username: str, password: str
):
    """Import all photos from photos_dir to backend."""
    
    print("Photo Import Tool")
    print("="*80)
    print(f"Photos directory: {photos_dir}")
    print(f"Backend URL: {backend_url}")
    print()
    
    # Authenticate
    print("Authenticating with backend...")
    try:
        access_token = authenticate(backend_url, username, password)
    except Exception:
        return False
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Get list of product directories
    if not os.path.exists(photos_dir):
        print(f"Error: Photos directory '{photos_dir}' not found")
        return False
    
    product_dirs = []
    try:
        for item in os.listdir(photos_dir):
            item_path = os.path.join(photos_dir, item)
            if os.path.isdir(item_path):
                product_dirs.append(item)
    except Exception as e:
        print(f"Error reading photos directory: {e}")
        return False
    
    if not product_dirs:
        print("No product directories found")
        return False
    
    print(f"Found {len(product_dirs)} product directories")
    print()
    
    # Statistics
    processed = 0
    skipped = 0
    photos_uploaded = 0
    photos_failed = 0
    products_not_found = 0
    
    # Process each product directory
    for idx, product_ref in enumerate(sorted(product_dirs), 1):
        product_dir = os.path.join(photos_dir, product_ref)
        
        # Get photo files
        photo_files = get_photo_files(product_dir)
        
        if not photo_files:
            msg = f"  [{idx}/{len(product_dirs)}] {product_ref}: "
            msg += "No photos found"
            print(msg)
            skipped += 1
            continue
        
        msg = f"  [{idx}/{len(product_dirs)}] {product_ref}: "
        msg += f"Found {len(photo_files)} photo(s)"
        print(msg, end='', flush=True)
        
        # Get product from backend
        product = get_product_by_ref(backend_url, product_ref, headers)
        
        if not product:
            print(" - Product not found in backend ✗")
            products_not_found += 1
            continue
        
        product_id = product.get('_id') or product.get('id')
        
        # Check if product already has photos
        existing_photos = product.get('photos', [])
        if existing_photos:
            msg = f" - Already has {len(existing_photos)} photo(s), "
            msg += "skipping ⊘"
            print(msg)
            skipped += 1
            continue
        
        if not product_id:
            print(" - No product ID ✗")
            products_not_found += 1
            continue
        
        print()
        
        # Upload each photo
        uploaded_count = 0
        for filename, file_path in photo_files:
            print(f"    Uploading {filename}...", end='', flush=True)
            
            # Upload photo
            photo_id = upload_photo(
                backend_url, filename, file_path, product_ref, headers
            )
            
            if photo_id:
                # Link to product
                if link_photo_to_product(
                    backend_url, product_id, photo_id, headers
                ):
                    print(" ✓")
                    uploaded_count += 1
                    photos_uploaded += 1
                else:
                    print(" ✗ (failed to link)")
                    photos_failed += 1
            else:
                print(" ✗ (failed to upload)")
                photos_failed += 1
        
        if uploaded_count > 0:
            msg = f"    Uploaded {uploaded_count}/{len(photo_files)} "
            msg += f"photos for {product_ref}"
            print(msg)
        
        processed += 1
    
    # Print summary
    print()
    print("="*80)
    print("IMPORT SUMMARY")
    print("="*80)
    print(f"Total product directories: {len(product_dirs)}")
    print(f"✓ Products processed: {processed}")
    print(f"⊘ Skipped (no photos or already have photos): {skipped}")
    print(f"✗ Products not found in backend: {products_not_found}")
    print()
    print(f"✓ Photos successfully uploaded: {photos_uploaded}")
    print(f"✗ Photos failed: {photos_failed}")
    
    return True


def main():
    """Main function with command-line interface."""
    
    default_photos_dir = 'downloaded_documents'
    default_backend_url = 'https://stock.asvig.com/api/v1'
    
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("Usage: python import_photos.py <username> <password> "
              "[photos_dir] [backend_url]")
        print("  username: Backend username for authentication")
        print("  password: Backend password for authentication")
        print(f"  photos_dir (optional): Directory with photos "
              f"(default: {default_photos_dir})")
        print(f"  backend_url (optional): Backend API URL "
              f"(default: {default_backend_url})")
        print()
        print("The photos_dir should contain subdirectories named after "
              "product refs")
        print("(e.g., AV-2411-000001, AV-2411-000002, etc.)")
        print()
        print("Example:")
        print("  python import_photos.py admin mypassword")
        print("  python import_photos.py admin mypassword ./my_photos")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    photos_dir = sys.argv[3] if len(sys.argv) > 3 else default_photos_dir
    backend_url = sys.argv[4] if len(sys.argv) > 4 else default_backend_url
    
    # Import photos
    success = import_photos(
        photos_dir=photos_dir,
        backend_url=backend_url,
        username=username,
        password=password
    )
    
    if not success:
        print("\nImport failed.")
        sys.exit(1)
    else:
        print("\n✓ Import completed!")


if __name__ == '__main__':
    main()
