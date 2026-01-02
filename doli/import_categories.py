#!/usr/bin/env python3
"""
Import categories from Dolibarr to Asviglager backend as warehouses.
Maps Dolibarr categories to backend warehouses.
"""

import json
import sys
import requests
from requests.exceptions import RequestException


def import_categories_as_warehouses(
    categories_file='categories.json',
    backend_url='https://stock.asvig.com/api/v1',
    username=None,
    password=None
):
    """
    Import categories from JSON file to backend as warehouses.
    
    Mapping:
        categories.id -> warehouse.ref
        categories.id -> warehouse.short
        categories.label -> warehouse.label
        categories.description -> warehouse.description
    
    Args:
        categories_file (str): Path to categories JSON file
        backend_url (str): Backend API base URL
        username (str): Backend username for authentication
        password (str): Backend password for authentication
    """
    
    # Load categories
    try:
        with open(categories_file, 'r', encoding='utf-8') as f:
            categories = json.load(f)
    except FileNotFoundError:
        print(f"Error: Categories file '{categories_file}' not found.")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse categories file: {e}")
        return False
    
    if not categories:
        print("No categories found in file.")
        return False
    
    print(f"Loaded {len(categories)} categories from {categories_file}")
    
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
    
    # Import categories as warehouses
    print(f"\nImporting categories as warehouses to: {backend_url}/warehouses")
    print("="*60)
    
    created_count = 0
    skipped_count = 0
    failed_count = 0
    
    warehouses_url = f"{backend_url}/warehouses"
    
    for idx, category in enumerate(categories, 1):
        # Extract required fields
        cat_id = category.get('id')
        label = category.get('label', '')
        description = category.get('description', '')
        
        # Skip if no ID or label
        if not cat_id or not label:
            print(f"  [{idx}/{len(categories)}] Skipping (missing ID or label)")
            skipped_count += 1
            continue
        
        print(f"  [{idx}/{len(categories)}] Category {cat_id}: {label}...", end='', flush=True)
        
        # Prepare warehouse data with mapping
        warehouse_data = {
            'ref': str(cat_id),           # id -> ref
            'short': str(cat_id),         # id -> short
            'label': label,               # label -> label
            'description': description if description else None,  # description -> description
            'status': True,               # Enable by default
            'deleted': False
        }
        
        try:
            # Create warehouse
            response = requests.post(
                warehouses_url,
                json=warehouse_data,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 201:
                print(" ✓ Created")
                created_count += 1
            elif response.status_code == 400:
                # Check if it's a duplicate
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
    print("\n" + "="*60)
    print("IMPORT SUMMARY")
    print("="*60)
    print(f"Total categories: {len(categories)}")
    print(f"✓ Successfully created: {created_count}")
    print(f"⊘ Skipped (already exist or missing data): {skipped_count}")
    print(f"✗ Failed: {failed_count}")
    
    return failed_count == 0


def main():
    """Main function with command-line interface."""
    
    default_categories_file = 'categories.json'
    default_backend_url = 'https://stock.asvig.com/api/v1'
    
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("Usage: python import_categories.py <username> <password> [categories_file] [backend_url]")
        print(f"  username: Backend username for authentication")
        print(f"  password: Backend password for authentication")
        print(f"  categories_file (optional): Path to categories.json (default: {default_categories_file})")
        print(f"  backend_url (optional): Backend API URL (default: {default_backend_url})")
        print("\nExample:")
        print("  python import_categories.py admin mypassword")
        print("  python import_categories.py admin mypassword categories.json http://localhost:8000/api/v1")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2]
    categories_file = sys.argv[3] if len(sys.argv) > 3 else default_categories_file
    backend_url = sys.argv[4] if len(sys.argv) > 4 else default_backend_url
    
    # Import categories
    success = import_categories_as_warehouses(
        categories_file=categories_file,
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
