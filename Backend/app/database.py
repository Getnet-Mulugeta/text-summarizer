from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "text_summarizer")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]

user_collection = database.get_collection("users")
message_collection = database.get_collection("messages")
history_collection = database.get_collection("history")
