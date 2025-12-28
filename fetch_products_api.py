#!/usr/bin/env python3
"""
Fetch products from REST API and save to JSON file.
"""

import json
import sys
import requests
from requests.exceptions import RequestException


def convert_price_fields(product):
    """
    Convert price fields from strings to floats with 2 decimals.
    
    Args:
        product (dict): Product dictionary
    """
    price_fields = [
        'price', 'price_ttc', 'price_min', 'price_min_ttc', 
        'cost_price', 'pmp', 'tva_tx', 'localtax1_tx', 'localtax2_tx'
    ]
    
    for field in price_fields:
        if field in product and product[field]:
            try:
                # Convert string to float and round to 2 decimals
                product[field] = round(float(product[field]), 2)
            except (ValueError, TypeError):
                # Keep original value if conversion fails
                pass


def fetch_products(api_key, output_file='products.json'):
    """
    Fetch ALL products from API with pagination and save to JSON file.
    
    Args:
        api_key (str): API key for authentication
        output_file (str): Path to output JSON file
    """
    
    # API configuration
    base_url = 'https://sundbus.asvig.com'
    endpoint = 'products'
    url = f'{base_url}/api/index.php/{endpoint}'
    
    # Headers with API key
    # Based on API error message, it expects DOLAPIKEY header
    headers = {
        'DOLAPIKEY': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    print(f"Fetching products from: {url}")
    print("Implementing pagination to fetch ALL products...")
    
    all_products = []
    page = 0
    limit = 100  # Dolibarr API default page size
    
    response = None
    try:
        while True:
            # Add pagination parameters
            params = {
                'limit': limit,
                'page': page
            }
            
            print(f"  Page {page + 1}: Fetching products {page * limit + 1}-{(page + 1) * limit}...", end='')
            
            # Make GET request with pagination
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            # Check if request was successful
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            if not data or len(data) == 0:
                # No more products, we've reached the end
                print(" (no more data)")
                break
            
            # Convert price fields for each product
            for product in data:
                if isinstance(product, dict):
                    convert_price_fields(product)
            
            all_products.extend(data)
            print(f" {len(data)} products (total: {len(all_products)})")
            
            # If we got fewer products than the limit, we've reached the end
            if len(data) < limit:
                break
            
            page += 1
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_products, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Successfully fetched {len(all_products)} product(s) in total")
        print(f"✓ Data saved to: {output_file}")
        
        # Print summary
        if all_products:
            print(f"\nTotal products: {len(all_products)}")
            
            # Show first item as example
            first_item = all_products[0]
            if isinstance(first_item, dict):
                print("\nFirst product sample:")
                # Show first 5 fields
                for key, value in list(first_item.items())[:5]:
                    print(f"  {key}: {value}")
                
                # Show price fields if available
                print("\nPrice fields in first product:")
                price_fields = ['price', 'price_ttc', 'cost_price', 'pmp']
                for field in price_fields:
                    if field in first_item:
                        print(f"  {field}: {first_item[field]} (type: {type(first_item[field]).__name__})")
        
        return True
        
    except RequestException as e:
        print(f"Request failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Status code: {e.response.status_code}")
            try:
                error_detail = e.response.json()
                print(f"Error detail: {error_detail}")
            except (ValueError, json.JSONDecodeError):
                print(f"Response text: {e.response.text[:200]}...")
        return False
        
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON response: {e}")
        if response is not None:
            print(f"Response text: {response.text[:200]}...")
        else:
            print("No response received")
        return False
        
    except Exception as e:
        print(f"Unexpected error: {type(e).__name__}: {e}")
        return False


def main():
    """Main function with command-line interface."""
    
    # Default API key from requirements
    default_api_key = 'e5JGJ20jfz7S8vou6s5SDWaD67E6qtET'
    default_output = 'products.json'
    
    # Parse command line arguments
    if len(sys.argv) == 1:
        # Use defaults
        api_key = default_api_key
        output_file = default_output
    elif len(sys.argv) == 2:
        # Custom API key provided
        api_key = sys.argv[1]
        output_file = default_output
    elif len(sys.argv) == 3:
        # Custom API key and output file
        api_key = sys.argv[1]
        output_file = sys.argv[2]
    else:
        print("Usage: python fetch_products_api.py [api_key] [output_file]")
        print(f"  Default API key: {default_api_key[:10]}...")
        print(f"  Default output: {default_output}")
        sys.exit(1)
    
    # Fetch products
    success = fetch_products(api_key, output_file)
    
    if not success:
        print("\nFailed to fetch products. Please check:")
        print("1. API key is correct")
        print("2. Network connection")
        print("3. API endpoint availability")
        sys.exit(1)


if __name__ == '__main__':
    main()
