from pymongo import MongoClient
from datetime import datetime, timezone


class ETLArtifacts:
    def __init__(self, mongo_uri="mongodb://localhost:27017/", db_name="StockDB",
                 collection_name="ETLArtifacts"):
        """
        Initializes the StockDataArtifacts class.

        Parameters:
            mongo_uri (str): MongoDB connection URI.
            db_name (str): The database name where artifacts are stored.
            collection_name (str): The collection name for the artifacts.
        """
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection_name = collection_name

    def create_first_etl_art_doc(self, run_id, ticker_list):
        print("Creating first ETLArtifacts collection")
        first_doc = {
            "$set": {
                "run_id": run_id,
                "run_counter": 0,
                "entry_ticker_list": ticker_list
            }
        }

        # Get the current UTC timestamp as a timezone-aware datetime object
        current_timestamp = datetime.now(timezone.utc)

        # Update the document for run_timestamp. Upsert = True will insert if the document doesn't exist.
        self.db[self.collection_name].update_one({"run_timestamp": current_timestamp}, first_doc, upsert=True)
        print("ETL Artifacts created successfully.")

        index_result = self.db[self.collection_name].create_index([("run_timestamp", 1)])
        print("Created index on ETLArtifacts:", index_result)


    def update_etl_artifacts(self, run_id, missing_tickers, new_tickers, tickers_to_update):

        # Get the current UTC timestamp as a timezone-aware datetime object
        current_timestamp = datetime.now(timezone.utc)

        # collect run_counter from latest run_timestamp, then add 1
        latest_doc = self.db[self.collection_name].find_one({}, sort=[("run_timestamp", -1)])
        current_run_counter = latest_doc.get("run_counter") + 1

        # Create the update document
        update_doc = {
            "$set": {
                "run_id": run_id,
                "run_counter": current_run_counter,
                "missing_tickers": missing_tickers,
                "new_tickers": new_tickers,
                "tickers_to_update": tickers_to_update
            }
        }

        # Update the document for run_timestamp. Upsert = True will insert if the document doesn't exist.
        self.db[self.collection_name].update_one({"run_timestamp": current_timestamp}, update_doc, upsert=True)

        print("ETL Artifacts updated successfully.")