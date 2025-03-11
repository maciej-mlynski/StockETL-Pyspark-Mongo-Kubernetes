from pyspark.sql.types import StructType, StructField, DateType, TimestampType, DoubleType, IntegerType, StringType

raw_stock_schema = StructType([
    StructField("date", TimestampType(), True),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("volume", IntegerType(), True)
])

final_stock_schema = StructType([
    StructField("date", DateType(), True),
    StructField("time", TimestampType(), True),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("volume", IntegerType(), True),
    StructField("ticker", StringType(), True),
    StructField("year", IntegerType(), True),
    StructField("month", IntegerType(), True)
])