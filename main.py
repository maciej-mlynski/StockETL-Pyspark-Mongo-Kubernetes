from pyspark.sql import SparkSession
from stock_etl import StockETL
from stock_loader import StockLoader



input_folder_path = 'RawStockData/stocks_historical_to_25_02_04'
spark = SparkSession.builder.master("local[*]").appName("ETL").getOrCreate()
sc = spark.sparkContext

# etl_app = StockETL(spark, input_folder_path, is_first_run=True)
#
# etl_app.run_etl()

loader = StockLoader(spark)
df = loader.create_temp_view(view_name='2025_01_stocks', years=['2025'], months=['1'])
result = spark.sql("SELECT ticker, date, time, open, close FROM 2025_01_stocks WHERE close > 150")
result.show()

