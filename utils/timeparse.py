"""
timeparse.py -- Parse human dates without losing your mind.

Provides a tiny utility to parse user-provided date strings into timezone-aware
datetime objects.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, Tuple

DATE_FORMATS = ["%H:%M %d.%m.%Y"]

def parse_date_with_formats(s: str, tz_name: str) -> Optional[datetime]:
    """
    Try to parse a string into a timezone-aware datetime object.

    Args:
        s: The date string provided by the user.
        tz_name: Name of the timezone to attach (e.g., "Europe/Helsinki").

    Returns:
        datetime object with tzinfo if parsing succeeds, else None.
    """
    for fmt in DATE_FORMATS:
        try:
            dt = datetime.strptime(s, fmt)
            return dt.replace(tzinfo=ZoneInfo(tz_name))
        except ValueError:
            # This format didn’t work, move on to the next.
            continue
    # Nothing worked. Time to cry.
    return None
