#!/usr/bin/env python3
"""
Create an admin user in the MongoDB database.

This script creates a default admin user with credentials:
- Username: admin
- Password: admin123

IMPORTANT: Change this password after first login!
"""
import sys
import asyncio
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.security import get_password_hash
from app.core.logging import logger
from app.db.mongodb import MongoDB
from app.core.config import settings


async def create_admin_user():
    """Create the admin user if it doesn't exist."""
    logger.info("Creating admin user")
    
    try:
        # Connect to MongoDB
        await MongoDB.connect_db()
        db = MongoDB.get_db()
        users_collection = db.users
        
        # Check if admin already exists
        existing_admin = await users_collection.find_one({"username": "admin"})
        
        if existing_admin:
            logger.warning("Admin user already exists — skipping creation")
            return
        
        # Create admin user
        admin_user = {
            "username": "admin",
            "email": "admin@example.com",
            "hashed_password": get_password_hash("admin123"),
            "is_active": True
        }
        
        result = await users_collection.insert_one(admin_user)
        
        if result.inserted_id:
            logger.info("Admin user created successfully")
        else:
            logger.error("Failed to create admin user")
    
    except Exception as e:
        logger.error("Error creating admin user", fields={"error": str(e)})
        raise
    
    finally:
        await MongoDB.close_db()


if __name__ == "__main__":
    asyncio.run(create_admin_user())
