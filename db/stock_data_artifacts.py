from pymongo import MongoClient
from datetime import datetime, timezone
from db.check_server import check_mongo_server
import os


class StockDataArtifacts:
    def __init__(self, mongo_uri=os.environ["MONGO_URI"], db_name="StockDB",
                 collection_name="StockDataArtifacts"):
        """
        Initializes the StockDataArtifacts class.

        Parameters:
            mongo_uri (str): MongoDB connection URI.
            db_name (str): The database name where artifacts are stored.
            collection_name (str): The collection name for the artifacts.
        """
        check_mongo_server()
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.stock_collection = self.db[collection_name]

    def add_first_stock_artifacts(self, aggregated_df):
        """
        Creates initial stock artifacts by upserting aggregated data for each ticker.

        Parameters:
            aggregated_df (DataFrame): A Spark DataFrame aggregated by ticker containing:
                - ticker: the stock ticker.
                - row_count: number of records for that ticker.
                - oldest_date: the earliest date for that ticker.
                - newest_date: the latest date for that ticker.

        For each ticker, the method upserts a document with the following fields:
            - ticker
            - row_count
            - oldest_date
            - newest_date
            - last_update_date (current UTC timestamp)
        """
        # Collect the aggregated data from Spark DataFrame to a list of Row objects
        records = aggregated_df.collect()

        for record in records:
            ticker = record["ticker"]
            row_count = record["row_count"]
            oldest_date = record["oldest_date"]
            latest_date = record["latest_date"]

            # Get the current UTC timestamp as a timezone-aware datetime object
            current_timestamp = datetime.now(timezone.utc)

            # Create the update document
            update_doc = {
                "$set": {
                    "row_count": row_count,
                    "oldest_date": oldest_date,
                    "latest_date": latest_date,
                    "last_update_date": current_timestamp
                }
            }

            # Update the document for this ticker. Upsert = True will insert if the document doesn't exist.
            self.stock_collection.update_one({"ticker": ticker}, update_doc, upsert=True)

        print("Initial stock data artifacts added successfully.")

        # Create an index on the "ticker" field in the StockDataArtifacts collection
        index_result = self.stock_collection.create_index([("ticker", 1)])
        print("Created index on StockDataArtifacts:", index_result)

        # Optionally, create a compound index on "ticker" and "newest_date"
        compound_index = self.stock_collection.create_index([("ticker", 1), ("latest_date", 1)])
        print("Created compound index on StockDataArtifacts:", compound_index)

    def export_ticker_data_from_mongo(self):
        """
        Exports ticker data from the StockDataArtifacts collection as a dictionary.
        Checks if the collection contains any documents; if not, returns an empty dictionary.

        Returns:
            dict: Mapping of ticker to latest_date.
        """
        # Check if the collection contains any documents
        if self.stock_collection.count_documents({}) == 0:
            print("Collection is empty or does not exist.")
            return {}
        # Get processed tickers from MongoDB with their oldest_date.
        cursor = self.stock_collection.find({}, {"_id": 0, "ticker": 1, "latest_date": 1, "oldest_date": 1})
        processed_docs = list(cursor)
        # Build a dictionary: { ticker: newest_date }
        return {doc["ticker"]: {"latest_date": doc["latest_date"], "oldest_date": doc["oldest_date"]} for doc in processed_docs}

    def update_stock_artifacts(self, aggregated_df):
        """
        Updates stock data artifacts by merging new aggregated data with existing data.
        For each ticker, adds the new row count to the current row count, updates latest_date,
        and records the current update timestamp.

        Parameters:
            aggregated_df (DataFrame): Spark DataFrame with columns:
                - ticker
                - row_count
                - latest_date
        """
        # Collect the aggregated data from Spark DataFrame to a list of Row objects
        records = aggregated_df.collect()

        # For each record in input spark df
        for record in records:
            ticker = record["ticker"]
            row_count = record["row_count"]
            latest_date_file = record["latest_date"]
            oldest_date_file = record["oldest_date"]

            # Get the current UTC timestamp as a timezone-aware datetime object
            current_timestamp = datetime.now(timezone.utc)

            # Collect ticker doc from collection
            ticker_doc = self.stock_collection.find_one({"ticker": ticker})
            if ticker_doc:

                oldest_date_db = ticker_doc.get('oldest_date')
                latest_data_db = ticker_doc.get('latest_date')

                # Add row count from df to current row count
                row_count = ticker_doc.get('row_count') + record["row_count"]
                # Create the update document
                update_doc = {
                    "$set": {
                        "row_count": row_count,
                        "latest_date": max(latest_date_file, latest_data_db),
                        "oldest_date": min(oldest_date_file, oldest_date_db),
                        "last_update_date": current_timestamp
                    }
                }
            # If ticker does not exist in mongo add oldest_date also
            else:
                update_doc = {
                    "$set": {
                        "row_count": row_count,
                        "latest_date": latest_date_file,
                        "oldest_date": oldest_date_file,
                        "last_update_date": current_timestamp
                    }
                }

            # Update the document for this ticker. Upsert = True will insert if the document doesn't exist.
            self.stock_collection.update_one({"ticker": ticker}, update_doc, upsert=True)

        print("StockData Artifacts updated successfully.")

    def get_stock_artifacts_by_ticker_name(self, ticker_name):
        # Check if the collection contains any documents
        if self.stock_collection.count_documents({}) == 0:
            print("Collection is empty or does not exist.")
            return {}
        # Get processed tickers from MongoDB by ticker name
        return self.stock_collection.find_one({"ticker": ticker_name})

    def save_base_on_mode(self, mode, aggregated_df):
        if mode == "overwrite":
            self.add_first_stock_artifacts(aggregated_df)
            return "First artifacts created successfully"
        else:
            self.update_stock_artifacts(aggregated_df)
            return "Artifacts updated successfully"