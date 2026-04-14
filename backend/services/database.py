import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
client = None
db = None

def close_db():
    global client
    if client is not None:
        client.close()
        print("MongoDB connection closed.")

def get_db():
    global client, db
    if not MONGODB_URI or MONGODB_URI == "<YOUR_MONGODB_CONNECTION_STRING_HERE>":
        print("WARNING: MONGODB_URI is strictly required. No local fallback is allowed.")
        return None
    
    if client is None:
        client = AsyncIOMotorClient(MONGODB_URI)
        db = client["omnibooth_db"]
    return db
