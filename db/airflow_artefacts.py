from pymongo import MongoClient
from db.check_server import check_mongo_server
import os
from typing import List


class AirflowArtifacts:
    def __init__(self, mongo_uri=os.environ["MONGO_URI"], db_name="StockDB",
                 collection_name="AirflowETLArtifacts"):
        """
        Initializes the AirflowArtifacts class.

        Parameters:
            mongo_uri (str): MongoDB connection URI.
            db_name (str): Name of the MongoDB database.
            collection_name (str): Collection name for ETL artifacts.
        """
        check_mongo_server()
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.airflow_collection = self.db[collection_name]


    def get_airflow_etl_artifacts(self):
        if self.airflow_collection.count_documents({}) == 0:
            return [{"Info": "Collection does not exist."}]
        record = self.airflow_collection.find_one({"_id":"processed_folders"})
        return record

    def add_skip_date(self, skip_dates: List):
        self.airflow_collection.update_one(
            {"_id": "processed_folders"},
            {
                "$setOnInsert": {"folders": []}, # Only if it is first upsert
                "$addToSet": {"skip_dates": {"$each": skip_dates}},
            },
            upsert=True,
        )
        return self.airflow_collection.find_one({"_id": "processed_folders"})

    def remove_skip_date(self, skip_dates: List):
        if self.airflow_collection.count_documents({"_id": "processed_folders"}) == 0:
            return {"info": "Collection does not exist."}

        result = self.airflow_collection.update_one(
            {"_id": "processed_folders"},
            {"$pullAll": {"skip_dates": skip_dates}},
        )

        if result.modified_count == 0:
            return {"info": "None of the provided skip date(s) were found to remove."}

        return self.airflow_collection.find_one({"_id": "processed_folders"})
