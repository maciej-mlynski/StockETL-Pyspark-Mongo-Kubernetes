from pymongo import MongoClient
from datetime import datetime, timezone


class StockDataArtifacts:
    def __init__(self, mongo_uri="mongodb://localhost:27017/", db_name="StockDB",
                 collection_name="StockDataArtifacts"):
        """
        Initializes the StockDataArtifacts class.

        Parameters:
            mongo_uri (str): MongoDB connection URI.
            db_name (str): The database name where artifacts are stored.
            collection_name (str): The collection name for the artifacts.
        """
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def add_first_stock_artifacts(self, aggregated_df):
        """
        Updates the artifacts collection with aggregated data for each ticker.

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
            self.collection.update_one({"ticker": ticker}, update_doc, upsert=True)

        print("StockData Artifacts updated successfully.")

        # Create an index on the "ticker" field in the StockDataArtifacts collection
        index_result = self.collection.create_index([("ticker", 1)])
        print("Created index on StockDataArtifacts:", index_result)

        # Optionally, create a compound index on "ticker" and "newest_date"
        compound_index = self.collection.create_index([("ticker", 1), ("latest_date", 1)])
        print("Created compound index on StockDataArtifacts:", compound_index)

    def export_ticker_data_from_mongo(self):
        """
        Queries ticker & oldest_date from the StockDataArtifacts collection and exports the data
        to a dict
        """
        # Check if the collection contains any documents
        if self.collection.count_documents({}) == 0:
            print("Collection is empty or does not exist.")
            return {}
        # Get processed tickers from MongoDB with their oldest_date.
        cursor = self.collection.find({}, {"_id": 0, "ticker": 1, "latest_date": 1})
        processed_docs = list(cursor)
        # Build a dictionary: { ticker: newest_date }
        return {doc["ticker"]: doc["latest_date"] for doc in processed_docs}

    def update_stock_artifacts(self, aggregated_df):
        """
        """
        # Collect the aggregated data from Spark DataFrame to a list of Row objects
        records = aggregated_df.collect()

        for record in records:
            ticker = record["ticker"]
            # Collect ticker doc from collection
            ticker_doc = self.collection.find_one({"ticker": ticker})
            # Add row count from df to current row count
            row_count = ticker_doc.get('row_count') + record["row_count"]
            latest_date = record["latest_date"]

            # Get the current UTC timestamp as a timezone-aware datetime object
            current_timestamp = datetime.now(timezone.utc)

            # Create the update document
            update_doc = {
                "$set": {
                    "row_count": row_count,
                    # "oldest_date": oldest_date, - old date stays the same
                    "latest_date": latest_date,
                    "last_update_date": current_timestamp
                }
            }

            # Update the document for this ticker. Upsert = True will insert if the document doesn't exist.
            self.collection.update_one({"ticker": ticker}, update_doc, upsert=True)

        print("StockData Artifacts updated successfully.")