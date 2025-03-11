from pyspark.sql import SparkSession
from stock_etl import StockETL



input_folder_path = 'RawStockData/stocks_historical_to_25_02_04'
spark = SparkSession.builder.master("local[*]").appName("ETL").getOrCreate()
sc = spark.sparkContext

# etl_app = StockETL(spark, input_folder_path, is_first_run=True)
#
# etl_app.run_etl()

