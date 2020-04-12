from pyrebase.pyrebase import Database, PyreResponse

from firebase import firebase_db, firebase_utils
from group.models import User
from user_logging import constants, helpers

FIREBASE_USER_SETTING_ROOT = "group_storywell_setting"
FIREBASE_USER_LOGGING = "user_logging"
FIREBASE_PERSON_DAILY_FITNESS_ROOT = "person_daily_fitness"

def get_all_families_shallow() -> list:
    db: Database = firebase_db.get()
    all_families = db.child(FIREBASE_USER_SETTING_ROOT).shallow().get().val()
    return sorted(all_families)


def get_family_fitness_by_family_id(family_id: str, limit=60):
    family_setting = get_family_ref_by_id(family_id).get().val()
    caregiver_id = family_setting["group"]["members"][0]["id"]
    child_id = family_setting["group"]["members"][1]["id"]

    output = {
        "last_sync": {
            "caregiver": firebase_utils.get_datetime_from_timestamp(
                family_setting['fitnessSyncInfo']['caregiverDeviceInfo']['lastSyncTime']),
            "child": firebase_utils.get_datetime_from_timestamp(
                family_setting['fitnessSyncInfo']['childDeviceInfo']['lastSyncTime'])
        },
        "fitness_data": get_family_fitness_data(caregiver_id, child_id, limit)
    }

    return output


def get_family_ref_by_id(family_id: str) -> Database:
    db: Database = firebase_db.get()
    return db.child(FIREBASE_USER_SETTING_ROOT).child(family_id)


def get_person_daily_fitness_ref_by_id(person_id: int) -> Database:
    db: Database = firebase_db.get()
    return db.child(FIREBASE_PERSON_DAILY_FITNESS_ROOT).child(person_id)


def get_person_fitness_data(person_id: int, limit=30) -> dict:
    daily_fitness = get_person_daily_fitness_ref_by_id(person_id)\
        .order_by_child("timestamp").limit_to_last(limit).get()

    person_daily_fitness = dict()

    if daily_fitness.each() is not None:
        for one_day in daily_fitness.each():
            date_string = firebase_utils.get_date_str_from_timestamp(one_day.val()["timestamp"])
            person_daily_fitness[date_string] = one_day.val()["steps"]

    return person_daily_fitness

def get_family_fitness_data(caregiver_id: int, child_id: int, limit=30) -> dict:
    caregiver_data = get_person_fitness_data(caregiver_id, limit)
    child_data = get_person_fitness_data(child_id, limit)

    family_fitness_data = dict()
    set_of_date_str = set()

    for key in caregiver_data:
        set_of_date_str.add(key)

    for key in child_data:
        set_of_date_str.add(key)

    for date_str in sorted(set_of_date_str, reverse=True):
        one_day_fitness = {
            "caregiver": caregiver_data[date_str] if date_str in caregiver_data else "-",
            "child": child_data[date_str] if date_str in child_data else "-",
        }
        family_fitness_data[date_str] = one_day_fitness

    return family_fitness_data

def get_members_by_role(user: User) -> dict:
    members_by_role = dict()

    for person in user.get_members():
        members_by_role[person.role] = person

    return members_by_role


def get_raw_logging_data(user_id:str, start_date: str, end_date: str, db: Database) -> PyreResponse:
    return db.child(FIREBASE_USER_LOGGING) \
        .child(user_id) \
        .order_by_key() \
        .start_at(start_date) \
        .end_at(end_date) \
        .get()


def get_fitness_data_by_role(user: User, start_date: str, end_date: str, db: Database) -> dict:
    member_fitness_data = dict()

    for person in user.get_members():
        daily_steps = dict()

        fitness_data_raw: PyreResponse = db.child(FIREBASE_PERSON_DAILY_FITNESS_ROOT) \
            .child(person.person_id).order_by_key() \
            .start_at(start_date) \
            .end_at(end_date) \
            .get()

        for daily_steps_raw in fitness_data_raw.each():
            daily_steps[daily_steps_raw.key()] = daily_steps_raw.val()['steps']

        member_fitness_data[person.role] = dict(daily_steps)

    return member_fitness_data


def get_logs_by_day(user: User, start_date: str, end_date: str, is_show_raw: bool) -> dict:
    db = firebase_db.get()
    logs_by_day = dict()  # A dict that will store the daily logs
    raw_log_by_day = get_raw_logging_data(user.user_id, start_date, end_date, db)
    members_by_role: dict = get_members_by_role(user)
    members_fitness_data: dict = get_fitness_data_by_role(user, start_date, end_date, db)

    for log in raw_log_by_day.each():
        date_str: str = log.key()
        raw_timestamp_logs: dict = log.val()
        timestamp_logs = list()

        if is_show_raw:
            logs_to_iterate = list(raw_timestamp_logs.keys())
        else:
            logs_to_iterate = helpers.get_filtered_logs(raw_timestamp_logs, constants.event_names)

        for timestamp_id in logs_to_iterate:
            event: dict = raw_timestamp_logs[timestamp_id]
            time_str: str = helpers.get_friendly_time_from_timestamp(int(timestamp_id))
            timestamp_logs.append({
                "timestamp": int(timestamp_id),
                "event": event['eventName'],
                "time": time_str,
                "description": helpers.get_event_info(event, members_by_role),
                "edit_uri": helpers.get_edit_uri(user, event),
                "transcript": helpers.get_transcript(event)
            })

        logs_by_day[date_str] = {
            "date": helpers.get_friendly_date_from_str(date_str),
            "adult_steps": helpers.get_member_steps_on_day(members_fitness_data, "P", date_str),
            "child_steps": helpers.get_member_steps_on_day(members_fitness_data, "C", date_str),
            "minute_logs": timestamp_logs
        }

    return dict(sorted(logs_by_day.items(), reverse=True))