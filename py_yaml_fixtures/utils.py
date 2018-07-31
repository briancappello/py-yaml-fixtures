from datetime import datetime, timezone
from dateutil.parser import parse as parse_datetime


def datetime_factory(value):
    if value in {'today', 'now', 'utcnow'}:
        return datetime.now(timezone.utc)
    elif value not in {None, 'None'}:
        return parse_datetime(value)


def date_factory(value):
    dt = datetime_factory(value)
    if isinstance(dt, datetime):
        return dt.date
