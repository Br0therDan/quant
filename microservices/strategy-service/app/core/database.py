# """
# Database configuration and connectivity
# """

# import os
# from typing import Dict, Any
# from motor.motor_asyncio import AsyncIOMotorClient
# from beanie import init_beanie
# import asyncio

# from app.models.strategy import (
#     Strategy,
#     StrategyTemplate,
#     StrategyExecution,
#     StrategyPerformance,
# )

# # MongoDB configuration
# MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
# DATABASE_NAME = os.getenv("DATABASE_NAME", "quant_strategy")

# # Global MongoDB client and database
# client: AsyncIOMotorClient | None = None
# database = None


# async def connect_to_database():
#     """Initialize database connection and Beanie ODM"""
#     global client, database

#     try:
#         # Create MongoDB client
#         client = AsyncIOMotorClient(MONGODB_URL)
#         database = client[DATABASE_NAME]

#         # Initialize Beanie with document models
#         await init_beanie(
#             database=database,
#             document_models=[
#                 Strategy,
#                 StrategyTemplate,
#                 StrategyExecution,
#                 StrategyPerformance,
#             ],
#         )

#         print(f"Connected to MongoDB: {DATABASE_NAME}")
#         return True

#     except Exception as e:
#         print(f"Failed to connect to MongoDB: {e}")
#         return False


# async def close_database_connection():
#     """Close database connection"""
#     global client

#     if client:
#         client.close()
#         print("Disconnected from MongoDB")


# async def get_database_status() -> Dict[str, Any]:
#     """Check database connection status"""
#     global client, database

#     try:
#         if not client or not database:
#             return {"connected": False, "error": "No database connection"}

#         # Ping the database
#         await client.admin.command("ping")

#         # Get server info
#         server_info = await client.server_info()

#         # Get database stats
#         stats = await database.command("dbStats")

#         return {
#             "connected": True,
#             "server_version": server_info.get("version", "unknown"),
#             "database_name": DATABASE_NAME,
#             "collections_count": stats.get("collections", 0),
#             "data_size": stats.get("dataSize", 0),
#             "storage_size": stats.get("storageSize", 0),
#             "indexes": stats.get("indexes", 0),
#         }

#     except Exception as e:
#         return {"connected": False, "error": str(e)}
