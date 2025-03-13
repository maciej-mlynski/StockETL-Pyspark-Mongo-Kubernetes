from pymongo import MongoClient
from datetime import datetime
from check_server import check_mongo_server
import sys


def create_databases():
    """
    Connects to the MongoDB server and creates two databases:
      - StockDataArtifacts: stores Stock Data artifacts like current row count, start date, end date last_update for given ticker
      - ETLArtifacts: stores ETL artifacts like new tickers founded, missing tickers, gaps after each new ETL run for each new day inserted
    A dummy document is inserted into a temporary collection to ensure the databases are created.
    """
    if not check_mongo_server():
        sys.exit(1)

    # Connect to MongoDB server (adjust the URI as needed)
    client = MongoClient("mongodb://localhost:27017/")

    # Access the databases (they will be created when data is inserted)
    stock_data_artifacts_db = client["StockDataArtifacts"]
    etl_artifacts_db = client["ETLArtifacts"]

    # Helper function to create dummy collection if not exists, insert dummy doc, then drop it
    def ensure_db_exists(db):
        if db.name in client.list_database_names():
            print(f"Database '{db.name}' already exists, skipping creation.")
        else:
            # Insert an initial record into a 'metadata' collection
            db.metadata.insert_one({"created": True, "timestamp": datetime.now()})
            print(f"Database '{db.name}' has been created with an initial record.")

    ensure_db_exists(stock_data_artifacts_db)
    ensure_db_exists(etl_artifacts_db)


if __name__ == "__main__":
    create_databases()
