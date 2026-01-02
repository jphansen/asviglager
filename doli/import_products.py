#!/usr/bin/env python3
"""
Import products from Dolibarr to Asviglager backend.
Includes product data, stock levels, and photo uploads.
"""

import json
import sys
import os
import base64
import requests
from requests.exceptions import RequestException
from pathlib import Path


def load_product_categories(product_categories_file='product_categories.txt'):
    """Load product-to-category mapping from text file."""
    mapping = {}
    try:
        with open(product_categories_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    product_id, categories = line.split(':', 1)
                    # Categories are comma-separated
                    category_list = [cat.strip() for cat in categories.split(',')]
                    mapping[product_id] = category_list
        print(f"✓ Loaded {len(mapping)} product-category mappings")
        return mapping
    except FileNotFoundError:
        print(f"Warning: Product categories file '{product_categories_file}' not found")
        print("Products will be imported without warehouse stock assignments")
        return {}


def import_products(
    products_file='products.json',
    product_categories_file='product_categories.txt',
    photos_dir='downloaded_documents',
    backend_url='https://stock.asvig.com/api/v1',
    username=None,
    password=None
):
    """
    Import products, stock levels, and photos from Dolibarr export to backend.
    
    Args:
        products_file (str): Path to products JSON file
        product_categories_file (str): Path to product_categories.txt file
        photos_dir (str): Directory containing downloaded product photos
        backend_url (str): Backend API base URL
        username (str): Backend username for authentication
        password (str): Backend password for authentication
    """
    
    # Load products
    try:
        with open(products_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except FileNotFoundError:
        print(f"Error: Products file '{products_file}' not found.")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse products file: {e}")
        return False
    
    if not products:
        print("No products found in file.")
        return False
    
    print(f"Loaded {len(products)} products from {products_file}")
    
    # Load product-category mapping
    product_categories = load_product_categories(product_categories_file)
    
    # Authenticate with backend
    print(f"\nAuthenticating with backend: {backend_url}")
    
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
    except Exception as e:
        print(f"✗ Authentication failed: {e}")
        return False
    
    # Prepare headers for API requests
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Import products
    print(f"\nImporting products to: {backend_url}/products")
    print("="*80)
    
    created_count = 0
    skipped_count = 0
    failed_count = 0
    stock_added = 0
    photos_uploaded = 0
    
    products_url = f"{backend_url}/products"
    
    for idx, product in enumerate(products, 1):
        # Extract Dolibarr product fields
        doli_id = product.get('id')
        ref = product.get('ref', '')
        label = product.get('label', '')
        description = product.get('description', '')
        barcode = product.get('barcode', '')
        price = product.get('price', 0.0)
        cost_price = product.get('cost_price')
        product_type = product.get('type', '0')
        status = product.get('status', '1')
        status_buy = product.get('status_buy', '1')
        
        # Skip if no ref or label
        if not ref or not label:
            print(f"  [{idx}/{len(products)}] Skipping (missing ref or label)")
            skipped_count += 1
            continue
        
        # Ensure price is a number
        try:
            price = float(price) if price else 0.0
            if cost_price:
                cost_price = float(cost_price)
        except (ValueError, TypeError):
            price = 0.0
            cost_price = None
        
        print(f"  [{idx}/{len(products)}] {ref}: {label[:50]}...", end='', flush=True)
        
        # Prepare product data
        product_data = {
            'ref': ref,
            'label': label,
            'price': price,
            'type': product_type,
            'status': status,
            'status_buy': status_buy,
        }
        
        # Add optional fields
        if barcode:
            product_data['barcode'] = barcode
        if cost_price is not None:
            product_data['cost_price'] = cost_price
        if description:
            product_data['description'] = description
        
        try:
            # Create product
            response = requests.post(
                products_url,
                json=product_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:
                created_product = response.json()
                # Backend returns _id (MongoDB ID) in response
                backend_product_id = created_product.get('_id') or created_product.get('id')
                print(f" ✓ Created (ID: {backend_product_id})", end='')
                created_count += 1
                
                # Add stock to warehouses based on category mapping
                if doli_id in product_categories:
                    warehouse_refs = product_categories[doli_id]
                    for warehouse_ref in warehouse_refs:
                        try:
                            stock_url = f"{products_url}/{backend_product_id}/stock/{warehouse_ref}"
                            stock_response = requests.put(
                                stock_url,
                                json={'items': 1.0},
                                headers=headers,
                                timeout=30
                            )
                            if stock_response.status_code == 200:
                                stock_added += 1
                        except Exception:
                            pass  # Continue even if stock update fails
                    print(f" | Stock: {len(warehouse_refs)} warehouse(s)", end='')
                
                # Upload photos if they exist
                photos_uploaded_for_product = upload_photos_for_product(
                    backend_product_id=backend_product_id,
                    doli_ref=ref,
                    photos_dir=photos_dir,
                    headers=headers,
                    backend_url=backend_url
                )
                if photos_uploaded_for_product > 0:
                    photos_uploaded += photos_uploaded_for_product
                    print(f" | Photos: {photos_uploaded_for_product}", end='')
                
                print()  # New line
                
            elif response.status_code == 400:
                error_detail = response.json().get('detail', '')
                if 'already exists' in error_detail:
                    print(" ⊘ Already exists")
                    skipped_count += 1
                else:
                    print(f" ✗ Failed: {error_detail}")
                    failed_count += 1
            else:
                print(f" ✗ Failed: HTTP {response.status_code}")
                failed_count += 1
                
        except RequestException as e:
            print(f" ✗ Error: {e}")
            failed_count += 1
            continue
    
    # Print summary
    print("\n" + "="*80)
    print("IMPORT SUMMARY")
    print("="*80)
    print(f"Total products: {len(products)}")
    print(f"✓ Successfully created: {created_count}")
    print(f"⊘ Skipped (already exist or missing data): {skipped_count}")
    print(f"✗ Failed: {failed_count}")
    print(f"\nStock assignments: {stock_added}")
    print(f"Photos uploaded: {photos_uploaded}")
    
    return failed_count == 0


def upload_photos_for_product(backend_product_id, doli_ref, photos_dir, headers, backend_url):
    """Upload all photos for a product."""
    photos_uploaded = 0
    
    # Look for product photo directory
    # Photos are in: downloaded_documents/AV-2411-000001/filename.jpg
    product_photo_dir = os.path.join(photos_dir, doli_ref)
    
    if not os.path.exists(product_photo_dir):
        return 0
    
    # Get all image files in the directory
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    photo_files = []
    
    try:
        for file in os.listdir(product_photo_dir):
            file_path = os.path.join(product_photo_dir, file)
            if os.path.isfile(file_path):
                ext = os.path.splitext(file)[1].lower()
                if ext in image_extensions:
                    photo_files.append((file, file_path))
    except Exception as e:
        return 0
    
    if not photo_files:
        return 0
    
    # Upload each photo
    for filename, file_path in photo_files:
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
                'description': f'Product photo for {doli_ref}'
            }
            
            response = requests.post(
                photos_url,
                json=photo_data,
                headers=headers,
                timeout=60
            )
            
            if response.status_code == 201:
                photo_response = response.json()
                photo_id = photo_response['id']
                
                # Link photo to product
                link_url = f"{backend_url}/products/{backend_product_id}/photos/{photo_id}"
                link_response = requests.post(
                    link_url,
                    headers=headers,
                    timeout=30
                )
                
                if link_response.status_code == 204:
                    photos_uploaded += 1
                    
        except Exception:
            continue  # Skip this photo if it fails
    
    return photos_uploaded


def main():
    """Main function with command-line interface."""
    
    default_products_file = 'products.json'
    default_product_categories_file = 'product_categories.txt'
    default_photos_dir = 'downloaded_documents'
    default_backend_url = 'https://stock.asvig.com/api/v1'
    
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("Usage: python import_products.py <username> <password> [products_file] [categories_file] [photos_dir] [backend_url]")
        print(f"  username: Backend username for authentication")
        print(f"  password: Backend password for authentication")
        print(f"  products_file (optional): Path to products.json (default: {default_products_file})")
        print(f"  categories_file (optional): Path to product_categories.txt (default: {default_product_categories_file})")
        print(f"  photos_dir (optional): Directory with photos (default: {default_photos_dir})")
        print(f"  backend_url (optional): Backend API URL (default: {default_backend_url})")
        print("\nExample:")
        print("  python import_products.py admin mypassword")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    products_file = sys.argv[3] if len(sys.argv) > 3 else default_products_file
    product_categories_file = sys.argv[4] if len(sys.argv) > 4 else default_product_categories_file
    photos_dir = sys.argv[5] if len(sys.argv) > 5 else default_photos_dir
    backend_url = sys.argv[6] if len(sys.argv) > 6 else default_backend_url
    
    # Import products
    success = import_products(
        products_file=products_file,
        product_categories_file=product_categories_file,
        photos_dir=photos_dir,
        backend_url=backend_url,
        username=username,
        password=password
    )
    
    if not success:
        print("\nImport completed with errors.")
        sys.exit(1)
    else:
        print("\n✓ Import completed successfully!")


if __name__ == '__main__':
    main()
