import logging
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.config import settings
from app.models import User

logger = logging.getLogger(__name__)


class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None


db = Database()


async def connect_to_mongo():
    """Create database connection"""
    try:
        # Create Motor client
        db.client = AsyncIOMotorClient(
            settings.mongodb_url,
            maxPoolSize=10,
            minPoolSize=10,
            serverSelectionTimeoutMS=5000,
        )
        
        # Get database
        db.database = db.client[settings.database_name]
        
        # Initialize Beanie with the User model
        await init_beanie(
            database=db.database,
            document_models=[User],
        )
        
        # Test connection
        await db.client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB: {settings.database_name}")
        
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("MongoDB connection closed")


async def get_database():
    """Get database instance"""
    return db.database


async def check_database_health() -> bool:
    """Check if database connection is healthy"""
    try:
        if not db.client:
            return False
        
        # Ping the database
        await db.client.admin.command('ping')
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
