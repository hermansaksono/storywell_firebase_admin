from datetime import datetime
from pyrebase.pyrebase import Database, PyreResponse

from firebase import firebase_db, firebase_utils

FIREBASE_USER_SETTING_ROOT = "group_storywell_setting"

def get_all_families_shallow(order="desc") -> list:
    db: Database = firebase_db.get()
    all_families = db.child(FIREBASE_USER_SETTING_ROOT).shallow().get().val()
    return sorted(all_families)


def get_family_by_id(family_id: str):
    ref = get_family_ref_by_id(family_id)
    path = ref.database_url + ref.path
    family = ref.get().val()
    family['path'] = path
    family['caregiverLastSync'] = firebase_utils\
        .get_datetime_from_timestamp(family['fitnessSyncInfo']['caregiverDeviceInfo']['lastSyncTime'])
    family['childLastSync'] = firebase_utils\
        .get_datetime_from_timestamp(family['fitnessSyncInfo']['childDeviceInfo']['lastSyncTime'])
    family['appStartDateDjango'] = datetime.fromtimestamp(family['appStartDate'] / 1000)

    return family


def get_family_ref_by_id(family_id: str) -> Database:
    db: Database = firebase_db.get()
    return db.child(FIREBASE_USER_SETTING_ROOT).child(family_id)


def get_geostory_meta_ref_by_id(geostory_id: str) -> Database:
    db: Database = firebase_db.get()
    return db.child("all_geostory").child(geostory_id).child("meta")
