from pyspark.sql import SparkSession
from ETL.stock_etl import StockETL

spark = SparkSession.builder.master("local[*]").appName("ETL").getOrCreate()
sc = spark.sparkContext

input_folder_path = 'RawStockData/stocks_historical_to_2025_02_04'
etl_app1 = StockETL(spark, input_folder_path, run_id=2)
etl_app1.run_etl()

# input_folder_path2 = 'RawStockData/stocks_2025_02_05'
# etl_app2 = StockETL(spark, input_folder_path2, run_id=2)
# etl_app2.run_etl()

# loader = StockLoader(spark)
# df = loader.get_data(tickers=['3MINDIA'], months=[2])
# print(df.tail(20))


# df = loader.create_temp_view(view_name='2025_01_stocks', years=['2025'], months=['1'])
# result = spark.sql("SELECT ticker, date, time, open, close FROM 2025_01_stocks WHERE close > 150")
# result.show()

spark.stop()