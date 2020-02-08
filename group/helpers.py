from datetime import datetime

from pyrebase.pyrebase import PyreResponse

from firebase import firebase_utils
from group.models import User, Person


def get_datetime_from_pyre(user: PyreResponse, key: str) -> datetime:
    return firebase_utils.get_datetime_from_timestamp(user.val()[key])


def create_persons_in_group(list_of_members: list, user: User):
        for person_data in list_of_members:
            person = Person(
                user=user,
                person_id=person_data["id"],
                name=person_data["name"],
                role=person_data["role"]
            )
            person.save()