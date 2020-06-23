import json
from datetime import datetime, timedelta
from typing import Optional

import pytz as pytz

from firebase import firebase_utils
from group.models import User, Person
from user_logging import config
from . import constants

NOW_STR: str = "NOW"
ONE_DAY_TIMEDELTA: timedelta = timedelta(days=1)
TZ_TIMEZONE = pytz.timezone("America/New_York")

# Load geostories
with open(constants.GEOSTORIES_PATH) as f:
    all_geostories = json.load(f)

# Load all stories
stories = dict()
for key, val in constants.story_contents_json.items():
    with open(val) as f:
        stories[key] = json.load(f)

def get_friendly_date_from_str(date_str: str) -> str:
    friendly_datetime: datetime = firebase_utils.get_datetime_from_str(date_str)
    return firebase_utils.get_pretty_date_str(friendly_datetime)


def get_friendly_time_from_timestamp(timestamp_millis: int) -> str:
    friendly_datetime: datetime = firebase_utils.get_datetime_from_timestamp(timestamp_millis)
    return firebase_utils.get_pretty_time_str(friendly_datetime)


def get_event_info(event: dict, member_by_role: dict) -> str:
    person_adult: Person = member_by_role["P"]
    person_child: Person = member_by_role["C"]
    event_name: str = event['eventName']
    event_params: dict
    if 'eventParams' in event :
        event_params = event['eventParams']

    if event_name == "READ_STORY":
        story_id: str = event_params['STORY_ID']
        story_name: str = constants.stories[story_id] if story_id in constants.stories.keys() else story_id
        return "Read a storybook: <i>" + story_name + "</i>."
    elif event_name == "REFLECTION_RESPONDED":
        text: str = get_reflection_question(event_params)
        return "Answered this question:<span class='quote'><i>" + text + "</i></span>"
    elif event_name == "REFLECTION_PLAYBACK_START":
        return "Replaying the recorded answer"
    elif event_name == "CHALLENGE_PICKED":
        challenge_data = json.loads(event_params['CHALLENGE_JSON'])
        adult_goal = round(challenge_data['challenges_by_person'][str(person_adult.person_id)]["goal"])
        child_goal = round(challenge_data['challenges_by_person'][str(person_child.person_id)]["goal"])
        return "Picked a fitness challenge. Caregiver: {0} steps, child {1} steps.".format(adult_goal, child_goal)
    elif event_name == "PLAY_PROGRESS_ANIMATION":
        is_completed: bool = float(event_params['OVERALL_PROGRESS']) >= 1.0
        if is_completed:
            return "Completed family fitness challenge."
        else:
            return "Family did not complete the fitness challenge."
    elif event_name == "STORY_UNLOCKED":
        story_id: str = event_params['STORY_ID']
        story_name: str = constants.stories[story_id] if constants.stories[story_id] else event_params['STORY_ID']
        return "Unlocked a story chapter in: " + story_name + "."
    elif event_name == "GEOSTORY_SUBMITTED":
        prompt: str = get_geostory_prompt(event_params)
        return person_adult.name + " shared a community story. " \
                                   "<span class='quote'>Question: <i>" + prompt + "</i></span>"
    # elif event_name == "GEOSTORY_VIEWED":
    elif event_name == "GEOSTORY_PLAYED":
        if event_params['geostory_id'] in all_geostories:
            author = all_geostories[event_params['geostory_id']]['meta']['userNickname']
        else:
            author = ""
        # return person_adult.name  + " listened to a community story from <b>" + author + "</b>: "
        return "Listened to a community story from <b>" + author + "</b>: "
    elif event_name == "GEOSTORY_REACTION_ADDED":
        story_author_str: str = event_params["geoStoryAuthorNickname"]
        reaction_str: str = event_params["reaction"]
        return person_adult.name + " reacted with \"" + reaction_str + "\" to a story by " + story_author_str + "."
    elif event_name == "EMOTION_LOGGED_ADULT":
        emotion_str: str = "<span class='emotion'>"
        emotion_str += "</span>, <span class='emotion'>".join(json.loads(event_params['list_of_emotions']))
        emotion_str += "</span>"
        return person_adult.name + " logged this emotion: " + emotion_str + ". "
    elif event_name == "EMOTION_LOGGED_CHILD":
        emotion_str: str = "<span class='emotion'>"
        emotion_str += "</span>, <span class='emotion'>".join(json.loads(event_params['list_of_emotions']))
        emotion_str += "</span>"
        return person_child.name + " logged this emotion: " + emotion_str + ". "
    elif event_name == "APP_STARTUP":
        return "Starting the app"
    else:
        if 'eventParams' in event:
            return str(event_params)
        else:
            return ""


def get_filtered_logs(unfiltered_logs: dict, event_names: list) -> list:
    return list(filter(lambda key:
                       unfiltered_logs[key]['eventName'] in event_names,
                   unfiltered_logs))


def get_member_steps_on_day(member_fitness_data: dict, role: str, date_str: str) -> int:
    if date_str in member_fitness_data[role]:
        return member_fitness_data[role][date_str]
    else:
        return 0


def get_edit_uri(user: User, event: dict) -> Optional[str]:
    event_name: str = event['eventName']
    event_timestamp: int = int(event['timestamp'])
    event_params: dict

    if 'eventParams' in event:
        event_params = event['eventParams']

    if event_name == "REFLECTION_RESPONDED":
        # user_id: str = user.user_id
        # story_id: str = event_params["STORY_ID"]
        # page_id: str = str(event_params["PAGE_ID"])
        # return "/reflection/edit/{0}/{1}/{2}/{3}".format(user_id, story_id, page_id, event_timestamp)

        user_id: str = user.user_id
        date_string: str = firebase_utils.get_date_str_from_timestamp(event_timestamp)
        return config.URL_EDIT_LOG.format(user_id, date_string, event_timestamp)
    elif event_name == "GEOSTORY_SUBMITTED":
        user_id: str = user.user_id
        date_string: str = firebase_utils.get_date_str_from_timestamp(event_timestamp)
        return config.URL_EDIT_LOG.format(user_id, date_string, event_timestamp)
    else:
        return None


def get_transcript(event: dict) -> Optional[str]:
    event_name: str = event['eventName']
    event_params: dict

    if 'eventParams' in event:
        event_params = event['eventParams']

    if event_name == "REFLECTION_RESPONDED":
        if "transcript" in event_params:
            return event_params["transcript"]
        elif "TRANSCRIPT" in event_params:
            return event_params["TRANSCRIPT"]
        else:
            return ""
    elif event_name == "GEOSTORY_SUBMITTED":
        if "GEOSTORY_ID" not in event_params:
            return None

        if event_params["GEOSTORY_ID"] in all_geostories:
            return all_geostories[event_params["GEOSTORY_ID"]]['meta']['transcript']
        else:
            return "———"
        # return event_params['transcript'] if 'transcript' in event_params else ""
    elif event_name == "GEOSTORY_PLAYED":
        geostory_id: str = event_params['geostory_id']
        transcript = all_geostories[geostory_id]['meta']['transcript'] if geostory_id in all_geostories else geostory_id
        return transcript
    else:
        return None


def get_reflection_question(event_params: dict) -> str:
    story_id: str = event_params["STORY_ID"]
    page_id: int = event_params["PAGE_ID"]

    if story_id not in stories:
        return "({0})".format(story_id)
    else:
        contents: list = stories[story_id]['contents']

    if page_id > len(contents):
        return "({0}, {1})".format(story_id, page_id)
    else:
        page: dict = contents[page_id-1]
        return page['text']


def get_geostory_prompt(event_params: dict) -> str:
    story_id: str = event_params["PROMPT_PARENT_ID"]
    page_id: int = int(event_params["PROMPT_ID"])

    if story_id not in stories:
        return "({0})".format(story_id)
    else:
        contents: list = stories[story_id]['contents']

    if page_id > len(contents):
        return "({0}, {1})".format(story_id, page_id)
    else:
        page: dict = contents[page_id]
        return page['text']


def get_meta(event: dict) -> Optional[str]:
    event_name: str = event['eventName']
    event_params: dict

    if 'eventParams' in event :
        event_params = event['eventParams']

    if event_name == "GEOSTORY_PLAYED":
        geostory_id: str = event_params['geostory_id']

        if geostory_id in all_geostories:
            story = all_geostories[event_params['geostory_id']]
            return "&mdash; " + story['meta']['userNickname'] + ". " + story['meta']["bio"]
        else:
            return "&mdash; " + geostory_id
    else:
        return None