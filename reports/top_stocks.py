from utils.stock_loader import StockLoader
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from pyspark.sql.functions import col, min, max, concat, format_number, lit


class TopStocksApp(StockLoader):
    """
    TopStocksApp extends StockLoader to provide functionality for calculating
    the top N profit stocks over a specified time range. The profit is calculated
    based on the first available open price and the last available close price.
    """

    def __init__(self, spark):
        """
        Initializes the TopStocksApp with a Spark session and sets the earliest
        historical stock date.

        Parameters:
            spark (SparkSession): The Spark session to be used.
        """
        self.spark = spark
        # Set the earliest stock date (boundary date from which data is available)
        self.earliest_stock_date = datetime.strptime('2015-02-02', '%Y-%m-%d').date()
        super().__init__(spark)

    def find_start_date(self, target_date, time_frame):
        """
        Determines the start date for the analysis period based on the target date
        and the selected time_frame.

        Parameters:
            target_date (date): The target date for the analysis.
            time_frame (str): One of ["Daily", "Weekly", "Day", "YearToDate", "Annual", "HistoricalToDate"].
                             (Note: "Day" here is used instead of "Month" in our updated version.)
                             However, as per our discussion, we'll use "Month" to represent a monthly period.
                             Therefore, valid time_frames in our code are:
                             ["Daily", "Weekly", "Month", "YearToDate", "Annual", "HistoricalToDate"].

        Returns:
            date: The computed start date.

        Raises:
            ValueError: If an invalid time_frame is provided.
        """
        if time_frame == 'SingleDay':
            start_date = target_date
        elif time_frame == 'PastWeek':
            start_date = target_date - timedelta(days=7)
        elif time_frame == 'PastMonth':  # Changed from "Monthly" to "Month" for clarity.
            start_date = target_date - relativedelta(months=1)
        elif time_frame == 'YearToDate':
            start_date = date(target_date.year, 1, 1)
        elif time_frame == 'PastYear':
            start_date = target_date - relativedelta(years=1)
        elif time_frame == 'HistoricalToDate':
            # For HistoricalToDate, we return the earliest available stock date
            start_date = self.earliest_stock_date
        else:
            raise ValueError(
                "Invalid time_frame. Must be one of: Daily, Weekly, Month, YearToDate, Annual, HistoricalToDate."
            )

        return start_date

    def find_top_n_profit_stocks(self, target_date, target_time=None, time_frame='SingleDay', num_of_stocks=None):
        """
        Finds the top N stocks with the highest profit over a specified time range.

        The profit is calculated as:
            (last_close - first_open) / first_open * 100
        For time_frames other than 'HistoricalToDate', only tickers that have data
        starting from the computed start date are included (i.e., only boundary dates are required).

        Parameters:
            target_date (date): The target date in 'YYYY-MM-DD' format.
            target_time (time, optional): A specific time in 'HH:MM:SS' format (optional).
            time_frame (str): One of ["Daily", "Weekly", "Month", "YearToDate", "Annual", "HistoricalToDate"].
            num_of_stocks (int): Number of top stocks to return.

        Returns:
            DataFrame: A Spark DataFrame with columns:
                - ticker
                - first_dt: First available timestamp for the ticker in the period.
                - last_dt: Last available timestamp for the ticker in the period.
                - first_open: The open price at the first timestamp.
                - last_close: The close price at the last timestamp.
                - profit_pct: The profit percentage formatted as a string (rounded to 2 decimal places with a '%' sign).
        """
        # Check if target date is valid (not earlier than available data)
        if target_date < self.earliest_stock_date:
            raise Exception(f"Your date {target_date} is older than first historical date {self.earliest_stock_date}")

        # Determine the start date based on the selected time_frame
        start_date = self.find_start_date(target_date, time_frame)

        # Create lists for the years and months to load; we use boundary years and months.
        years_to_load = list({start_date.year, target_date.year})
        months_to_load = list({start_date.month, target_date.month})

        # Retrieve stock data using get_data (only boundary dates are required)
        data = super().get_data(years=years_to_load, months=months_to_load)

        # Filter data to include only rows between start_date and target_date
        data = data.filter(col("date") >= start_date)
        if not target_time:
            data = data.filter(col("date") <= target_date)
        else:
            # If a specific time is provided, combine it with the target date and filter using date_time
            target_date_time = datetime.combine(target_date, target_time)
            data = data.filter(col("date_time") <= target_date_time)

        # Compute boundary timestamps (first and last date_time for each ticker)
        time_bounds = data.groupBy("ticker").agg(
            min("date_time").alias("first_dt"),
            max("date_time").alias("last_dt")
        )

        # Join to get the first open price for each ticker using the earliest timestamp
        first_prices = data.alias("d").join(
            time_bounds.alias("tb"),
            (col("d.ticker") == col("tb.ticker")) & (col("d.date_time") == col("tb.first_dt"))
        ).select(col("d.ticker"), col("d.open").alias("first_open"))

        # Join to get the last close price for each ticker using the latest timestamp
        last_prices = data.alias("d").join(
            time_bounds.alias("tb"),
            (col("d.ticker") == col("tb.ticker")) & (col("d.date_time") == col("tb.last_dt"))
        ).select(col("d.ticker"), col("d.close").alias("last_close"))

        # Combine the results by joining first_prices and last_prices on ticker
        result = time_bounds.join(first_prices, on="ticker").join(last_prices, on="ticker")

        # Compute the profit percentage as a raw numeric value
        result = result.withColumn("profit_pct_value",
                                   (col("last_close") - col("first_open")) / col("first_open") * 100)

        # Create a formatted string version of profit_pct and store it in 'profit_pct'
        result = result.withColumn("profit_pct", concat(format_number(col("profit_pct_value"), 2), lit("%")))

        if not num_of_stocks:
            num_of_stocks = 10

        # Sort by profit percentage descending and limit to top N results
        result = result.orderBy(col("profit_pct_value").desc()).limit(num_of_stocks)

        # Return only the selected columns
        return result.select("ticker", "first_dt", "last_dt", "first_open", "last_close", "profit_pct")
