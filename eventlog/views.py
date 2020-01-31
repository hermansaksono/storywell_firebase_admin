from datetime import datetime

from django.http import HttpResponse
from pyrebase.pyrebase import PyreResponse

from eventlog.models import Log
from firebase import firebase_db, firebase_utils
from group.models import User


def refresh_logs(request, user_id: str, date_string: str) -> HttpResponse:
    user: User = User.objects.get(user_id=user_id)

    if __refresh_log_by_date(user, date_string):
        return HttpResponse("Success")
    else:
        return HttpResponse("No data on this day")


def __get_event_log(user: User, event_name: str, event_date: datetime) -> Log:
    try:
        event_log: Log = Log.objects.get(user=user, event=event_name, date=event_date)
        event_log.count = 0
        return event_log
    except Log.DoesNotExist:
        return Log(user=user, event=event_name, date=event_date, count=0)


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





