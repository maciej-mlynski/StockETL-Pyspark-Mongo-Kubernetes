# Performance Comparison: Raw CSV vs. Transformed Parquet Data Aggregation

## Overview

This experiment compares the performance of advanced aggregation operations on stock data from two different data sources:

1. **Raw CSV Data:**  
   - **Location:** `RawStockData` folder.
   - **Processing:**  
     - Data is read using a predefined schema.
     - The `ticker` is extracted from the file name.
     - The `date` column is converted to a proper date type.
   - **Aggregation:**  
     The data is grouped by `ticker` to compute the following metrics:
     - **record_count:** Total number of records per ticker.
     - **min_date:** Earliest date per ticker.
     - **max_date:** Latest date per ticker.
     - Volume statistics (average, standard deviation, total volume).
   - **Timing:**  
     Both the reading time and the aggregation time are measured.

2. **Transformed Parquet Data:**  
   - **Location:** `StockData` folder.
   - **Processing:**  
     - Data is preprocessed and stored as Parquet files, partitioned by `ticker`, `year`, and `month`.
   - **Aggregation:**  
     A similar aggregation is performed by grouping on `ticker` (using the `date_time` column) to compute the same set of metrics.
   - **Timing:**  
     Both the reading time and the aggregation time are measured.

## Experiment Methodology

The experiment measures:
- **Reading Time:** The time taken to load the data into a Spark DataFrame.
- **Aggregation Time:** The time taken to perform the aggregation (grouping by `ticker` and computing metrics).

The processing time is measured using Python's `time.perf_counter()`.

## Results

The following results were obtained during the experiment:

### Advanced Aggregation on Raw CSV Data
- **Number of Groups:** 6
- **Time taken to read raw data:** 2.58 seconds
- **Time taken for raw aggregation:** 91.12 seconds

### Advanced Aggregation on Transformed Parquet Data
- **Number of Groups:** 6
- **Time taken to read parquet data:** 4.18 seconds
- **Time taken for parquet aggregation:** 11.30 seconds

## Observations and Conclusions

- **Raw CSV Data:**  
  Although the reading time is relatively low (2.58 seconds), the aggregation process is significantly slower (91.12 seconds). This is likely due to the overhead of parsing and processing CSV files, which are row-based and lack the optimizations provided by columnar storage.

- **Transformed Parquet Data:**  
  The reading time is slightly higher (4.18 seconds), but the aggregation is dramatically faster (11.30 seconds). Parquet’s columnar format, along with partitioning, allows for more efficient data processing and aggregation.

**Conclusion:**  
Storing and processing data in Parquet format offers significant performance improvements for aggregation operations compared to processing raw CSV data, despite a slight increase in the data loading time.

## Running the Experiment

To run the experiment, ensure that:
- Raw CSV files are located in the `RawStockData` folder.
- Transformed Parquet files are located in the `StockData` folder.
- Your Spark environment is properly configured.

Then execute the following command:

```bash
python performance_comparison.py
