from pyrebase.pyrebase import Database

from firebase import firebase_db, firebase_utils


def update_reflection_transcript(user_id: str, timestamp: int, transcript: str) -> bool:
    db: Database = firebase_db.get()
    date_string: str = firebase_utils.get_date_str_from_timestamp(timestamp)

    reflection_query = db.child("user_logging") \
        .child(user_id)\
        .child(date_string) \
        .order_by_child("timestamp")\
        .equal_to(str(timestamp)) \
        .get()

    if reflection_query.get():
        reflection_log =reflection_query.get()[0].val()
        reflection_log["transcript"] = transcript

        reflection_query.update(reflection_log)
        return True
    else:
        return False
