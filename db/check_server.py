import sys
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
import os


def check_mongo_server(mongo_uri = os.environ.get("MONGO_URI", "mongodb://localhost:27017/"), timeout_ms=3000):
    """
    Checks if the MongoDB server is running by attempting to ping it.

    Parameters:
        mongo_uri (str): MongoDB connection URI.
        timeout_ms (int): Timeout in milliseconds for the server selection.

    Returns:
        bool: True if the server is running, False otherwise.
    """
    try:
        # Set a short timeout to avoid waiting too long
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=timeout_ms)
        # The ping command is used to check the server status.
        client.admin.command('ping')
        print("MongoDB server is running.")
        return True
    except ServerSelectionTimeoutError:
        raise Exception(f"MongoDB server is not running. Please start the server")



# Example usage in your main script
if __name__ == "__main__":
    if not check_mongo_server():
        sys.exit(1)
