from datetime import datetime
from pyrebase.pyrebase import Database, PyreResponse

from firebase import firebase_db, firebase_utils


def get_all_stories(order="desc") -> list:
    db: Database = firebase_db.get()

    all_geostory_raw = db.child("all_geostory").order_by_child("lastUpdateTimestamp", ).get()
    all_geostory_output = list()

    for geostory_raw in all_geostory_raw.each():
        geostory = geostory_raw.val()
        geostory_datetime: datetime = firebase_utils.get_datetime_from_timestamp(geostory["lastUpdateTimestamp"])
        geostory['datetimeString'] = firebase_utils.get_pretty_datetime_str(geostory_datetime)
        all_geostory_output.append(geostory)

    if order is "desc":
        all_geostory_output.reverse()

    return all_geostory_output


def get_geostory_by_id(geostory_id: str):
    ref = get_geostory_ref_by_id(geostory_id)
    path = ref.database_url + ref.path
    geostory = ref.get().val()
    geostory_datetime: datetime = firebase_utils.get_datetime_from_timestamp(geostory["lastUpdateTimestamp"])
    geostory['datetimeString'] = firebase_utils.get_pretty_datetime_str(geostory_datetime)
    geostory['path'] = path

    return geostory


def get_geostory_ref_by_id(geostory_id: str) -> Database:
    db: Database = firebase_db.get()
    return db.child("all_geostory").child(geostory_id)


def get_geostory_meta_ref_by_id(geostory_id: str) -> Database:
    db: Database = firebase_db.get()
    return db.child("all_geostory").child(geostory_id).child("meta")
