from collections import defaultdict
from datetime import datetime
from datetime import timedelta

import pytz
from django.db.models.sql import Query
from django.http import HttpResponse
from django.template import loader
from pyrebase.pyrebase import PyreResponse

from eventlog.models import Log
from firebase import firebase_db, firebase_utils
from group.models import User

NOW_STR: str = "NOW"
ONE: int = 1
ONE_DAY_TIMEDELTA: timedelta = timedelta(days=ONE)
TZ_TIMEZONE = pytz.timezone("America/Los_Angeles")
ALL_STR: str = "all"


def view_logs(request, event:str, start_date: str, end_date:str, user_id: str = ALL_STR):
    try:
        if user_id == ALL_STR:
            users = User.objects.all()
        else:
            users = User.objects.filter(user_id=user_id)

        user_list: list = [user.user_id for user in users]
        date_list: list = __get_list_of_dates(start_date, end_date)
        logs: Query = __get_log_data_by_event(user_list, date_list, event)

        user_dict = __get_str_lookup_dict(user_list)
        date_dict = __get_str_lookup_dict(date_list)

        raw_log_data = __get_raw_log_data(logs, user_dict, date_dict)
        raw_log_data = __get_annotated_data(raw_log_data, users, user_dict, date_dict)

        final_data = __get_prepped_data(raw_log_data, user_dict)

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
        date_list: list = __get_list_of_dates(start_date, end_date)
        logs1: Query = __get_log_data_by_event(user_list, date_list, event1)
        logs2: Query = __get_log_data_by_event(user_list, date_list, event2)

        user_dict = __get_str_lookup_dict(user_list)
        date_dict = __get_str_lookup_dict(date_list)

        raw_log1_data = __get_raw_log_data(logs1, user_dict, date_dict)
        raw_log2_data = __get_raw_log_data(logs2, user_dict, date_dict)
        compared_data = __get_compared_data(raw_log1_data, raw_log2_data, user_dict, date_list)
        compared_data = __get_annotated_data(compared_data, users, user_dict, date_dict)
        final_data = __get_prepped_data(compared_data, user_dict)

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


def __get_log_data_by_event(users: list, dates: list, event_name: str) -> Query :
    return Log.objects.filter(
        user__in=users,
        event=event_name,
        date__in=dates) \
        .order_by('date', 'user')


def __get_str_lookup_dict(str_list: list) -> dict:
    lookup_dict = dict()
    count = 0
    for user in str_list:
        lookup_dict[user] = count
        count += 1
    return lookup_dict


def __get_raw_log_data(logs: Query, user_dict: dict, date_dict: dict, ):
    raw_log = [[0] * len(date_dict) for i in range(len(user_dict))]
    for log in logs:
        user_index = user_dict[log.user.user_id]
        date_str = firebase_utils.get_date_str_from_datetime(log.date)
        date_index = date_dict[date_str]
        raw_log[user_index][date_index] = log.count
    return raw_log


def __get_compared_data(log_data1, log_data2, user_dict: dict, date_list: list):
    compared_data = [[0] * len(date_list) for i in range(len(user_dict))]
    for user in user_dict.keys():
        user_index = user_dict[user]
        for i in range(len(date_list)):
            if log_data2[user_index][i] > 0:
                compared_data[user_index][i] = 2
            elif log_data1[user_index][i] > 0:
                compared_data[user_index][i] = 1
    return compared_data


def __get_annotated_data(compared_data, users: Query, user_dict: dict, date_dict: dict):
    for user in users:
        user_index = user_dict[user.user_id]
        date_str = firebase_utils.get_date_str_from_datetime(user.app_start_date)
        date_index = date_dict[date_str]
        compared_data[user_index][date_index] = "Start"
    return compared_data


def __get_prepped_data(compared_data, user_dict: dict):
    prepped_data = list()
    for user in user_dict.keys():
        user_index = user_dict[user]
        prepped_data.append({
            'user_id': user,
            'logs': compared_data[user_index]
        })
    return prepped_data


def __get_list_of_dates(start_date_str: str, end_date_str: str):
    cursor_date: datetime = firebase_utils.get_datetime_from_str(start_date_str)
    end_date: datetime = firebase_utils.get_datetime_from_str(end_date_str)

    output_dates = list()
    while cursor_date <= end_date:
        output_dates.append(firebase_utils.get_date_str_from_datetime(cursor_date))
        cursor_date += ONE_DAY_TIMEDELTA

    return output_dates


def __get_empty_log_dict(users: list, dates: list):
    log_data = multi_dict(2, int)
    for user in users:
        for date in dates:
            log_data[user][date] = 0
    return log_data


def multi_dict(K, type):
    if K == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: multi_dict(K-1, type))



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




