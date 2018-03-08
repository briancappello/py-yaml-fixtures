from datetime import datetime, timezone
from dateutil.parser import parse as parse_datetime


def datetime_factory(value):
    if value in {'today', 'now', 'utcnow'}:
        return datetime.now(timezone.utc)
    return parse_datetime(value)


def date_factory(value):
    return datetime_factory(value).date
