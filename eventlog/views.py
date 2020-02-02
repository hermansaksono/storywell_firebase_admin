from datetime import datetime

import pytz
from django.db.models.sql import Query
from django.http import HttpResponse
from django.template import loader
from pyrebase.pyrebase import PyreResponse

from eventlog import helpers
from eventlog.models import Log
from firebase import firebase_db, firebase_utils
from group.models import User

NOW_STR: str = "NOW"
TZ_TIMEZONE = pytz.timezone("America/New York")
ALL_STR: str = "all"


def view_logs(request, event:str, start_date: str, end_date:str, user_id: str = ALL_STR):
    try:
        if user_id == ALL_STR:
            users = User.objects.all()
        else:
            users = User.objects.filter(user_id=user_id)

        user_list: list = [user.user_id for user in users]
        date_list: list = helpers.get_list_of_dates(start_date, end_date)
        logs: Query = helpers.get_log_data_by_event(user_list, date_list, event)

        user_dict = helpers.get_str_lookup_dict(user_list)
        date_dict = helpers.get_str_lookup_dict(date_list)

        raw_log_data = helpers.get_raw_log_data(logs, user_dict, date_dict)
        raw_log_data = helpers.get_annotated_data_daily(raw_log_data, users, user_dict, date_dict)

        final_data = helpers.get_prepped_data(raw_log_data, user_dict)

        template = loader.get_template('eventlog/view_logs.html')
        context = {
            'event_name': event,
            'users': user_list,
            'dates': date_list,
            'log_data': final_data
        }

        return HttpResponse(template.render(context, request))
    except User.DoesNotExist:
        return HttpResponse("User not found")


def compare_logs(request, event1: str, event2: str, start_date: str, end_date:str, user_id: str = ALL_STR):
    try:
        if user_id == ALL_STR:
            users = User.objects.all()
        else:
            users = User.objects.filter(user_id=user_id)

        user_list: list = [user.user_id for user in users]
        date_list: list = helpers.get_list_of_dates(start_date, end_date)
        logs1: Query = helpers.get_log_data_by_event(user_list, date_list, event1)
        logs2: Query = helpers.get_log_data_by_event(user_list, date_list, event2)

        user_dict = helpers.get_str_lookup_dict(user_list)
        date_dict = helpers.get_str_lookup_dict(date_list)

        raw_log1_data = helpers.get_raw_log_data(logs1, user_dict, date_dict)
        raw_log2_data = helpers.get_raw_log_data(logs2, user_dict, date_dict)
        compared_data = helpers.get_compared_data(raw_log1_data, raw_log2_data, user_dict, date_list)
        compared_data = helpers.get_annotated_data_daily(compared_data, users, user_dict, date_dict)
        final_data = helpers.get_prepped_data(compared_data, user_dict)

        template = loader.get_template('eventlog/view_logs.html')
        context = {
            'event_name': event1 + " to " + event2,
            'users': user_list,
            'dates': date_list,
            'log_data': final_data
        }

        return HttpResponse(template.render(context, request))
    except User.DoesNotExist:
        return HttpResponse("User not found")


def compare_logs_weekly(request, event1: str, event2: str, start_date: str, end_date:str, user_id: str = ALL_STR):
    try:
        if user_id == ALL_STR:
            users = User.objects.all()
        else:
            users = User.objects.filter(user_id=user_id)

        user_list: list = [user.user_id for user in users]
        date_list: list = helpers.get_list_of_dates(start_date, end_date)
        logs1: Query = helpers.get_log_data_by_event(user_list, date_list, event1)
        logs2: Query = helpers.get_log_data_by_event(user_list, date_list, event2)

        user_dict = helpers.get_str_lookup_dict(user_list)
        date_dict = helpers.get_str_lookup_dict(date_list)

        raw_log1_data = helpers.get_raw_log_data(logs1, user_dict, date_dict)
        raw_log2_data = helpers.get_raw_log_data(logs2, user_dict, date_dict)
        compared_data = helpers.get_compared_data(raw_log1_data, raw_log2_data, user_dict, date_list)
        compared_data = helpers.get_annotated_data_monthly(compared_data, users, user_dict, date_dict, num_weeks=12)
        final_data = helpers.get_prepped_data(compared_data, user_dict)

        template = loader.get_template('eventlog/view_logs.html')
        context = {
            'event_name': event1 + " to " + event2,
            'users': user_list,
            'dates': date_list,
            'log_data': final_data
        }

        return HttpResponse(template.render(context, request))
    except User.DoesNotExist:
        return HttpResponse("User not found")


def refresh_logs(request, user_id: str, end_date_str="now") -> HttpResponse:
    try:
        user: User = User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return HttpResponse("User not found")

    cursor_datetime: datetime = user.last_update
    end_datetime: datetime = helpers.get_end_datetime(end_date_str)

    total_days_updated: int = 0
    cursor_datetime_str: str = ""

    while cursor_datetime <= end_datetime:
        cursor_datetime_str = firebase_utils.get_date_str_from_datetime(cursor_datetime)

        if __refresh_log_by_date(user, cursor_datetime_str):
            total_days_updated += 1

        print("Finished " + user_id + " log(s) on " + cursor_datetime_str)
        cursor_datetime += helpers.ONE_DAY_TIMEDELTA

    user.last_update = cursor_datetime
    user.save()

    response_string = "Finished " + user_id + " log(s) until " + cursor_datetime_str \
                      + ". Logged " + str(total_days_updated) + " days "
    return HttpResponse(response_string)


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
                log_event = helpers.get_event_log(user, event_name, event_date)
                event_dict[event_name] = log_event

            log_event.count += 1
            log_event.save()

        user.last_update = firebase_utils.get_datetime_from_timestamp(timestamp_last_update)
        user.save()

        return True


