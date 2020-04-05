from collections import OrderedDict
from datetime import datetime
from pyrebase.pyrebase import Database, PyreResponse

from firebase import firebase_db, firebase_utils

FIREBASE_USER_SETTING_ROOT = "group_storywell_setting"
FIREBASE_PERSON_DAILY_FITNESS_ROOT = "person_daily_fitness"

def get_all_families_shallow() -> list:
    db: Database = firebase_db.get()
    all_families = db.child(FIREBASE_USER_SETTING_ROOT).shallow().get().val()
    return sorted(all_families)


def get_family_fitness_by_family_id(family_id: str, limit=60):
    family_setting = get_family_ref_by_id(family_id).get().val()
    caregiver_id = family_setting["group"]["members"][0]["id"]
    child_id = family_setting["group"]["members"][1]["id"]

    return get_family_fitness_data(caregiver_id, child_id, limit)


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

    # family_fitness_data = OrderedDict()
    # for key in caregiver_data:
    #     family_fitness_data[key]["caregiver"] = caregiver_data[key]
    #
    # for key in child_data:
    #     family_fitness_data[key]["child"] = child_data[key]

    return family_fitness_data



