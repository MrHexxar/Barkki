"""
timeparse.py -- Parse human dates without losing your mind.

Turns messy user-provided date strings into proper timezone-aware datetimes.
Keeps the rest of the code clean by isolating the parsing logic here.
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, Tuple

# Accepted input formats. Expand this list if users keep messing up.
DATE_FORMATS = ["%H:%M %d.%m.%Y"]

def parse_date_with_formats(s: str, tz_name: str) -> Optional[datetime]:
    """
    Try to parse a string into a timezone-aware datetime object.

    Args:
        s: The date string provided by the user.
        tz_name: Name of the timezone to attach (e.g., "Europe/Helsinki").

    Returns:
        datetime with tzinfo if parsing succeeds, else None.
    """
    for fmt in DATE_FORMATS:
        try:
            # Try current format; if it explodes, we’ll just continue.
            dt = datetime.strptime(s, fmt)
            # Attach the given timezone
            return dt.replace(tzinfo=ZoneInfo(tz_name))
        except ValueError:
            # Wrong format? Move on to the next candidate.
            continue
    # Nothing matched.
    return None
