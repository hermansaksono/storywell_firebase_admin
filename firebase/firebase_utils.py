import time
from datetime import datetime

import pytz

DATE_STRING_FORMAT: str = "%Y-%m-%d"


def get_datetime_from_str(datetime_str: str) -> datetime:
    local_tz = pytz.timezone("America/New_York")
    raw_time = time.strptime(datetime_str, DATE_STRING_FORMAT)  # type: time.struct_time
    return local_tz.localize(datetime(*raw_time[:6]))


def get_datetime_from_timestamp(timestamp_millis: int) -> datetime:
    timestamp = round(timestamp_millis / 1000)  # type: int
    local_tz = pytz.timezone("America/New_York")
    utc_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    return local_tz.normalize(utc_dt.astimezone(local_tz))


def get_date_str_from_datetime(input_date: datetime) -> str:
    return input_date.strftime(DATE_STRING_FORMAT)
