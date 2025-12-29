#!/usr/bin/env python3
"""
Import Dolibarr products from dcjph-products.json into MongoDB.

This script:
1. Reads the Dolibarr products JSON file
2. Converts data types (timestamps, prices, booleans)
3. Handles UTF-8 encoding for Danish/Swedish characters
4. Preserves all Dolibarr fields
5. Uses upsert logic (updates existing products by ref)
6. Shows progress during import
"""
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.models.product import ProductFull
from app.db.mongodb import MongoDB
from app.core.config import settings


def convert_dolibarr_product(dolibarr_data: dict) -> dict:
    """
    Convert Dolibarr product data to our MongoDB format.
    Handles type conversions and field mappings.
    """
    # Make a copy to avoid modifying original
    data = dolibarr_data.copy()
    
    # Convert Unix timestamps to datetime objects
    timestamp_fields = ["date_creation", "date_modification"]
    for field in timestamp_fields:
        if field in data and isinstance(data[field], int) and data[field] > 0:
            try:
                data[field] = datetime.fromtimestamp(data[field])
            except Exception as e:
                print(f"  Warning: Failed to convert {field}: {e}")
                data[field] = datetime.utcnow()
    
    # Store original Dolibarr ID
    if "id" in data:
        data["dolibarr_id"] = str(data["id"])
        del data["id"]
    
    # Convert price strings to Decimal
    price_fields = [
        "price", "price_ttc", "price_min", "price_min_ttc", 
        "cost_price", "pmp", "tva_tx", "localtax1_tx", "localtax2_tx"
    ]
    for field in price_fields:
        if field in data and data[field] is not None:
            try:
                if isinstance(data[field], str):
                    # Convert to float for MongoDB (Decimal not supported)
                    data[field] = float(data[field])
                elif isinstance(data[field], (int, float)):
                    data[field] = float(data[field])
                elif isinstance(data[field], Decimal):
                    data[field] = float(data[field])
            except Exception as e:
                print(f"  Warning: Failed to convert {field} to float: {e}")
                data[field] = None
    
    # Convert dimension fields to float
    dimension_fields = ["weight", "length", "width", "height", "surface", "volume"]
    for field in dimension_fields:
        if field in data and data[field] is not None:
            try:
                data[field] = float(str(data[field]))
            except Exception:
                data[field] = None
    
    # Convert string "0"/"1" to boolean for certain fields
    # Note: Keeping type, status, etc. as strings since that's what the model expects
    
    # Handle empty strings - convert to None for optional fields
    for key, value in list(data.items()):
        if value == "":
            data[key] = None
    
    # Add soft delete fields
    data["deleted"] = False
    data["deleted_at"] = None
    
    # Ensure required fields have defaults
    if "date_creation" not in data or data["date_creation"] is None:
        data["date_creation"] = datetime.utcnow()
    if "date_modification" not in data or data["date_modification"] is None:
        data["date_modification"] = datetime.utcnow()
    
    return data


async def import_dolibarr_products():
    """Import Dolibarr products from JSON file."""
    # Path to the products JSON file (in parent directory)
    products_file = Path(__file__).parent.parent.parent / "products.json"
    
    if not products_file.exists():
        print(f"✗ Products file not found: {products_file}")
        print(f"  Expected location: {products_file.absolute()}")
        return
    
    print(f"📂 Reading products from: {products_file.name}")
    
    # Read JSON file with UTF-8 encoding
    try:
        with open(products_file, "r", encoding="utf-8") as f:
            dolibarr_products = json.load(f)
    except Exception as e:
        print(f"✗ Error reading JSON file: {e}")
        return
    
    if not isinstance(dolibarr_products, list):
        print(f"✗ Expected a list of products, got: {type(dolibarr_products)}")
        return
    
    total_products = len(dolibarr_products)
    print(f"📊 Found {total_products} products to import")
    print()
    
    # Connect to MongoDB
    print("🔌 Connecting to MongoDB...")
    await MongoDB.connect_db()
    db = MongoDB.get_db()
    products_collection = db.products
    
    # Import products with progress
    imported_count = 0
    updated_count = 0
    error_count = 0
    
    print("🚀 Starting import...")
    print()
    
    for idx, dolibarr_product in enumerate(dolibarr_products, 1):
        try:
            # Convert product data
            product_data = convert_dolibarr_product(dolibarr_product)
            
            # Get ref for identification
            ref = product_data.get("ref", "UNKNOWN")
            label = product_data.get("label", "No label")
            
            # Check if product already exists (by ref)
            existing = await products_collection.find_one({"ref": ref})
            
            if existing:
                # Update existing product
                # Remove fields that shouldn't be updated
                update_data = {k: v for k, v in product_data.items() if k not in ["_id"]}
                
                await products_collection.update_one(
                    {"ref": ref},
                    {"$set": update_data}
                )
                updated_count += 1
                action = "UPDATED"
            else:
                # Insert new product
                await products_collection.insert_one(product_data)
                imported_count += 1
                action = "IMPORTED"
            
            # Progress indicator (every 10 products)
            if idx % 10 == 0 or idx == total_products:
                print(f"  [{idx}/{total_products}] {action}: {ref} - {label[:50]}")
        
        except Exception as e:
            error_count += 1
            ref = dolibarr_product.get("ref", "UNKNOWN")
            print(f"  ✗ Error importing {ref}: {e}")
    
    print()
    print("=" * 60)
    print("📋 Import Summary:")
    print(f"  Total products processed: {total_products}")
    print(f"  ✓ New products imported: {imported_count}")
    print(f"  ↻ Existing products updated: {updated_count}")
    print(f"  ✗ Errors: {error_count}")
    print("=" * 60)
    
    await MongoDB.close_db()
    
    if error_count == 0:
        print("✓ Import completed successfully!")
    else:
        print(f"⚠️  Import completed with {error_count} errors")


if __name__ == "__main__":
    asyncio.run(import_dolibarr_products())
