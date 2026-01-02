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
    base_url = 'https://lager.asvig.com'
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


def fetch_categories(api_key, output_file='categories.json'):
    """
    Fetch ALL categories from API with pagination and save to JSON file.
    
    Args:
        api_key (str): API key for authentication
        output_file (str): Path to output JSON file
    """
    
    # API configuration
    base_url = 'https://lager.asvig.com'
    endpoint = 'categories'
    url = f'{base_url}/api/index.php/{endpoint}'
    
    # Headers with API key
    headers = {
        'DOLAPIKEY': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    print(f"\nFetching categories from: {url}")
    print("Implementing pagination to fetch ALL categories...")
    
    all_categories = []
    page = 0
    limit = 100
    
    response = None
    try:
        while True:
            # Add pagination parameters
            params = {
                'limit': limit,
                'page': page
            }
            
            print(f"  Page {page + 1}: Fetching categories {page * limit + 1}-{(page + 1) * limit}...", end='')
            
            # Make GET request with pagination
            response = requests.get(url, headers=headers, params=params, timeout=30)
            
            # Check if request was successful
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            if not data or len(data) == 0:
                # No more categories, we've reached the end
                print(" (no more data)")
                break
            
            all_categories.extend(data)
            print(f" {len(data)} categories (total: {len(all_categories)})")
            
            # If we got fewer categories than the limit, we've reached the end
            if len(data) < limit:
                break
            
            page += 1
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_categories, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Successfully fetched {len(all_categories)} categor(y/ies) in total")
        print(f"✓ Data saved to: {output_file}")
        
        # Print summary
        if all_categories:
            print(f"\nTotal categories: {len(all_categories)}")
            
            # Show first item as example
            first_item = all_categories[0]
            if isinstance(first_item, dict):
                print("\nFirst category sample:")
                # Show first 5 fields
                for key, value in list(first_item.items())[:5]:
                    print(f"  {key}: {value}")
        
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


def fetch_documents(api_key, products_file='products.json', output_file='documents.json'):
    """
    Fetch ALL documents for each product from API and save to JSON file.
    
    Args:
        api_key (str): API key for authentication
        products_file (str): Path to products JSON file
        output_file (str): Path to output JSON file
    """
    
    # First, load products to get their IDs
    try:
        with open(products_file, 'r', encoding='utf-8') as f:
            products = json.load(f)
    except FileNotFoundError:
        print(f"Error: Products file '{products_file}' not found.")
        print("Please run the script to fetch products first.")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse products file: {e}")
        return False
    
    if not products:
        print("No products found in products file.")
        return False
    
    # API configuration
    base_url = 'https://lager.asvig.com'
    endpoint = 'documents'
    url = f'{base_url}/api/index.php/{endpoint}'
    
    # Headers with API key
    headers = {
        'DOLAPIKEY': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    print(f"\nFetching documents from: {url}")
    print(f"Processing {len(products)} products...")
    
    all_documents = []
    products_with_docs = 0
    total_docs = 0
    
    response = None
    try:
        for idx, product in enumerate(products, 1):
            # Get product ID and ref for logging
            product_id = product.get('id')
            product_ref = product.get('ref', 'N/A')
            
            if not product_id:
                print(f"  [{idx}/{len(products)}] Skipping product (no ID): {product_ref}")
                continue
            
            # Parameters for document fetch
            params = {
                'modulepart': 'produit',
                'id': product_id
            }
            
            print(f"  [{idx}/{len(products)}] Product ID {product_id} (ref: {product_ref})...", end='')
            
            try:
                # Make GET request
                response = requests.get(url, headers=headers, params=params, timeout=30)
                
                # Check if request was successful
                response.raise_for_status()
                
                # Parse JSON response
                data = response.json()
                
                if data and len(data) > 0:
                    # Add product reference to each document for easier tracking
                    for doc in data:
                        if isinstance(doc, dict):
                            doc['product_id'] = product_id
                            doc['product_ref'] = product_ref
                    
                    all_documents.extend(data)
                    products_with_docs += 1
                    total_docs += len(data)
                    print(f" {len(data)} document(s)")
                else:
                    print(" no documents")
                    
            except RequestException as e:
                # Don't fail entire process if one product fails
                print(f" ERROR: {e}")
                continue
        
        # Save to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_documents, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Successfully fetched {total_docs} document(s) from {products_with_docs} products")
        print(f"✓ Data saved to: {output_file}")
        
        # Print summary
        if all_documents:
            print(f"\nTotal documents: {len(all_documents)}")
            print(f"Products with documents: {products_with_docs}/{len(products)}")
            
            # Show first item as example
            first_item = all_documents[0]
            if isinstance(first_item, dict):
                print("\nFirst document sample:")
                # Show first 5 fields
                for key, value in list(first_item.items())[:5]:
                    print(f"  {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"\nUnexpected error: {type(e).__name__}: {e}")
        return False


def main():
    """Main function with command-line interface."""
    
    # Default API key from requirements
    default_api_key = 'ah9jP9o3rIPO22znqXo28cHdP9W7FT7R'
    default_output_products = 'products.json'
    default_output_categories = 'categories.json'
    default_output_documents = 'documents.json'
    
    # Parse command line arguments
    if len(sys.argv) == 1:
        # Use defaults
        api_key = default_api_key
        output_products = default_output_products
        output_categories = default_output_categories
        output_documents = default_output_documents
    elif len(sys.argv) == 2:
        # Custom API key provided
        api_key = sys.argv[1]
        output_products = default_output_products
        output_categories = default_output_categories
        output_documents = default_output_documents
    elif len(sys.argv) == 5:
        # Custom API key and output files
        api_key = sys.argv[1]
        output_products = sys.argv[2]
        output_categories = sys.argv[3]
        output_documents = sys.argv[4]
    else:
        print("Usage: python fetch_products_api.py [api_key] [products_file] [categories_file] [documents_file]")
        print(f"  Default API key: {default_api_key[:10]}...")
        print(f"  Default products output: {default_output_products}")
        print(f"  Default categories output: {default_output_categories}")
        print(f"  Default documents output: {default_output_documents}")
        sys.exit(1)
    
    # Fetch products
    print("="*60)
    print("FETCHING PRODUCTS")
    print("="*60)
    success_products = fetch_products(api_key, output_products)
    
    # Fetch categories
    print("\n" + "="*60)
    print("FETCHING CATEGORIES")
    print("="*60)
    success_categories = fetch_categories(api_key, output_categories)
    
    # Fetch documents (only if products were fetched successfully)
    print("\n" + "="*60)
    print("FETCHING DOCUMENTS")
    print("="*60)
    if success_products:
        success_documents = fetch_documents(api_key, output_products, output_documents)
    else:
        print("Skipping documents fetch (products not available)")
        success_documents = False
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    if success_products and success_categories and success_documents:
        print("✓ Successfully fetched products, categories, and documents")
    elif success_products and success_categories:
        print("✓ Products and categories fetched successfully")
        print("✗ Documents fetch failed")
    elif success_products and success_documents:
        print("✓ Products and documents fetched successfully")
        print("✗ Categories fetch failed")
    elif success_products:
        print("✓ Products fetched successfully")
        print("✗ Categories and documents fetch failed")
    elif success_categories:
        print("✗ Products fetch failed")
        print("✓ Categories fetched successfully")
        print("✗ Documents fetch failed (requires products)")
    else:
        print("✗ All fetches failed")
        print("\nPlease check:")
        print("1. API key is correct")
        print("2. Network connection")
        print("3. API endpoint availability")
        sys.exit(1)


if __name__ == '__main__':
    main()
