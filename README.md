# Stock Data ETL Pipeline

## Overview

This project implements a robust ETL pipeline for processing stock data using Apache Spark and MongoDB. The pipeline includes the following key functionalities:

- **Data Ingestion & Transformation:**
  - Reads raw CSV files from the `RawStockData` folder using a predefined schema.
  - Extracts the ticker from the filename.
  - Converts and splits date-time information (e.g., renames `date` to `date_time` and creates separate `date` and `time` columns).
  - Extracts partitioning information (year and month) from the date.

- **Data Validation & Artifact Management:**
  - Validates the transformed stock data against artifacts stored in MongoDB.
  - Classifies tickers as new, missing, or requiring updates.
  - Updates MongoDB collections (`StockDataArtifacts` and `ETLArtifacts`) with aggregated metadata such as record counts and date ranges.

- **Data Loading:**
  - Writes the validated and transformed data to a partitioned Parquet store in the `StockData` folder.

- **Performance Comparison:**
  - An optional experiment compares the performance of aggregations on raw CSV data versus transformed Parquet data.
  - Both reading time and aggregation time are measured.

## Project Structure

- **stock_etl.py:**  
  Contains the `StockETL` class that orchestrates the full ETL process by extending functionality from `StockLoader`, `StockDataArtifacts`, and `ETLArtifacts`.

- **date_transform.py:**  
  Provides the `extract_date_from_path` utility to extract date information from folder names.

- **stock_loader.py:**  
  Implements the `StockLoader` class for reading stock data from Parquet files, with filtering and temporary view creation support.

- **etl_artifacts.py:**  
  Manages ETL artifacts in MongoDB, including run metadata and ticker classification.

- **stock_data_artifacts.py:**  
  Manages stock data artifacts in MongoDB, updating aggregated data (e.g., record count, date ranges) for each ticker.

- **check_server.py:**  
  Contains a utility function to verify that the MongoDB server is running.

- **create_db.py:**  
  A script to create the necessary MongoDB databases and collections if they don't already exist.

- **main.py:**  
  The main entry point that runs the full ETL process, including data reading, validation, writing, and artifact updates.

- **performance_comparison.py:**  
  (Optional) Compares performance metrics between aggregations on raw CSV data and transformed Parquet data.

## Setup and Execution

### Prerequisites

- **Apache Spark:**  
  Ensure that Spark is installed and properly configured.

- **MongoDB:**  
  Either run a local MongoDB server or use a MongoDB Atlas cluster. Verify connectivity using `check_server.py`.

- **Python Environment:**  
  Python 3.x and required dependencies (listed in `requirements.txt`).

### Installation

1. Clone the repository.
2. Create and activate a virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt


## Git and .gitignore

To keep your repository clean and avoid pushing large datasets (which can total over 20GB) to Git, it is highly recommended to use a `.gitignore` file. Ensure that folders containing raw data (`RawStockData`) and transformed data (`StockData`) are excluded from version control. For example, your `.gitignore` file might include:

