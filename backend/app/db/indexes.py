"""MongoDB index creation and management."""
from motor.motor_asyncio import AsyncIOMotorDatabase
import pymongo

from app.core.logging import logger


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
        logger.info("Created unique index", fields={"collection": "products", "field": "ref"})
        
        # Create regular index on barcode for lookup (not unique since many products have null)
        await products_collection.create_index(
            "barcode",
            name="idx_barcode"
        )
        logger.info("Created index", fields={"collection": "products", "field": "barcode"})
        
        # Create text index on label for full-text search
        await products_collection.create_index(
            [("label", pymongo.TEXT)],
            name="idx_label_text"
        )
        logger.info("Created text index", fields={"collection": "products", "field": "label"})
        
        # Create index on date_creation for sorting
        await products_collection.create_index(
            [("date_creation", pymongo.DESCENDING)],
            name="idx_date_creation_desc"
        )
        logger.info("Created index", fields={"collection": "products", "field": "date_creation"})
        
        # Create index on deleted field for filtering
        await products_collection.create_index(
            "deleted",
            name="idx_deleted"
        )
        logger.info("Created index", fields={"collection": "products", "field": "deleted"})
        
        # Create compound index for common queries
        await products_collection.create_index(
            [("deleted", pymongo.ASCENDING), ("date_creation", pymongo.DESCENDING)],
            name="idx_deleted_date_compound"
        )
        logger.info("Created compound index", fields={"collection": "products", "fields": "deleted+date_creation"})
        
    except Exception as e:
        logger.error("Error creating products indexes", fields={"error": str(e)})
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
        logger.info("Created unique index", fields={"collection": "users", "field": "username"})
        
        # Create unique index on email (if provided)
        await users_collection.create_index(
            "email",
            unique=True,
            sparse=True,
            name="idx_email_unique_sparse"
        )
        logger.info("Created unique sparse index", fields={"collection": "users", "field": "email"})
        
    except Exception as e:
        logger.error("Error creating users indexes", fields={"error": str(e)})
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
        logger.info("Created unique index", fields={"collection": "warehouses", "field": "ref"})
        
        # Create text index on label and description for full-text search
        await warehouses_collection.create_index(
            [("label", pymongo.TEXT), ("description", pymongo.TEXT)],
            name="idx_label_description_text"
        )
        logger.info("Created text index", fields={"collection": "warehouses", "fields": "label+description"})
        
        # Create index on date_creation for sorting
        await warehouses_collection.create_index(
            [("date_creation", pymongo.DESCENDING)],
            name="idx_date_creation_desc"
        )
        logger.info("Created index", fields={"collection": "warehouses", "field": "date_creation"})
        
        # Create index on deleted field for filtering
        await warehouses_collection.create_index(
            "deleted",
            name="idx_deleted"
        )
        logger.info("Created index", fields={"collection": "warehouses", "field": "deleted"})
        
        # Create index on statut for filtering
        await warehouses_collection.create_index(
            "statut",
            name="idx_statut"
        )
        logger.info("Created index", fields={"collection": "warehouses", "field": "statut"})
        
        # Create compound index for common queries
        await warehouses_collection.create_index(
            [("deleted", pymongo.ASCENDING), ("date_creation", pymongo.DESCENDING)],
            name="idx_deleted_date_compound"
        )
        logger.info("Created compound index", fields={"collection": "warehouses", "fields": "deleted+date_creation"})
        
    except Exception as e:
        logger.error("Error creating warehouses indexes", fields={"error": str(e)})
        raise
    
    logger.info("All indexes created successfully")
