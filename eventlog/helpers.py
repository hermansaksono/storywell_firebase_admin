from collections import defaultdict
from datetime import datetime, timedelta

import pytz as pytz
from gcloud.datastore import Query

from eventlog.models import Log
from firebase import firebase_db, firebase_utils
from group.models import User
from pyrebase.pyrebase import PyreResponse


NOW_STR: str = "NOW"
ONE_DAY_TIMEDELTA: timedelta = timedelta(days=1)
TZ_TIMEZONE = pytz.timezone("America/New York")


def get_multi_dict(K, type):
    if K == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: get_multi_dict(K-1, type))


def get_empty_log_dict(users: list, dates: list):
    log_data = get_multi_dict(2, int)
    for user in users:
        for date in dates:
            log_data[user][date] = 0
    return log_data


def get_list_of_dates(start_date_str: str, end_date_str: str):
    cursor_date: datetime = firebase_utils.get_datetime_from_str(start_date_str)
    end_date: datetime = firebase_utils.get_datetime_from_str(end_date_str)

    output_dates = list()
    while cursor_date <= end_date:
        output_dates.append(firebase_utils.get_date_str_from_datetime(cursor_date))
        cursor_date += ONE_DAY_TIMEDELTA

    return output_dates


def get_log_data_by_event(users: list, dates: list, event_name: str) -> Query :
    return Log.objects.filter(
        user__in=users,
        event=event_name,
        date__in=dates) \
        .order_by('date', 'user')


def get_str_lookup_dict(str_list: list) -> dict:
    lookup_dict = dict()
    count = 0
    for user in str_list:
        lookup_dict[user] = count
        count += 1
    return lookup_dict


def get_raw_log_data(logs: Query, user_dict: dict, date_dict: dict, ) -> list:
    raw_log = [[0] * len(date_dict) for i in range(len(user_dict))]
    for log in logs:
        user_index = user_dict[log.user.user_id]
        date_str = firebase_utils.get_date_str_from_datetime(log.date)
        date_index = date_dict[date_str]
        raw_log[user_index][date_index] = log.count
    return raw_log


def get_compared_data(log_data1, log_data2, user_dict: dict, date_list: list):
    compared_data = [[0] * len(date_list) for i in range(len(user_dict))]
    for user in user_dict.keys():
        user_index = user_dict[user]
        for i in range(len(date_list)):
            if log_data2[user_index][i] > 0:
                compared_data[user_index][i] = 2
            elif log_data1[user_index][i] > 0:
                compared_data[user_index][i] = 1
    return compared_data


def get_annotated_data_daily(data, users: Query, user_dict: dict, date_dict: dict):
    for user in users:
        user_index = user_dict[user.user_id]
        date_str = firebase_utils.get_date_str_from_datetime(user.app_start_date)
        date_index = date_dict[date_str]
        data[user_index][date_index - 1] = "Start"
    return data


def get_annotated_data_monthly(data, users: Query, user_dict: dict, date_dict: dict, num_weeks: int=1):
    annotated_data = [[0] * num_weeks for i in range(len(user_dict))]
    for user in users:
        user_index = user_dict[user.user_id]
        date_index = date_dict[firebase_utils.get_date_str_from_datetime(user.app_start_date)]

        for week_index in range(num_weeks):
            for day_week_index in range(7):
                index: int = (week_index * 7) + day_week_index
                annotated_data[user_index][index] = data[user_index][date_index + index]


        annotated_data[user_index][date_index - 1] = "Start"

    return annotated_data


def get_prepped_data(compared_data, user_dict: dict):
    prepped_data = list()
    for user in user_dict.keys():
        user_index = user_dict[user]
        prepped_data.append({
            'user_id': user,
            'logs': compared_data[user_index]
        })
    return prepped_data


def get_event_log(user: User, event_name: str, event_date: datetime) -> Log:
    try:
        event_log: Log = Log.objects.get(user=user, event=event_name, date=event_date)
        event_log.count = 0
        return event_log
    except Log.DoesNotExist:
        return Log(user=user, event=event_name, date=event_date, count=0)


def get_end_datetime(end_date_str: str):
    if end_date_str == NOW_STR:
        return TZ_TIMEZONE.localize(datetime.now())
    else:
        return firebase_utils.get_datetime_from_str(end_date_str)