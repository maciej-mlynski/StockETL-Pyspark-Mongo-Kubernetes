# Top Stocks Profit API

## Overview

The Top Stocks Profit API is a component of a broader Stock Data ETL system that uses Apache Spark for processing minute-level stock data. This API calculates the top N stocks with the highest profit over a user-specified time period. Profit is computed as the percentage difference between the first available open price and the last available close price for each ticker:

\[
\text{Profit (\%)} = \frac{(\text{last\_close} - \text{first\_open})}{\text{first\_open}} \times 100
\]

For most timeframes (except "HistoricalToDate"), only tickers with data that starts from the computed boundary (i.e. the earliest available date in the period) are included. The API validates the target date, ensures that trading data exists for that day (e.g., not on weekends or holidays), and raises an exception if the data is missing.

## Methodology

The Top Stocks Profit API works as follows:

1. **Input Parsing and Validation:**
   - The user provides a target date (and optionally a specific time) along with a timeframe and the number of top stocks to display.
   - The target date is parsed into a Python `date` object.
   - The API checks that the target date is not earlier than the earliest available stock data date.
   - For the "SingleDay" timeframe, if no data exists (due to a holiday or gap), an exception is raised.

2. **Timeframe Determination:**
   - Based on the selected timeframe, a start date is computed:
     - **SingleDay:** Only the target date is used.
     - **PastWeek:** The period spans the 7 days preceding the target date.
     - **PastMonth:** The period spans one month before the target date.
     - **YearToDate:** The period starts on January 1st of the target year and ends on the target date.
     - **PastYear:** The period spans one year before the target date.
     - **HistoricalToDate:** The period starts from the earliest available stock date (set to 2015-02-02) and goes to the target date.
   - These options ensure clarity in how far back the analysis will go.

3. **Data Retrieval and Filtering:**
   - The API calls the inherited `get_data` method (from `StockLoader`) to retrieve stock data for the boundary years and months.
   - The data is then filtered to include only records between the computed start date and the target date (or up to a specified time if provided).

4. **Aggregation and Profit Calculation:**
   - The filtered data is grouped by ticker to determine the first (earliest) and last (latest) trading timestamps.
   - Joins are performed to extract the open price corresponding to the earliest timestamp and the close price corresponding to the latest timestamp.
   - The profit percentage is calculated as:
     \[
     \text{profit\_pct\_value} = \frac{(\text{last\_close} - \text{first\_open})}{\text{first\_open}} \times 100
     \]
   - A formatted string version of the profit percentage (rounded to 2 decimal places with a "%" symbol) is also generated.

5. **Result Ordering and Limiting:**
   - The resulting tickers are ordered by profit in descending order.
   - The API returns only the top N stocks as specified by the user.

## Code Structure

### TopStocksApp Class (reports/top_stocks.py)

- **Purpose:**  
  Extends `StockLoader` to implement methods for determining the analysis period and calculating the top N profit stocks.
  
- **Key Methods:**
  - `__init__(spark)`: Initializes the Spark session and sets the earliest available stock date.
  - `find_start_date(target_date, time_frame)`: Computes the start date based on the target date and the selected timeframe.
  - `find_top_n_profit_stocks(target_date, target_time, time_frame, num_of_stocks)`:  
    Retrieves the relevant stock data, filters it according to the specified period, calculates the profit percentage for each ticker, and returns the top N results.

### API Endpoint (routers/top_stocks.py)

- **Endpoint:** `GET /api/get_top_stocks`
  
- **Parameters:**
  - `time_frame` (enum): Options are `SingleDay`, `PastWeek`, `PastMonth`, `YearToDate`, `PastYear`, and `HistoricalToDate`.
  - `target_date` (date): The target analysis date (e.g., 2020-01-01).
  - `optional_time` (time, optional): A specific time for filtering, if needed.
  - `num_of_stocks_to_display` (int, optional): The number of top stocks to return (default is 10).

- **Workflow:**
  - Initializes a Spark session.
  - Instantiates `TopStocksApp` and invokes the `find_top_n_profit_stocks` method.
  - Converts the resulting DataFrame to JSON.
  - Returns the JSON response.

## Running the API

To run the API server, execute:

```bash
python main.py
```
Using a GET request, you might call the endpoint as follows (example URL):
```bash
http://localhost:8000/api/get_top_stocks?time_frame=SingleDay&target_date=2020-01-01&num_of_stocks_to_display=10
```
If optional_time is needed, include it as an additional query parameter.


## Performance Comparison Experiment (via API)

### Methodology

The performance check compares advanced aggregation operations on two datasets:

1. **Raw CSV Data:**
   - **Location:** `RawStockData` folder.
   - **Processing:**  
     - Data is read using a predefined schema.
     - The `ticker` is extracted from the filename.
     - The `date` column is converted to a proper date type.
   - **Aggregation:**  
     Data is grouped by `ticker` to compute:
       - `record_count`: Total number of records per ticker.
       - `min_date`: Earliest date per ticker.
       - `max_date`: Latest date per ticker.
       - Additional volume statistics (average, standard deviation, total volume).
   - **Timing:**  
     Both the data reading time and aggregation time are measured.

2. **Transformed Parquet Data:**
   - **Location:** `StockData` folder.
   - **Processing:**  
     Data is stored as Parquet files partitioned by `ticker`, `year`, and `month`.
   - **Aggregation:**  
     Similar aggregation is performed on the `date_time` column.
   - **Timing:**  
     Reading and aggregation times are measured.

### Example Results

**Advanced Aggregation on Raw CSV Data:**
- Number of Groups: 6  
- Time taken to read raw data: 2.58 seconds  
- Time taken for raw aggregation: 91.12 seconds

**Advanced Aggregation on Transformed Parquet Data:**
- Number of Groups: 6  
- Time taken to read Parquet data: 4.18 seconds  
- Time taken for Parquet aggregation: 11.30 seconds

*Note: Replace these numbers with your actual measurements.*

### Accessing the Performance Check API

To trigger the performance check:
1. Run the application using:
   ```bash
   python main.py
2. Make an HTTP call (e.g., using curl, Postman, or your browser) to the following endpoint
    ```bash
   http://localhost:8000/api/get_etl_artifacts_by_run_id
3. The API will return a JSON response with performance metrics for both data sources

