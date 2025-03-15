from pymongo import MongoClient
from datetime import datetime, timezone


class ETLArtifacts:
    def __init__(self, mongo_uri="mongodb://localhost:27017/", db_name="StockDB",
                 collection_name="ETLArtifacts"):
        """
        Initializes the ETLArtifacts class.

        Parameters:
            mongo_uri (str): MongoDB connection URI.
            db_name (str): Name of the MongoDB database.
            collection_name (str): Collection name for ETL artifacts.
        """
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection_name = collection_name

    def create_first_etl_art_doc(self, run_id, ticker_list):
        """
        Creates the first ETL artifacts document if it does not already exist.

        Parameters:
            run_id (str): Run identifier.
            ticker_list (list): List of tickers present in the input data.
        """
        print("Creating first ETLArtifacts document...")
        first_doc = {
            "$set": {
                "run_id": run_id,
                "run_counter": 0,
                "entry_ticker_list": ticker_list
            }
        }
        current_timestamp = datetime.now(timezone.utc)
        self.db[self.collection_name].update_one({"run_timestamp": current_timestamp}, first_doc, upsert=True)
        print("ETL Artifacts document created successfully.")
        index_result = self.db[self.collection_name].create_index([("run_timestamp", 1)])
        print("Created index on ETLArtifacts:", index_result)

    def update_etl_artifacts(self, run_id, missing_tickers, new_tickers, tickers_to_update, skip_writing):
        """
        Updates the ETL artifacts document with run details.

        Parameters:
            run_id (str): Run identifier.
            missing_tickers (list): Tickers missing in input.
            new_tickers (list): New tickers found in input.
            tickers_to_update (list): Tickers requiring updates.
        """
        current_timestamp = datetime.now(timezone.utc)
        latest_doc = self.db[self.collection_name].find_one({}, sort=[("run_timestamp", -1)])
        current_run_counter = latest_doc.get("run_counter", 0) + 1 if latest_doc else 1

        update_doc = {
            "$set": {
                "run_id": run_id,
                "run_counter": current_run_counter,
                "missing_tickers": missing_tickers,
                "new_tickers": new_tickers,
                "tickers_to_update": tickers_to_update,
                "skip_writing": skip_writing
            }
        }
        self.db[self.collection_name].update_one({"run_timestamp": current_timestamp}, update_doc, upsert=True)
        print("ETL Artifacts updated successfully.")
