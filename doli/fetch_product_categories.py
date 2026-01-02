#!/usr/bin/env python3
"""
Fetch product categories mapping from Dolibarr API.
Creates a simple key:value file mapping product IDs to category IDs.
"""

import json
import sys
import requests
from requests.exceptions import RequestException


def fetch_product_categories(api_key, products_file='products.json', output_file='product_categories.txt'):
    """
    Fetch categories for each product and create mapping file.
    
    Args:
        api_key (str): API key for authentication
        products_file (str): Path to products JSON file
        output_file (str): Path to output text file
    """
    
    # Load products to get their IDs
    try:
        with open(products_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except FileNotFoundError:
        print(f"Error: Products file '{products_file}' not found.")
        print("Please run fetch_products_api.py first to generate products.json")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse products file: {e}")
        return False
    
    if not products:
        print("No products found in products file.")
        return False
    
    # API configuration
    base_url = 'https://lager.asvig.com'
    
    # Headers with API key
    headers = {
        'DOLAPIKEY': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    print(f"Fetching product categories from: {base_url}/api/index.php/products/{{id}}/categories")
    print(f"Processing {len(products)} products...\n")
    
    product_category_map = {}
    products_with_categories = 0
    products_without_categories = 0
    failed_requests = 0
    
    for idx, product in enumerate(products, 1):
        # Get product ID
        product_id = product.get('id')
        product_ref = product.get('ref', 'N/A')
        
        if not product_id:
            print(f"  [{idx}/{len(products)}] Skipping product (no ID): {product_ref}")
            continue
        
        # Build URL for this product's categories
        url = f'{base_url}/api/index.php/products/{product_id}/categories'
        params = {
            'sortfield': 's.rowid',
            'sortorder': 'ASC'
        }
        
        print(f"  [{idx}/{len(products)}] Product ID {product_id} (ref: {product_ref})...", end='', flush=True)
        
        try:
            # Make GET request
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            # Check if request was successful
            response.raise_for_status()
            
            # Parse JSON response
            categories = response.json()
            
            if categories and len(categories) > 0:
                # Extract category IDs
                category_ids = [cat.get('id') for cat in categories if isinstance(cat, dict) and cat.get('id')]
                
                if category_ids:
                    # Store in map
                    product_category_map[product_id] = category_ids
                    products_with_categories += 1
                    print(f" {len(category_ids)} categor{'y' if len(category_ids) == 1 else 'ies'}: {','.join(category_ids)}")
                else:
                    products_without_categories += 1
                    print(" no valid category IDs")
            else:
                products_without_categories += 1
                print(" no categories")
                
        except RequestException as e:
            print(f" ERROR: {e}")
            failed_requests += 1
            continue
        except Exception as e:
            print(f" ERROR: {type(e).__name__}: {e}")
            failed_requests += 1
            continue
    
    # Write mapping to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for product_id, category_ids in sorted(product_category_map.items(), key=lambda x: int(x[0])):
                # Format: product_id:category_id1,category_id2,...
                category_str = ','.join(category_ids)
                f.write(f"{product_id}:{category_str}\n")
        
        print(f"\n✓ Product-category mapping saved to: {output_file}")
    except Exception as e:
        print(f"\nError writing output file: {e}")
        return False
    
    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Total products processed: {len(products)}")
    print(f"✓ Products with categories: {products_with_categories}")
    print(f"⊘ Products without categories: {products_without_categories}")
    print(f"✗ Failed requests: {failed_requests}")
    print(f"\nMappings saved: {len(product_category_map)}")
    
    # Show sample mappings
    if product_category_map:
        print("\nSample mappings:")
        for product_id, category_ids in list(product_category_map.items())[:5]:
            category_str = ','.join(category_ids)
            print(f"  {product_id}:{category_str}")
    
    return True


def main():
    """Main function with command-line interface."""
    
    # Default API key
    default_api_key = 'ah9jP9o3rIPO22znqXo28cHdP9W7FT7R'
    default_products_file = 'products.json'
    default_output_file = 'product_categories.txt'
    
    # Parse command line arguments
    if len(sys.argv) == 1:
        # Use defaults
        api_key = default_api_key
        products_file = default_products_file
        output_file = default_output_file
    elif len(sys.argv) == 2:
        # Custom API key provided
        api_key = sys.argv[1]
        products_file = default_products_file
        output_file = default_output_file
    elif len(sys.argv) == 4:
        # Custom API key, products file, and output file
        api_key = sys.argv[1]
        products_file = sys.argv[2]
        output_file = sys.argv[3]
    else:
        print("Usage: python fetch_product_categories.py [api_key] [products_file] [output_file]")
        print(f"  Default API key: {default_api_key[:10]}...")
        print(f"  Default products file: {default_products_file}")
        print(f"  Default output file: {default_output_file}")
        sys.exit(1)
    
    # Fetch product categories
    success = fetch_product_categories(api_key, products_file, output_file)
    
    if not success:
        print("\nFailed to fetch product categories. Please check:")
        print("1. API key is correct")
        print("2. Network connection")
        print("3. API endpoint availability")
        print("4. Products file exists and is valid")
        sys.exit(1)
    else:
        print("\n✓ Product categories mapping completed successfully!")


if __name__ == '__main__':
    main()
