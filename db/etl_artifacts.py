from pymongo import MongoClient
from datetime import datetime, timezone
from db.check_server import check_mongo_server
import os


class ETLArtifacts:
    def __init__(self, mongo_uri=os.environ.get("MONGO_URI", "mongodb://localhost:27017/"), db_name="StockDB",
                 collection_name="ETLArtifacts"):
        """
        Initializes the ETLArtifacts class.

        Parameters:
            mongo_uri (str): MongoDB connection URI.
            db_name (str): Name of the MongoDB database.
            collection_name (str): Collection name for ETL artifacts.
        """
        check_mongo_server()
        self.client = MongoClient(mongo_uri)
        self.etl_db = self.client[db_name]
        self.etl_collection = self.etl_db[collection_name]
        self.run_id = 0

    def create_first_etl_art_doc(self, ticker_list):
        """
        Creates the first ETL artifacts document if it does not already exist.

        Parameters:
            ticker_list (list): List of tickers present in the input data.
        """
        print("Creating first ETLArtifacts document...")
        current_timestamp = datetime.now(timezone.utc)
        first_doc = {
            "$set": {
                "run_timestamp": current_timestamp,
                "entry_ticker_list": ticker_list
            }
        }
        self.etl_collection.update_one({ "run_id": self.run_id}, first_doc, upsert=True)
        print("ETL Artifacts document created successfully.")
        index_result = self.etl_collection.create_index([("run_timestamp", 1)])
        print("Created index on ETLArtifacts:", index_result)

    def update_etl_artifacts(self, missing_tickers, new_tickers, tickers_to_update, skip_writing):
        """
        Updates the ETL artifacts document with run details.

        Parameters:
            missing_tickers (list): Tickers missing in input.
            new_tickers (list): New tickers found in input.
            tickers_to_update (list): Tickers requiring updates.
            skip_writing: It
        """

        current_timestamp = datetime.now(timezone.utc)
        latest_doc = self.etl_collection.find_one({}, sort=[("run_timestamp", -1)])
        #  Update run_id
        self.run_id = latest_doc.get("run_id", 0) + 1 if latest_doc else 0

        update_doc = {
            "$set": {
                "run_timestamp": current_timestamp,
                "missing_tickers": missing_tickers,
                "new_tickers": new_tickers,
                "tickers_to_update": tickers_to_update,
                "skip_writing": skip_writing
            }
        }
        self.etl_collection.update_one({ "run_id": self.run_id}, update_doc, upsert=True)
        print("ETL Artifacts updated successfully.")

    def get_artifacts_by_run_id(self, run_id):
        if self.etl_collection.count_documents({}) == 0:
            print("Collection is empty or does not exist.")
            return {}
        return self.etl_collection.find_one({"run_id": run_id})
