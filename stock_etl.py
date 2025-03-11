from pyspark.sql.types import StructType, StructField, TimestampType, DoubleType, IntegerType
from pyspark.sql.functions import year, month, input_file_name, regexp_extract, to_date, col, date_format
import os


class StockETL:
    def __init__(self, spark, input_folder_path, is_first_run=False):
        self.input_folder_path = self.validate_input_folder(input_folder_path)
        self.mode = self.define_mode_base_on_init_value(is_first_run)
        self.spark = spark
        self.schema = self.input_file_schema()

    @staticmethod
    def validate_input_folder(input_folder_path):
        if os.path.exists(input_folder_path):
            return input_folder_path
        raise Exception(f"Could not find input folder data base on provided path: {input_folder_path}")

    @staticmethod
    def define_mode_base_on_init_value(is_first_run):
        if is_first_run:
            return "overwrite"
        return "append"

    @staticmethod
    def input_file_schema():
        return StructType([
            StructField("date", TimestampType(), nullable=True),
            StructField("open", DoubleType(), nullable=True),
            StructField("high", DoubleType(), nullable=True),
            StructField("low", DoubleType(), nullable=True),
            StructField("close", DoubleType(), nullable=True),
            StructField("volume", IntegerType(), nullable=True)
        ])

    def read_prepare_input_files(self):

        # read files base on provided path
        df = self.spark.read \
            .option("header", "true") \
            .schema(self.schema) \
            .csv(f"{self.input_folder_path}/*")

        if df.rdd.isEmpty():
            raise Exception(f"The Stock Data in '{self.input_folder_path}' is empty.")
        else:
            print("Stock data loaded successfully with records.")

        # Add ticker name from file name
        df = df.withColumn("file_name", input_file_name())
        df = df.withColumn("ticker", regexp_extract(col("file_name"), ".*/(.*)\.csv", 1)).drop('file_name')

        # Create new columns: one for the date part and one for the time part
        df = df.withColumn("new_date", to_date(col("date"))) \
            .withColumn("time", date_format(col("date"), "HH:mm:ss"))

        # Drop the original 'date' column and rename 'new_date' to 'date'
        df = df.drop("date").withColumnRenamed("new_date", "date")

        # Create new columns for year and month extracted from the date column
        df = df.withColumn("year", year(col("date"))) \
            .withColumn("month", month(col("date")))

        # Sort the DataFrame globally by 'date' and 'time'
        df = df.orderBy("ticker", "date", "time")

        # return selected files
        return df.select("ticker", "year", "month", "date", "time", "open", "high", "low", "close", "volume")

    def write_partitioned_stock_data(self, stock_data):
        # Write data to StockData folder with partitioning by "ticker", "year", "month"
        try:
            stock_data.write.partitionBy("ticker", "year", "month") \
                .option("header", "true").mode(self.mode).parquet("StockData")
            print("Data successfully saved to StockData")
        except Exception as e:
            raise Exception(f"Could not save data in StockData. ERROR: {e}")

    def run_etl(self):
        stock_data = self.read_prepare_input_files()
        self.write_partitioned_stock_data(stock_data)
