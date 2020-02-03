import json

from pyrebase import pyrebase
from pyrebase.pyrebase import Firebase, Database

CONFIG_PATH: str = "../data/user_logging_firebase.json"


# Temporarily replace quote function
def noquote(s):
    return s


def get() -> Database:
    with open(CONFIG_PATH, "r") as read_file:
        config = json.load(read_file)

    pyrebase.quote = noquote

    firebase: Firebase = pyrebase.initialize_app(config)

    return firebase.database()

