import re
from datetime import datetime


def extract_date_from_path(path: str):
    """
    Extracts the date from the end of the given path and returns a tuple:
    (date_obj, year, month).

    Expected path format examples:
        - "RawStockData/stocks_historical_to_2025_02_04"
        - "RawStockData/stocks_2025_02_07"
    The date must always be at the end of the path in the format YYYY_MM_DD.

    Returns:
        tuple: (date_obj, year, month)
            - date_obj: a datetime.date object representing the extracted date.
            - year: int, e.g., 2025.
            - month: int, e.g., 2.

    Raises:
        ValueError: if no valid date pattern is found at the end of the path.
    """
    # Search for the pattern: 4 digits, underscore, 2 digits, underscore, 2 digits at the end of the string.
    match = re.search(r'(\d{4})_(\d{2})_(\d{2})$', path)
    if not match:
        raise ValueError("No valid date pattern found at the end of the path.")

    # Extract the year, month, and day strings from the matched groups.
    year_str, month_str, day_str = match.groups()
    year = int(year_str)
    month = int(month_str)
    day = int(day_str)

    # Create a date object using the extracted year, month, and day.
    date_obj = datetime(year, month, day).date()

    # If path contains historical -> return year, month as None -> all data will be loaded in this case
    if "historical" in path:
        return date_obj, None, None

    return date_obj, year, month