"""Bot database connection."""
import motor.motor_asyncio

db = motor.motor_asyncio.AsyncIOMotorClient("mongo").crabot
