import json

from django.http import HttpResponse
from pyrebase import pyrebase
from pyrebase.pyrebase import Database

from group.models import User
from datetime import datetime
import pytz

with open("../data/user_logging_firebase.json", "r") as read_file:
    config = json.load(read_file)

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()


def __get_datetime(user: Database, key: str) -> datetime:
    timestamp = round(user.val()[key] / 1000)  # type: int
    local_tz = pytz.timezone("America/New_York")
    utc_dt = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
    return local_tz.normalize(utc_dt.astimezone(local_tz))


def refresh_groups(request):
    db = firebase.database()
    all_users = db.child("group_storywell_setting").get()

    for user in all_users.each():
        app_start_date = __get_datetime(user, "appStartDate")  # type:datetime
        logging_user = User(
            user_id=user.key(),
            app_start_date=__get_datetime(user, "appStartDate"),
            last_update=app_start_date
        )
        logging_user.save()
    return HttpResponse("Success")
