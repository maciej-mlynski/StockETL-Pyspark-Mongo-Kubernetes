from airflow.exceptions import AirflowSkipException
from datetime import datetime, timedelta, date
import re


class FolderSelector:
    date_pattern = re.compile(r'(\d{4}_\d{2}_\d{2})')

    @classmethod
    def extract_date(cls, folder_name: str):
        m = cls.date_pattern.search(folder_name)
        if not m:
            return None
        return datetime.strptime(m.group(1).replace('_','-'), '%Y-%m-%d').date()

    @classmethod
    def business_day(cls, d: date, forward: bool = True) -> date:
        delta = timedelta(days=1 if forward else -1)
        next_day = d + delta
        # move day forward/back if weekend
        while next_day.weekday() >= 5:
            next_day += delta
        return next_day

    @classmethod
    def select_folder(cls,
                      new_folders: list[str],
                      processed_folders: list[str],
                      skip_dates: list[str]) -> str:
        # Get dates from folders names
        processed_dates = [cls.extract_date(f) for f in processed_folders]
        processed_dates = [d for d in processed_dates if d]

        # Transform each date in skip_dates
        skip_set = {datetime.strptime(s, '%Y-%m-%d').date() for s in skip_dates}

        # Filter only new folders
        candidates = [f for f in new_folders if f not in processed_folders]
        folder_dates = [(f, cls.extract_date(f)) for f in candidates]
        folder_dates = [(f,d) for f,d in folder_dates if d]

        # CASE 1: No processed folders yet -> take the earliest date
        if not processed_dates:
            oldest = min(folder_dates, key=lambda x: x[1])[0]
            return oldest

        # CASE 2: Check which dates are allowed -> We only allow 1 day back/forward dates
        # E.g.: processed_dates = [2025-01-02, 2025-01-03] -> allowed: 2025-01-01, 2025-01-04
        allowed = set()
        for d in processed_dates:
            allowed.add(cls.business_day(d, forward=True))
            allowed.add(cls.business_day(d, forward=False))

        # Drop weekends & skip_dates
        # If date is on skip_date move forward
        to_adjust = {d for d in allowed if d in skip_set or d.weekday()>=5}
        for d in to_adjust:
            allowed.discard(d)
            nd = cls.business_day(d, forward=True)
            while nd in skip_set:
                nd = cls.business_day(nd, forward=True)
            allowed.add(nd)

        # Match folders
        matches = [f for f,d in folder_dates if d in allowed]
        if not matches:
            raise AirflowSkipException("No folders to upload after meeting skip dates criteria and following date requirements.")
        # Chose folder with the oldest date
        chosen = min(matches, key=lambda f: cls.extract_date(f))
        return chosen