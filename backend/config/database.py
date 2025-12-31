"""
MongoDB database connection and configuration
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Global database client
db_client: AsyncIOMotorClient = None


async def connect_db():
    """Connect to MongoDB and initialize Beanie ODM"""
    global db_client
    
    try:
        # Create MongoDB client
        db_client = AsyncIOMotorClient(settings.MONGODB_URI)
        
        # Ping to verify connection
        await db_client.admin.command('ping')
        
        # Get database
        db = db_client.get_default_database()
        
        # Import all models
        from models.user import User
        from models.note import Note
        from models.person import Person
        from models.meeting import Meeting
        from models.reminder import Reminder
        from models.relationship import Relationship
        
        # Initialize Beanie with all models
        await init_beanie(
            database=db,
            document_models=[
                User,
                Note,
                Person,
                Meeting,
                Reminder,
                Relationship
            ]
        )
        
        logger.info("Successfully connected to MongoDB")
        
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise


async def close_db():
    """Close MongoDB connection"""
    global db_client
    
    if db_client:
        db_client.close()
        logger.info("Closed MongoDB connection")


def get_db():
    """Get database instance"""
    if db_client:
        return db_client.get_default_database()
    raise Exception("Database not initialized")
