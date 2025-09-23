"""
timeparse.py -- Parse human dates without losing your mind.

Provides a tiny utility to parse user-provided date strings into timezone-aware
datetime objects. Accepts multiple formats because humans are lazy and inconsistent.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, Tuple

DATE_FORMATS = ["%H:%M %d-%m-%Y", "%H:%M %d.%m.%Y"]


def parse_date_with_formats(s: str, tz_name: str) -> Optional[datetime]:
    """
    Try to parse a string into a timezone-aware datetime object.

    Args:
        s: The date string provided by the user.
        tz_name: Name of the timezone to attach (e.g., "Europe/Helsinki").

    Returns:
        datetime object with tzinfo if parsing succeeds, else None.

    Notes:
        - Loops over allowed DATE_FORMATS until one works.
        - If nothing works, returns None and leaves the human to suffer.
        - We slap the timezone on afterward because Discord is picky.
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

def default_start_end(tz_name: str) -> Tuple[datetime, datetime]:
    """
    Compute default start (08:00 tomorrow) and end (23:59 tomorrow) datetimes,
    making sure the start is always in the future.
    """
    now = datetime.now(ZoneInfo(tz_name))
    start = now.replace(hour=8, minute=0, second=0, microsecond=0) + timedelta(days=1)
    if start <= now:
        # Execution at 23:59? Push to the day after
        start += timedelta(days=1)

    end = start.replace(hour=23, minute=59)
    return start, end