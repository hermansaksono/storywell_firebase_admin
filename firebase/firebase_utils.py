import time
from datetime import datetime

import pytz


def get_datetime_from_str(datetime_str: str) -> datetime:
    raw_time = time.strptime(datetime_str, "%Y-%m-%d")  # type: time.struct_time
    return datetime(*raw_time[:6])


def get_datetime_from_timestamp(timestamp_millis: int) -> datetime:
    timestamp = round(timestamp_millis / 1000)  # type: int
    local_tz = pytz.timezone("America/New_York")
    utc_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    return local_tz.normalize(utc_dt.astimezone(local_tz))