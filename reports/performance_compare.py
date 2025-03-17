from ETL.stock_etl import StockETL
from pyspark.sql.functions import count, min, max, avg, stddev, sum, col
import time


class PerformanceCheck(StockETL):

    def __init__(self, spark):
        super().__init__(spark, 'RawStockData/stocks_historical_to_2025_02_04')
        self.spark = spark

    def read_raw_data(self):
        start = time.perf_counter()
        raw_df = super().read_prepare_input_files()
        read_time = time.perf_counter() - start
        return raw_df, read_time

    def read_parq_data(self):
        start = time.perf_counter()
        parquet_df = self.spark.read.option("header", "true").parquet("StockData")
        read_time = time.perf_counter() - start
        return parquet_df, read_time


    @staticmethod
    def advanced_aggregation(df):
        start = time.perf_counter()
        # Perform advanced aggregation by ticker
        agg_df = df.groupBy("ticker").agg(
            count("*").alias("record_count"),
            min("date").alias("min_date"),
            max("date").alias("max_date"),
            avg("volume").alias("avg_volume"),
            stddev("volume").alias("std_volume"),
            sum("volume").alias("total_volume")
        )

        # Optional filtering by target year (assuming date format 'yyyy-MM-dd')
        agg_df = agg_df.filter(col("min_date").substr(1, 4) == str(2024))
        agg_df = agg_df.filter(col("record_count") >= 100)

        group_count = agg_df.count()
        agg_time = time.perf_counter() - start
        return agg_df, group_count, agg_time


    def compare(self):

        results = []

        # --- Raw CSV Data Performance ---
        print("Starting advanced aggregation on Raw CSV Data...")
        raw_df, raw_read_time = self.read_raw_data()
        raw_agg_df, raw_group_count, raw_agg_time = self.advanced_aggregation(raw_df)

        raw_result = {
            "source": "Raw CSV Data",
            "group_count": raw_group_count,
            "read_time": round(raw_read_time, 2),
            "aggregation_time": round(raw_agg_time, 2)
        }
        results.append(raw_result)

        # --- Transformed Parquet Data Performance ---
        print("\nStarting advanced aggregation on Transformed Parquet Data...")
        parquet_df, parquet_read_time = self.read_parq_data()
        parquet_agg_df, parquet_group_count, parquet_agg_time = self.advanced_aggregation(parquet_df)

        parquet_result = {
            "source": "Transformed Parquet Data",
            "group_count": parquet_group_count,
            "read_time": round(parquet_read_time, 2),
            "aggregation_time": round(parquet_agg_time, 2)
        }
        results.append(parquet_result)

        # --- Display Results ---
        print("\n=== Advanced Aggregation on Raw CSV Data ===")
        print(f"Number of groups (raw): {raw_group_count}")
        print(f"Time taken to read raw data: {raw_read_time:.2f} seconds")
        print(f"Time taken for raw aggregation: {raw_agg_time:.2f} seconds\n")

        print("=== Advanced Aggregation on Transformed Parquet Data ===")
        print(f"Number of groups (parquet): {parquet_group_count}")
        print(f"Time taken to read parquet data: {parquet_read_time:.2f} seconds")
        print(f"Time taken for parquet aggregation: {parquet_agg_time:.2f} seconds\n")

        return results
