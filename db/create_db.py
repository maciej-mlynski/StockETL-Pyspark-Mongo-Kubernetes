from pymongo import MongoClient
from datetime import datetime
from check_server import check_mongo_server
import sys, os


def create_databases():
    """
    Connects to the MongoDB server and creates two databases:
      - StockDataArtifacts: stores Stock Data artifacts like current row count, start date, end date last_update for given ticker
      - ETLArtifacts: stores ETL artifacts like new tickers founded, missing tickers, gaps after each new ETL run for each new day inserted

    If a database already exists (i.e. it appears in client.list_database_names()),
    it prints a message indicating that creation is skipped. Otherwise, it creates
    the database by inserting an initial record into a 'metadata' collection.
    """
    if not check_mongo_server():
        sys.exit(1)

    # Connect to MongoDB server (adjust the URI as needed)
    client = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017/"))

    # Access the databases (they will be created when data is inserted)
    stock_data_db = client["StockDB"]

    if stock_data_db.name in client.list_database_names():
        print(f"Database '{stock_data_db.name}' already exists, skipping creation.")
    else:
        # Insert an initial record into a 'metadata' collection
        stock_data_db.metadata.insert_one({"created": True, "timestamp": datetime.now()})
        print(f"Database '{stock_data_db.name}' has been created with an initial record.")


if __name__ == "__main__":
    create_databases()
