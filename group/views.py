from datetime import datetime

from django.http import HttpResponse
from pyrebase.pyrebase import PyreResponse

from firebase import firebase_db, firebase_utils
from group.models import User


def __get_datetime_from_pyre(user: PyreResponse, key: str) -> datetime:
    return firebase_utils.get_datetime_from_timestamp(user.val()[key])


def refresh_groups(request) -> HttpResponse:
    db = firebase_db.get()
    all_users = db.child("group_storywell_setting").get()

    for user in all_users.each():
        app_start_date: datetime = __get_datetime_from_pyre(user, "appStartDate")
        logging_user = User(
            user_id=user.key(),
            app_start_date=app_start_date,
            last_update=app_start_date
        )
        logging_user.save()
    return HttpResponse("Success")
