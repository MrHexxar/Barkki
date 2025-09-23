# utils/timeparse.py
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

DATE_FORMATS = ["%d-%m-%Y", "%H:%M %d.%m.%Y"]

def parse_date_with_formats(s: str, tz_name: str) -> Optional[datetime]:
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.replace(tzinfo=ZoneInfo(tz_name))
        except ValueError:
            continue
    return None
