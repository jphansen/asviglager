#!/usr/bin/env python3
"""
Migrate flat warehouse structure to three-tier hierarchy.

This script:
1. Creates a "Default Warehouse" (type=warehouse)
2. Creates a "Default Location" under the warehouse (type=location)
3. Converts all existing warehouse records to containers (type=container)
4. Links all containers to the default location
5. Attempts to detect and set container types from labels
6. Product stock_warehouse references remain unchanged (still use container refs)
"""

import asyncio
import sys
import os
from datetime import datetime
import re

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from app.models.warehouse import WarehouseType, ContainerType


# Container type detection patterns
CONTAINER_TYPE_PATTERNS = {
    ContainerType.BOX: [r'\bbox\b', r'\bBOX\b', r'\bboks\b'],
    ContainerType.CASE: [r'\bcase\b', r'\bkasse\b', r'\bKasse\b'],
    ContainerType.SUITCASE: [r'\bsuitcase\b', r'\bkuffert\b'],
    ContainerType.IKEA_BOX: [r'\bikea.*box\b', r'\bikea.*kasse\b', r'\bikea.*\u00e6ske\b'],
    ContainerType.IKEA_CASE: [r'\bikea.*case\b'],
    ContainerType.STORAGE_BIN: [r'\bbin\b', r'\bopbevaring\b'],
    ContainerType.WRAP: [r'\bwrap\b', r'\bindpakning\b'],
    ContainerType.PALLET: [r'\bpallet\b'],
    ContainerType.SHELF: [r'\bshelf\b', r'\bhylde\b'],
    ContainerType.DRAWER: [r'\bdrawer\b', r'\bskuffe\b'],
}


def detect_container_type(label: str, description: str = None) -> ContainerType:
    """Detect container type from label and description."""
    text = f"{label} {description or ''}".lower()
    
    for container_type, patterns in CONTAINER_TYPE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return container_type
    
    return ContainerType.OTHER


async def migrate_warehouse_hierarchy():
    """Main migration function."""
    
    print("=" * 80)
    print("WAREHOUSE HIERARCHY MIGRATION")
    print("=" * 80)
    print()
    
    # Connect to MongoDB
    print(f"Connecting to MongoDB: {settings.mongodb_uri}")
    client = AsyncIOMotorClient(settings.mongodb_uri)
    db = client[settings.mongodb_db_name]
    warehouses_collection = db.warehouses
    products_collection = db.products
    
    # Get counts before migration
    existing_warehouses = await warehouses_collection.count_documents({"deleted": False})
    print(f"Found {existing_warehouses} existing warehouse records")
    print()
    
    # Check if migration already run
    existing_hierarchy = await warehouses_collection.find_one({"type": {"$exists": True}})
    if existing_hierarchy:
        print("⚠️  WARNING: Migration appears to have been run already!")
        print("   Found records with 'type' field. Continue anyway? (y/N): ", end="")
        response = input().strip().lower()
        if response != 'y':
            print("Migration cancelled.")
            return
        print()
    
    # Step 1: Create Default Warehouse
    print("Step 1: Creating Default Warehouse...")
    default_warehouse = {
        "ref": "MAIN",
        "label": "Default Warehouse",
        "type": WarehouseType.WAREHOUSE.value,
        "description": "Main warehouse - automatically created during migration",
        "short": "MAIN",
        "address": None,  # Can be updated by admin later
        "zip": None,
        "town": None,
        "phone": None,
        "fax": None,
        "container_type": None,
        "fk_parent": None,
        "status": True,
        "deleted": False,
        "deleted_at": None,
        "date_creation": datetime.utcnow(),
        "date_modification": datetime.utcnow(),
    }
    
    result = await warehouses_collection.insert_one(default_warehouse)
    warehouse_id = str(result.inserted_id)
    print(f"✓ Created Default Warehouse (ID: {warehouse_id})")
    print()
    
    # Step 2: Create Default Location
    print("Step 2: Creating Default Location...")
    default_location = {
        "ref": "DEFAULT",
        "label": "Default Location",
        "type": WarehouseType.LOCATION.value,
        "description": "Default storage location - automatically created during migration",
        "short": "DEF",
        "address": None,
        "zip": None,
        "town": None,
        "phone": None,
        "fax": None,
        "container_type": None,
        "fk_parent": warehouse_id,
        "status": True,
        "deleted": False,
        "deleted_at": None,
        "date_creation": datetime.utcnow(),
        "date_modification": datetime.utcnow(),
    }
    
    result = await warehouses_collection.insert_one(default_location)
    location_id = str(result.inserted_id)
    print(f"✓ Created Default Location (ID: {location_id})")
    print()
    
    # Step 3: Convert existing warehouses to containers
    print("Step 3: Converting existing warehouses to containers...")
    print("-" * 80)
    
    # Get all existing warehouses (without type field)
    cursor = warehouses_collection.find({"deleted": False, "type": {"$exists": False}})
    existing_records = await cursor.to_list(length=None)
    
    if not existing_records:
        print("No existing warehouse records to convert")
    else:
        converted_count = 0
        type_stats = {}
        
        for record in existing_records:
            record_id = record['_id']
            ref = record.get('ref', 'UNKNOWN')
            label = record.get('label', '')
            description = record.get('description', '')
            
            # Detect container type
            container_type = detect_container_type(label, description)
            
            # Update type stats
            type_stats[container_type] = type_stats.get(container_type, 0) + 1
            
            # Update record
            update_data = {
                "$set": {
                    "type": WarehouseType.CONTAINER.value,
                    "container_type": container_type.value,
                    "fk_parent": location_id,
                    "date_modification": datetime.utcnow(),
                },
                "$unset": {
                    # Remove address fields from containers
                    "address": "",
                    "zip": "",
                    "town": "",
                    "phone": "",
                    "fax": "",
                }
            }
            
            await warehouses_collection.update_one({"_id": record_id}, update_data)
            converted_count += 1
            
            print(f"  [{converted_count}/{len(existing_records)}] {ref}: {label[:50]}... → {container_type.value}")
        
        print()
        print(f"✓ Converted {converted_count} warehouses to containers")
        print()
        print("Container type distribution:")
        for ctype, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {ctype.value}: {count}")
        print()
    
    # Step 4: Verify product stock references
    print("Step 4: Verifying product stock references...")
    products_with_stock = await products_collection.count_documents({
        "stock_warehouse": {"$exists": True, "$ne": {}}
    })
    print(f"✓ Found {products_with_stock} products with stock data")
    print("  (No changes needed - stock references remain as container refs)")
    print()
    
    # Step 5: Create indexes
    print("Step 5: Creating indexes...")
    await warehouses_collection.create_index("type")
    await warehouses_collection.create_index("fk_parent")
    await warehouses_collection.create_index([("type", 1), ("deleted", 1), ("status", 1)])
    await warehouses_collection.create_index("container_type")
    print("✓ Created indexes on type, fk_parent, container_type")
    print()
    
    # Migration summary
    print("=" * 80)
    print("MIGRATION SUMMARY")
    print("=" * 80)
    total_records = await warehouses_collection.count_documents({"deleted": False})
    warehouses = await warehouses_collection.count_documents({"type": WarehouseType.WAREHOUSE.value, "deleted": False})
    locations = await warehouses_collection.count_documents({"type": WarehouseType.LOCATION.value, "deleted": False})
    containers = await warehouses_collection.count_documents({"type": WarehouseType.CONTAINER.value, "deleted": False})
    
    print(f"Total records:        {total_records}")
    print(f"  - Warehouses:       {warehouses}")
    print(f"  - Locations:        {locations}")
    print(f"  - Containers:       {containers}")
    print()
    print("Hierarchy structure:")
    print(f"  {default_warehouse['label']} ({default_warehouse['ref']})")
    print(f"    └── {default_location['label']} ({default_location['ref']})")
    print(f"          └── {containers} containers")
    print()
    print("✓ Migration completed successfully!")
    print()
    print("Next steps:")
    print("  1. Review the default warehouse/location and update addresses if needed")
    print("  2. Review container types and correct any misclassifications")
    print("  3. Create additional warehouses/locations as needed")
    print("  4. Move containers to appropriate locations using the admin interface")
    print()
    
    client.close()


if __name__ == '__main__':
    asyncio.run(migrate_warehouse_hierarchy())
