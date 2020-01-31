from datetime import datetime
from datetime import timedelta

import pytz
from django.http import HttpResponse
from pyrebase.pyrebase import PyreResponse

from eventlog.models import Log
from firebase import firebase_db, firebase_utils
from group.models import User

NOW_STR: str = "NOW"
ONE: int = 1
ONE_DAY_TIMEDELTA: timedelta = timedelta(days=ONE)
TZ_TIMEZONE = pytz.timezone("America/Los_Angeles")


def refresh_logs(request, user_id: str, end_date_str="now") -> HttpResponse:
    try:
        user: User = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return HttpResponse("User not found")

    cursor_datetime: datetime = user.last_update
    end_datetime: datetime = __get_end_datetime(end_date_str)

    total_days_updated: int = 0
    cursor_datetime_str: str = ""

    while cursor_datetime <= end_datetime:
        cursor_datetime_str = firebase_utils.get_date_str_from_datetime(cursor_datetime)

        if __refresh_log_by_date(user, cursor_datetime_str):
            total_days_updated += 1

        print("Finished " + user_id + " log(s) on " + cursor_datetime_str)
        cursor_datetime += ONE_DAY_TIMEDELTA

    user.last_update = cursor_datetime
    user.save()

    response_string = "Finished " + user_id + " log(s) until " + cursor_datetime_str \
                      + ". Logged " + str(total_days_updated) + " days "
    return HttpResponse(response_string)


def __get_end_datetime(end_date_str: str):
    if end_date_str == NOW_STR:
        return TZ_TIMEZONE.localize(datetime.now())
    else:
        return firebase_utils.get_datetime_from_str(end_date_str)


def refresh_logs_on_date(request, user_id: str, date_string: str) -> HttpResponse:
    try:
        user: User = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return HttpResponse("User not found")

    if __refresh_log_by_date(user, date_string):
        return HttpResponse("Success")
    else:
        return HttpResponse("No data on this day")


def __refresh_log_by_date(user: User, date_string: str) -> bool:
    timestamp_last_update: int = 0

    db = firebase_db.get()
    day_logs: PyreResponse = db.child("user_logging").child(user.user_id).child(date_string).get()

    if day_logs.each() is None:
        return False
    else:
        event_dict = dict()

        for log in day_logs.each():
            entry: Log = log.val()
            event_name: str = entry['eventName']
            event_date: datetime = firebase_utils.get_datetime_from_str(date_string)
            timestamp_last_update = int(entry['timestamp'])

            if event_name in event_dict:
                log_event = event_dict.get(event_name)  # type: Log
            else:
                log_event = __get_event_log(user, event_name, event_date)
                event_dict[event_name] = log_event

            log_event.count += 1
            log_event.save()

        user.last_update = firebase_utils.get_datetime_from_timestamp(timestamp_last_update)
        user.save()

        return True


def __get_event_log(user: User, event_name: str, event_date: datetime) -> Log:
    try:
        event_log: Log = Log.objects.get(user=user, event=event_name, date=event_date)
        event_log.count = 0
        return event_log
    except Log.DoesNotExist:
        return Log(user=user, event=event_name, date=event_date, count=0)




