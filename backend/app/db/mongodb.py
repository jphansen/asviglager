"""MongoDB database connection and lifecycle management."""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

from app.core.config import settings
from app.core.logging import logger


class MongoDB:
    """MongoDB connection manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    
    @classmethod
    async def connect_db(cls):
        """Connect to MongoDB."""
        try:
            cls.client = AsyncIOMotorClient(settings.mongodb_uri)
            # Test the connection
            await cls.client.admin.command('ping')
            logger.info(f"Connected to MongoDB", fields={"db": settings.mongodb_db_name})
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB", fields={"error": str(e)})
            raise
    
    @classmethod
    async def close_db(cls):
        """Close MongoDB connection."""
        if cls.client:
            cls.client.close()
            logger.info("Closed MongoDB connection")
    
    @classmethod
    def get_db(cls):
        """Get database instance."""
        if not cls.client:
            raise RuntimeError("Database not connected. Call connect_db() first.")
        return cls.client[settings.mongodb_db_name]
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a specific collection."""
        db = cls.get_db()
        return db[collection_name]


# Convenience function for dependency injection
def get_database():
    """Dependency for getting database instance in route handlers."""
    return MongoDB.get_db()
