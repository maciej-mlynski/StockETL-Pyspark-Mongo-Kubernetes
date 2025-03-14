from pyspark.sql.functions import year, month, input_file_name, regexp_extract, to_date, col, date_format, count, min, max
from utils.date_transform import extract_date_from_path
from utils.stock_loader import StockLoader
from db.stock_data_artifacts import StockDataArtifacts
from db.etl_artifacts import ETLArtifacts
from schemas.stock_schema import raw_stock_schema
import os


class StockETL(StockLoader, StockDataArtifacts, ETLArtifacts):
    def __init__(self, spark, input_folder_path, run_id):
        self.input_folder_path = self.validate_input_folder(input_folder_path)
        self.date, self.year, self.month = extract_date_from_path(input_folder_path)
        self.run_id = run_id
        self.mode = "append"
        self.spark = spark
        StockLoader.__init__(self, self.spark)
        StockDataArtifacts.__init__(self)
        ETLArtifacts.__init__(self)
        self.skip_writing = False

    @staticmethod
    def validate_input_folder(input_folder_path):
        if os.path.exists(input_folder_path):
            return input_folder_path
        raise Exception(f"Could not find input folder data base on provided path: {input_folder_path}")

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
        # read files base on provided path
        df = self.spark.read \
            .option("header", "true") \
            .schema(raw_stock_schema) \
            .csv(f"{self.input_folder_path}/*")

        if df.rdd.isEmpty():
            raise Exception(f"The Stock Data in '{self.input_folder_path}' is empty.")
        else:
            print("Stock data loaded successfully with records.")

        # Add ticker name from file name
        df = df.withColumn("file_name", input_file_name())
        df = df.withColumn("ticker", regexp_extract(col("file_name"), ".*/(.*)\.csv", 1)).drop('file_name')

        df = df.withColumnRenamed("date", "date_time")

        # Create new columns: one for the date part and one for the time part
        df = df.withColumn("date", to_date(col("date_time"))) \
            .withColumn("time", date_format(col("date_time"), "HH:mm:ss"))

        # Create new columns for year and month extracted from the date column
        df = df.withColumn("year", year(col("date"))) \
            .withColumn("month", month(col("date")))

        # Sort the DataFrame globally by 'date' and 'time'
        df = df.orderBy("ticker", "date_time")

        # return selected files
        return df.select("ticker", "date_time", "year", "month", "date", "time", "open", "high", "low", "close", "volume")

    def validate_file_to_write(self, stock_data):
        """
        Validates stock_data against the MongoDB artifacts (StockDataArtifacts collection) and determines:
          - Which tickers require an update (i.e. the maximum date in stock_data is greater than the stored latest_date)
          - Which tickers are new (present in stock_data but not in MongoDB)
          - Which tickers are missing (present in MongoDB but not in stock_data)

        If MongoDB does not contain any ticker data, the full stock_data is returned.
        Otherwise, the function filters out tickers that are already current (where
        stock_data's max date is less than or equal to MongoDB's stored latest_date) and returns the filtered DataFrame.

        Parameters:
            stock_data (DataFrame): Spark DataFrame containing at least "ticker" and "date_time" columns.

        Returns:
            DataFrame: The filtered DataFrame (only tickers that require update or are new).
        """
        # Collect ticker info from mongo db
        ticker_latest_day_dict = super().export_ticker_data_from_mongo()
        if not ticker_latest_day_dict:
            print('StockDataArtifacts does NOT exist yet. Saving full file...')

            print('Creating first ETL artifacts document...')
            unique_tickers = [row["ticker"] for row in stock_data.select("ticker").distinct().collect()]
            super().create_first_etl_art_doc(self.run_id, unique_tickers)

            # Change mode to overwrite
            self.mode = "overwrite"
            print("Changing mode to overwrite")

            return stock_data

        # Compute the minimum (latest) date for each ticker in stock_data.
        df_latest_dates = stock_data.groupBy("ticker").agg(max("date_time").alias("latest_date"))
        df_latest_dates_list = df_latest_dates.collect()
        # Build a dictionary: { ticker: latest_date }
        df_latest_dates_dict = {row["ticker"]: row["latest_date"] for row in df_latest_dates_list}

        # Create sets of tickers from the DataFrame and MongoDB.
        tickers_df = set(df_latest_dates_dict.keys())
        tickers_mongo = set(ticker_latest_day_dict.keys())

        # New tickers: present in stock_data but not in MongoDB.
        new_list = list(tickers_df - tickers_mongo)
        # Missing tickers: present in MongoDB but not in stock_data.
        missing_list = list(tickers_mongo - tickers_df)

        # For tickers present in both, check if the max date from stock_data
        # is less than or equal to the stored latest_date in MongoDB.
        update_list = []
        current_list = []
        for ticker in tickers_df.intersection(tickers_mongo):
            if df_latest_dates_dict[ticker] <= ticker_latest_day_dict[ticker]:
                current_list.append(ticker)
            else:
                update_list.append(ticker)

        # Filter out tickers that are already current from the DataFrame.
        # Only keep tickers that require update and new tickers.
        filtered_df = stock_data.filter(~col("ticker").isin(current_list))

        super().update_etl_artifacts(self.run_id, missing_list, new_list, update_list)

        if not update_list:
            self.skip_writing = True
            print("Data is up-to-date. Skipping write...")
        else:
            print('Saving Stock Data into StockData folder...')

        return filtered_df

    def write_partitioned_stock_data(self, stock_data):
        # Write data to StockData folder with partitioning by "ticker", "year", "month"
        try:
            stock_data.write.partitionBy("ticker", "year", "month") \
                .option("header", "true").mode(self.mode).parquet("StockData")
            print("Data successfully saved to StockData")
        except Exception as e:
            raise Exception(f"Could not save data in StockData. ERROR: {e}")

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
        # If self.mode == "overwrite" -> First run -> Load entire table
        if self.mode == "overwrite":
            df = super().get_data(col_list=['ticker', 'date_time'])

            # Save row_count, start_date, end_date for each ticker in mongo db
            aggregated_df = df.groupBy("ticker").agg(
                count("*").alias("row_count"),
                min("date_time").alias("oldest_date"),
                max("date_time").alias("latest_date")
            )
            super().add_first_stock_artifacts(aggregated_df)


        # Else -> load only last month data
        else:
            df = super().get_data(years=[self.year], months=[self.month], col_list=['ticker', 'date_time'])

            # Save row_count, start_date, end_date for each ticker in mongo db
            aggregated_df = df.groupBy("ticker").agg(
                count("*").alias("row_count"),
                min("date_time").alias("oldest_date"),
                max("date_time").alias("latest_date")
            )
            super().update_stock_artifacts(aggregated_df)



    def run_etl(self):
        stock_data = self.read_prepare_input_files()
        filtered_stock_data = self.validate_file_to_write(stock_data)
        del stock_data
        if not self.skip_writing:
            self.write_partitioned_stock_data(filtered_stock_data)
        self.create_save_stock_data_artifacts()

