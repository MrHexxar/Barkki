"""
timeparse.py -- Parse human dates without losing your mind.

Provides a tiny utility to parse user-provided date strings into timezone-aware
datetime objects. Accepts multiple formats because humans are lazy and inconsistent.
"""

from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional

DATE_FORMATS = ["%d-%m-%Y", "%H:%M %d.%m.%Y"]


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
