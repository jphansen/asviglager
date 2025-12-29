"""MongoDB index creation and management."""
from motor.motor_asyncio import AsyncIOMotorDatabase
import pymongo


async def create_indexes(db: AsyncIOMotorDatabase):
    """Create all necessary indexes for the application."""
    
    # Products collection indexes
    products_collection = db.products
    
    try:
        # Create unique index on ref (product reference number)
        await products_collection.create_index(
            "ref",
            unique=True,
            name="idx_ref_unique"
        )
        print("✓ Created unique index on products.ref")
        
        # Create regular index on barcode for lookup (not unique since many products have null)
        await products_collection.create_index(
            "barcode",
            name="idx_barcode"
        )
        print("✓ Created index on products.barcode")
        
        # Create text index on label for full-text search
        await products_collection.create_index(
            [("label", pymongo.TEXT)],
            name="idx_label_text"
        )
        print("✓ Created text index on products.label")
        
        # Create index on date_creation for sorting
        await products_collection.create_index(
            [("date_creation", pymongo.DESCENDING)],
            name="idx_date_creation_desc"
        )
        print("✓ Created index on products.date_creation")
        
        # Create index on deleted field for filtering
        await products_collection.create_index(
            "deleted",
            name="idx_deleted"
        )
        print("✓ Created index on products.deleted")
        
        # Create compound index for common queries
        await products_collection.create_index(
            [("deleted", pymongo.ASCENDING), ("date_creation", pymongo.DESCENDING)],
            name="idx_deleted_date_compound"
        )
        print("✓ Created compound index on products.deleted + date_creation")
        
    except Exception as e:
        print(f"✗ Error creating products indexes: {e}")
        raise
    
    # Users collection indexes
    users_collection = db.users
    
    try:
        # Create unique index on username
        await users_collection.create_index(
            "username",
            unique=True,
            name="idx_username_unique"
        )
        print("✓ Created unique index on users.username")
        
        # Create unique index on email (if provided)
        await users_collection.create_index(
            "email",
            unique=True,
            sparse=True,
            name="idx_email_unique_sparse"
        )
        print("✓ Created unique sparse index on users.email")
        
    except Exception as e:
        print(f"✗ Error creating users indexes: {e}")
        raise
    
    # Warehouses collection indexes
    warehouses_collection = db.warehouses
    
    try:
        # Create unique index on ref (warehouse reference code)
        await warehouses_collection.create_index(
            "ref",
            unique=True,
            name="idx_ref_unique"
        )
        print("✓ Created unique index on warehouses.ref")
        
        # Create text index on label and description for full-text search
        await warehouses_collection.create_index(
            [("label", pymongo.TEXT), ("description", pymongo.TEXT)],
            name="idx_label_description_text"
        )
        print("✓ Created text index on warehouses.label + description")
        
        # Create index on date_creation for sorting
        await warehouses_collection.create_index(
            [("date_creation", pymongo.DESCENDING)],
            name="idx_date_creation_desc"
        )
        print("✓ Created index on warehouses.date_creation")
        
        # Create index on deleted field for filtering
        await warehouses_collection.create_index(
            "deleted",
            name="idx_deleted"
        )
        print("✓ Created index on warehouses.deleted")
        
        # Create index on statut for filtering
        await warehouses_collection.create_index(
            "statut",
            name="idx_statut"
        )
        print("✓ Created index on warehouses.statut")
        
        # Create compound index for common queries
        await warehouses_collection.create_index(
            [("deleted", pymongo.ASCENDING), ("date_creation", pymongo.DESCENDING)],
            name="idx_deleted_date_compound"
        )
        print("✓ Created compound index on warehouses.deleted + date_creation")
        
    except Exception as e:
        print(f"✗ Error creating warehouses indexes: {e}")
        raise
    
    print("✓ All indexes created successfully")
