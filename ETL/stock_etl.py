from pyspark.sql.functions import year, month, input_file_name, regexp_extract, to_date, col, date_format, count, min, max, lit
from pyspark.sql.types import StructType, StructField, TimestampType, DoubleType, IntegerType
from ETL.utils.date_transform import extract_date_from_path
from utils.stock_loader import StockLoader
from db.stock_data_artifacts import StockDataArtifacts
from db.etl_artifacts import ETLArtifacts


class StockETL(StockLoader, StockDataArtifacts, ETLArtifacts):
    def __init__(self, spark, input_folder_path):
        self.input_folder_path = input_folder_path
        self.raw_stock_schema = self.define_raw_data_schema()
        self.date, self.year, self.month = extract_date_from_path(input_folder_path)
        self.mode = "append"
        self.spark = spark
        StockLoader.__init__(self, self.spark)
        StockDataArtifacts.__init__(self)
        ETLArtifacts.__init__(self)
        self.skip_writing = False
        self.tickers_new = []
        self.api_artifacts = {}

    @staticmethod
    def define_raw_data_schema():
        raw_stock_schema = StructType([
            StructField("date", TimestampType(), True),
            StructField("open", DoubleType(), True),
            StructField("high", DoubleType(), True),
            StructField("low", DoubleType(), True),
            StructField("close", DoubleType(), True),
            StructField("volume", IntegerType(), True)
        ])
        return raw_stock_schema

    def read_prepare_input_files(self):
        """
        Reads and prepares input stock data files from the provided folder path.

        Steps:
          1. Read CSV files from the input folder using the provided raw_stock_schema.
          2. Check if the loaded DataFrame is empty; if so, raise an Exception.
          3. Extract the ticker name from the file name using a regular expression.
          4. Rename the 'date' column to 'date_time'.
          5. Create separate columns for date and time from 'date_time':
             - 'date' (converted to proper date type)
             - 'time' (formatted as HH:mm:ss)
          6. Extract 'year' and 'month' from the 'date' column.
          7. Sort the DataFrame globally by 'ticker' and 'date_time'.
          8. Return the final DataFrame with selected columns.

        Returns:
          DataFrame: A Spark DataFrame with the following columns:
                     "ticker", "date_time", "year", "month", "date", "time",
                     "open", "high", "low", "close", "volume"
        """
        # 1. Read CSV files from minio
        try:
            df = self.spark.read \
                .option("header", "true") \
                .schema(self.raw_stock_schema) \
                .csv(f"s3a://rawstockdata/{self.input_folder_path}/*")
        except Exception as e:
            raise Exception(f"Could not load raw stock data: {self.input_folder_path} from minio. Error: {e}")

        # 2. Verify that data was loaded.
        if df.rdd.isEmpty():
            raise Exception(f"The Stock Data in '{self.input_folder_path}' is empty.")
        self.api_artifacts['LoadingData'] = "Successful"
        print("Stock data loaded successfully with records.")

        # 3. Extract ticker from file path.
        df = df.withColumn("file_name", input_file_name())
        df = df.withColumn("ticker", regexp_extract(col("file_name"), ".*/(.*)\.csv", 1)).drop('file_name')

        # 4. Rename and split date-time columns.
        df = df.withColumnRenamed("date", "date_time")
        df = df.withColumn("date", to_date(col("date_time"))) \
            .withColumn("time", date_format(col("date_time"), "HH:mm:ss"))

        # 5. Extract year and month from date.
        df = df.withColumn("year", year(col("date"))) \
            .withColumn("month", month(col("date")))

        # 6. Sort data for consistency.
        df = df.orderBy("ticker", "date_time")

        # 7. Return only the selected columns.
        return df.select("ticker", "date_time", "year", "month", "date", "time", "open", "high", "low", "close", "volume")

    def validate_file_to_write(self, stock_data):
        """
        Validates stock_data against MongoDB artifacts and determines which tickers:
          - Require an update (stock_data's max date is greater than MongoDB's stored latest_date)
          - Are new (present in stock_data but not in MongoDB)
          - Are missing (present in MongoDB but not in stock_data)

        If MongoDB has no ticker data, creates the first ETL artifacts document and sets mode to "overwrite".
        Otherwise, tickers that are considered "current" (stock_data's max date <= stored latest_date)
        are filtered out from stock_data.

        Returns:
            DataFrame: The filtered DataFrame (only tickers that require update or are new).
        """
        # Collect ticker info from mongo db
        mongo_ticker_dict = super().export_ticker_data_from_mongo()
        if not mongo_ticker_dict:
            print('StockDataArtifacts does NOT exist yet. Saving full file...')
            print('Creating first ETL artifacts document...')

            unique_tickers = [row["ticker"] for row in stock_data.select("ticker").distinct().collect()]
            super().create_first_etl_art_doc(unique_tickers)
            print("Changing mode to overwrite")
            self.mode = "overwrite"

            # Add details in etl artifacts
            self.api_artifacts["ETLArtifacts"] = "First artifacts created successfully"
            self.api_artifacts["run_id"] = self.run_id

            return stock_data

        # Compute the maximum (latest) date for each ticker in stock_data.
        df_latest_dates = stock_data.groupBy("ticker").agg(max("date_time").alias("latest_date"))
        df_latest_dates_list = df_latest_dates.collect()
        df_latest_dates_dict = {row["ticker"]: row["latest_date"] for row in df_latest_dates_list}

        # Compute the minimum (oldest) date for each ticker in stock_data.
        df_oldest_dates = stock_data.groupBy("ticker").agg(min("date_time").alias("oldest_date"))
        df_oldest_dates_list = df_oldest_dates.collect()
        df_oldest_dates_dict = {row["ticker"]: row["oldest_date"] for row in df_oldest_dates_list}

        # Create sets of tickers from the DataFrame and MongoDB.
        tickers_df = set(df_latest_dates_dict.keys())
        tickers_mongo = set(mongo_ticker_dict.keys())

        # New tickers: present in stock_data but not in MongoDB.
        self.tickers_new = list(tickers_df - tickers_mongo)

        # Missing tickers: present in MongoDB but not in stock_data.
        tickers_missing = list(tickers_mongo - tickers_df)

        tickers_update = []
        tickers_current = []

        for ticker in tickers_df.intersection(tickers_mongo):
            mongo_latest = mongo_ticker_dict[ticker]["latest_date"]
            mongo_oldest = mongo_ticker_dict[ticker]["oldest_date"]
            stock_latest = df_latest_dates_dict[ticker]
            stock_oldest = df_oldest_dates_dict[ticker]
            if stock_latest > mongo_latest or stock_oldest < mongo_oldest:
                tickers_update.append(ticker)
            else:
                tickers_current.append(ticker)

        # Filter out up-to-date tickers from stock_data.
        filtered_df = stock_data.filter(~col("ticker").isin(tickers_current))

        # If tickers to update & new tickers is empty -> skip write
        if not tickers_update and not self.tickers_new:
            self.skip_writing = True
            print("Data is up-to-date. Skipping write...")
            self.api_artifacts["WritingMode"] = "Data already up-to date. Write skipped"
        else:
            self.api_artifacts["WritingMode"] = self.mode

        # Update ETL artifacts with classification results.
        super().update_etl_artifacts(tickers_missing, self.tickers_new, tickers_update, self.skip_writing)
        self.api_artifacts["ETLArtifacts"] = "ETL Artifacts added successfully"
        self.api_artifacts["run_id"] = self.run_id

        return filtered_df

    def write_partitioned_stock_data(self, stock_data):
        # Write data to StockData folder with partitioning by "ticker", "year", "month"
        print('Saving Stock Data into StockData folder...')
        path = "s3a://stockdata/data/"
        try:
            stock_data.write.partitionBy("ticker", "year", "month") \
                .option("header", "true").mode(self.mode).parquet(path)
            print("Data successfully saved to StockData folder")
        except Exception as e:
            raise Exception(f'Could not save data in {path}. ERROR: {e}')
        self.api_artifacts['WritingData'] = "Successful"

    def create_save_stock_data_artifacts(self):
        """
        Loads stock data and creates artifact records for each ticker, then saves these artifacts
        to the MongoDB collection "StockDataArtifacts" in the "StockDB" database.

        The method performs the following steps:
          1. Data Loading:
             - If it is the first run (self.is_first_run is True), it loads the entire table using
               the parent's get_data() method, selecting only the 'ticker' and 'date_time' columns.
             - Otherwise, it loads only the last month's data by specifying the 'years' and 'months'
               parameters along with the column list.

          2. Aggregation:
             - The loaded DataFrame is grouped by 'ticker'.
             - For each ticker, the method calculates:
                  * "row_count": the total number of rows (records).
                  * "oldest_date": the minimum 'date_time' value (representing the earliest date).
                  * "latest_date": the maximum 'date_time' value (representing the most recent date).

          3. Saving Artifacts:
             - The aggregated DataFrame (aggregated_df) is then passed to the parent's update_artifacts()
               method, which upserts the aggregated data into the MongoDB collection.
               (The update_artifacts() method handles the MongoDB connection and saving of the data.)
        """
        # If self.mode == "overwrite" -> First run or if self.year is None means that data is historical (in case this data wasn't added in first run) -> Load entire table
        if self.mode == "overwrite" or self.year is None:
            df = super().get_data(col_list=['ticker', 'date', 'date_time'])
            df = df.filter(col("date") <= lit(self.date))
        # For adding new data (if year is not None -> daily data
        else:
            df = super().get_data(years=[self.year], months=[self.month], col_list=['ticker', 'date', 'date_time'])
            # Filter only single day data
            df = df.filter(col("date") == lit(self.date))

        # Drop date column
        df = df.drop("date")

        # Collect row count, latest date, and oldest date for each ticker on filtered stock data
        aggregated_df = df.groupBy("ticker").agg(
            count("*").alias("row_count"),
            min("date_time").alias("oldest_date"),
            max("date_time").alias("latest_date")
        )

        # Run method that trigger appropriate saving method base on saving mode -> returns the string explaining which method was chosen
        stock_data_artifacts_resp = super().save_base_on_mode(self.mode, aggregated_df)
        self.api_artifacts['StockDataArtifacts'] = stock_data_artifacts_resp


    def run_etl(self):
        """
        Runs the entire ETL process:
          1. Reads and prepares input files.
          2. Validates the data against existing MongoDB artifacts.
          3. Writes partitioned stock data if needed.
          4. Creates or updates stock data artifacts in MongoDB.
        """
        stock_data = self.read_prepare_input_files()
        stock_data = self.validate_file_to_write(stock_data)
        if not self.skip_writing:
            self.write_partitioned_stock_data(stock_data)
            self.create_save_stock_data_artifacts()

        return [self.api_artifacts]
