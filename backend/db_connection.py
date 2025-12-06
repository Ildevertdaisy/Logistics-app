
from motor.motor_asyncio import AsyncIOMotorClient
import logging


mongo_client = AsyncIOMotorClient("mongodb://mongodb:27017")


logger = logging.getLogger("uvicorn.error")


async def ping_mongo_db_server():
    try:
        await mongo_client.admin.command("ping")
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        raise e
