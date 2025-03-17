
*Note:* Only a few sample files have been committed for testing purposes. These samples are located in the `RawStockData` folder:
- `RawStockData/stocks_2025_02_05` – daily data sample
- `RawStockData/stocks_2025_02_06` – daily data sample
- `RawStockData/stocks_2025_02_07` – daily data sample
- `RawStockData/stocks_historical_to_2025_02_04` – historical data sample

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

