import requests

from fitness import config

def request(user_id) -> bool:
    payload = {"data": {"personId": user_id}}
    post_request = requests.post(config.URL_SYNC_FITNESS, json=payload)

    if post_request.status_code is 200:
        return True
    else:
        return False