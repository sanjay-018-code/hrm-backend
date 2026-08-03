import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "hr_management_system").strip()

if not MONGO_URL:
    raise RuntimeError("MONGO_URL is not configured")

client = MongoClient(
    MONGO_URL,
    connect=False,
    serverSelectionTimeoutMS=5_000,
)
db = client[DB_NAME]

employees_collection = db["employees"]
users_collection = db["users"]
attendance_collection = db["attendance"]
leave_collection = db["leaves"]
payroll_collection = db["payroll"]
department_collection = db["department"]
recovery_requests_collection = db["account_recovery_requests"]


def check_database_connection() -> None:
    try:
        client.admin.command("ping")
    except PyMongoError as error:
        raise RuntimeError("MongoDB is unavailable") from error
