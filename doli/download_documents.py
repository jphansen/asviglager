#!/usr/bin/env python3
"""
Download document files from Dolibarr API based on documents.json.
"""

import json
import sys
import os
import base64
import requests
from requests.exceptions import RequestException
from pathlib import Path
from urllib.parse import quote


def download_documents(api_key, documents_file='documents.json', output_dir='downloaded_documents'):
    """
    Download all document files from API and save to local directory.
    
    Args:
        api_key (str): API key for authentication
        documents_file (str): Path to documents JSON file
        output_dir (str): Directory to save downloaded files
    """
    
    # Load documents metadata
    try:
        with open(documents_file, 'r', encoding='utf-8') as f:
            documents = json.load(f)
    except FileNotFoundError:
        print(f"Error: Documents file '{documents_file}' not found.")
        print("Please run fetch_products_api.py first to generate documents.json")
        return False
    except json.JSONDecodeError as e:
        print(f"Error: Failed to parse documents file: {e}")
        return False
    
    if not documents:
        print("No documents found in documents file.")
        return True
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    # API configuration
    base_url = 'https://lager.asvig.com'
    endpoint = 'documents/download'
    url = f'{base_url}/api/index.php/{endpoint}'
    
    # Headers with API key
    headers = {
        'DOLAPIKEY': api_key,
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    print(f"\nDownloading documents from: {url}")
    print(f"Processing {len(documents)} document records...\n")
    
    successful_downloads = 0
    failed_downloads = 0
    skipped = 0
    
    for idx, doc in enumerate(documents, 1):
        # Extract required fields
        filepath = doc.get('filepath', '')
        filename = doc.get('filename', '')
        product_ref = doc.get('product_ref', 'unknown')
        
        if not filepath or not filename:
            print(f"  [{idx}/{len(documents)}] Skipping (missing filepath or filename)")
            skipped += 1
            continue
        
        # Build original_file parameter:
        # Remove "produit/" prefix from filepath, then add "/" and filename
        if filepath.startswith('produit/'):
            path_without_prefix = filepath[8:]  # Remove "produit/"
        else:
            path_without_prefix = filepath
        
        original_file = f"{path_without_prefix}/{filename}"
        
        # Build request parameters
        params = {
            'modulepart': 'produit',
            'original_file': original_file
        }
        
        print(f"  [{idx}/{len(documents)}] {filename} (product: {product_ref})...", end='', flush=True)
        
        try:
            # Make GET request
            response = requests.get(url, headers=headers, params=params, timeout=60)
            
            # Check if request was successful
            response.raise_for_status()
            
            # Parse JSON response
            data = response.json()
            
            # Validate response has required fields
            if 'content' not in data or 'encoding' not in data:
                print(f" ERROR: Response missing content or encoding")
                failed_downloads += 1
                continue
            
            # Decode base64 content
            if data['encoding'] == 'base64':
                try:
                    file_content = base64.b64decode(data['content'])
                except Exception as e:
                    print(f" ERROR: Failed to decode base64: {e}")
                    failed_downloads += 1
                    continue
            else:
                print(f" ERROR: Unsupported encoding: {data['encoding']}")
                failed_downloads += 1
                continue
            
            # Create subdirectory for product if needed
            product_dir = os.path.join(output_dir, path_without_prefix)
            os.makedirs(product_dir, exist_ok=True)
            
            # Save file
            output_path = os.path.join(product_dir, filename)
            with open(output_path, 'wb') as f:
                f.write(file_content)
            
            file_size_kb = len(file_content) / 1024
            print(f" ✓ ({file_size_kb:.1f} KB)")
            successful_downloads += 1
            
        except RequestException as e:
            print(f" ERROR: {e}")
            failed_downloads += 1
            continue
        except Exception as e:
            print(f" ERROR: {type(e).__name__}: {e}")
            failed_downloads += 1
            continue
    
    # Print summary
    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    print(f"Total documents: {len(documents)}")
    print(f"✓ Successfully downloaded: {successful_downloads}")
    print(f"✗ Failed downloads: {failed_downloads}")
    print(f"⊘ Skipped (missing data): {skipped}")
    print(f"\nFiles saved to: {os.path.abspath(output_dir)}")
    
    return failed_downloads == 0


def main():
    """Main function with command-line interface."""
    
    # Default API key
    default_api_key = 'ah9jP9o3rIPO22znqXo28cHdP9W7FT7R'
    default_documents_file = 'documents.json'
    default_output_dir = 'downloaded_documents'
    
    # Parse command line arguments
    if len(sys.argv) == 1:
        # Use defaults
        api_key = default_api_key
        documents_file = default_documents_file
        output_dir = default_output_dir
    elif len(sys.argv) == 2:
        # Custom API key provided
        api_key = sys.argv[1]
        documents_file = default_documents_file
        output_dir = default_output_dir
    elif len(sys.argv) == 4:
        # Custom API key, documents file, and output directory
        api_key = sys.argv[1]
        documents_file = sys.argv[2]
        output_dir = sys.argv[3]
    else:
        print("Usage: python download_documents.py [api_key] [documents_file] [output_dir]")
        print(f"  Default API key: {default_api_key[:10]}...")
        print(f"  Default documents file: {default_documents_file}")
        print(f"  Default output directory: {default_output_dir}")
        sys.exit(1)
    
    # Download documents
    success = download_documents(api_key, documents_file, output_dir)
    
    if not success:
        print("\nSome downloads failed. Please check:")
        print("1. API key is correct")
        print("2. Network connection")
        print("3. API endpoint availability")
        print("4. Document paths are correct")
        sys.exit(1)
    else:
        print("\n✓ All documents downloaded successfully!")


if __name__ == '__main__':
    main()
