from schemas.stock_schema import final_stock_schema

class StockLoader:
    def __init__(self, spark, base_path='StockData'):
        self.spark = spark
        self.base_path = base_path
        self.schema = final_stock_schema

    def get_data(self, tickers=None, years=None, months=None):
        """
            Loads stock data based on provided filters.

            Parameters:
                tickers (list, optional): List of ticker symbols.
                                          If None or empty, data for all tickers is returned.
                years (list, optional): List of years (as int or str).
                                        If None or empty, data for all years is returned.
                months (list, optional): List of months (as int or str).
                                         If None or empty, data for all months is returned.

            Returns:
                DataFrame: Spark sorted DataFrame containing the selected data with columns:
                           "ticker", "date", "time", "open", "high", "low", "close", "volume".
            """
        # Use wildcard "*" if no specific filter is provided.
        tickers = tickers if tickers and len(tickers) > 0 else ["*"]
        years = years if years and len(years) > 0 else ["*"]
        months = months if months and len(months) > 0 else ["*"]

        # Build a list of paths for all combinations of ticker, year, and month.
        paths = []
        for ticker in tickers:
            for year in years:
                for month in months:
                    path = f"{self.base_path}/ticker={ticker}/year={year}/month={month}"
                    paths.append(path)

        # Read Parquet files from the constructed paths.
        # The "basePath" option enables Spark to automatically extract partition columns.
        stock_df = self.spark.read.option("basePath", self.base_path).parquet(*paths)

        # Sort data
        stock_df = stock_df.orderBy("ticker", "date", "time")

        # Select only the desired columns.
        stock_df = stock_df.select("ticker", "date", "time", "open", "high", "low", "close", "volume")
        return stock_df

    def create_temp_view(self, view_name, tickers=None, years=None, months=None):
        """
        Loads stock data based on provided filters, registers it as a temporary view,
        and returns the DataFrame.

        Parameters:
            view_name (str): The name to assign to the temporary view.
            tickers (list, optional): List of ticker symbols.
            years (list, optional): List of years.
            months (list, optional): List of months.

        Returns:
            DataFrame: Spark DataFrame registered as a temporary view.
        """
        stock_df = self.get_data(tickers, years, months)
        stock_df.createOrReplaceTempView(view_name)
        print(f"Temporary view '{view_name}' created successfully!")
        return stock_df
