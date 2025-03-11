from pyspark.sql.types import StructType, StructField, TimestampType, DoubleType, IntegerType

raw_stock_schema = StructType([
    StructField("date", TimestampType(), True),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("volume", IntegerType(), True)
])

from pyspark.sql.types import StructType, StructField, DateType, TimestampType, DoubleType, IntegerType, StringType

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