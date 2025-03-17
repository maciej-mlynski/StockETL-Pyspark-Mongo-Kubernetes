
class StockLoader:
    def __init__(self, spark, base_path='StockData'):
        self.spark = spark
        self.base_path = base_path

    def get_data(self, tickers=None, years=None, months=None, col_list=None):
        """
            Loads stock data based on provided filters.

            Parameters:
                tickers (list, optional): List of ticker symbols.
                                          If None or empty, data for all tickers is returned.
                years (list, optional): List of years (as int or str).
                                        If None or empty, data for all years is returned.
                months (list, optional): List of months (as int or str).
                                         If None or empty, data for all months is returned.
                col_list (list, optional): A list of column names to select.
                                        If None, a default list is used.

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
                    # There might be a case where user wants to load 01-2020 & 01-2015 (Stock data starts at 02-2015) - let user collect latest available month in 2015
                    if year == 2015 and month == 1:
                        month = 2
                    path = f"{self.base_path}/ticker={ticker}/year={year}/month={month}"
                    paths.append(path)

        # Read Parquet files from the constructed paths.
        # The "basePath" option enables Spark to automatically extract partition columns.
        stock_df = self.spark.read.option("basePath", self.base_path).parquet(*paths)

        # Sort data
        stock_df = stock_df.orderBy("ticker", "date", "time")

        # set default column if user did not specify
        default_columns = ["ticker", "date_time", "date", "time", "open", "high", "low", "close", "volume"]

        # Use the provided columns list if available, otherwise use the default
        columns_to_select = col_list if col_list is not None else default_columns

        # Select only the desired columns.
        stock_df = stock_df.select(*columns_to_select)
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
