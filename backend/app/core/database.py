from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId


MONGO_URL = "mongodb://root:root@localhost:27017/?authSource=admin"
DB_NAME = "UTEZone"

client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

def obj_id(o):
    if isinstance(o, ObjectId):
        return str(o)
    return o

async def init_db():
    try:
        await client.admin.command("ping")
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
