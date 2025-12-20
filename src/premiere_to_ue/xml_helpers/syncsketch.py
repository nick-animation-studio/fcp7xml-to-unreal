import os

import syncsketch
from dotenv import load_dotenv

from premiere_to_ue.models.Episode import Episode


def connect_to_syncsketch():
    load_dotenv()
    SYNCSKETCH_USERNAME = os.getenv["SYNCSKETCH_USERNAME"]
    SYNCSKETCH_API_KEY = os.getenv["SYNCSKETCH_API_KEY"]

    if not SYNCSKETCH_USERNAME or not SYNCSKETCH_API_KEY:
        print("ERROR: syncsketch .env file not configured properly, missing values.")
        return
    else:
        print(f"INFO: using SYNCSKETCH_USERNAME: {SYNCSKETCH_USERNAME}")
        print(f"INFO: using SYNCSKETCH_API_KEY: {SYNCSKETCH_API_KEY}")

    s = syncsketch.SyncSketchAPI(SYNCSKETCH_USERNAME, SYNCSKETCH_API_KEY)

    return s


def get_project_id(s):
    projects = s.get_projects()["objects"]
    if len(projects) != 1:
        print("ERROR: there is not exactly one project associated with this account")
        return None
    return projects[0]["id"]


def get_review_id(s, project_id, syncsketch_link):
    reviews = s.get_reviews_by_project_id(project_id, limit=1000)["objects"]
    syncsketch_link = syncsketch_link.replace("nick.", "www.")
    syncsketch_link = syncsketch_link.replace("#/", "/")
    for review in reviews:
        if review["reviewURL"] in syncsketch_link:
            return review["id"]
    print("ERROR: can't find a review matching the URL provided")
    return None


def get_item_id(s, review_id, syncsketch_link):
    items = s.get_media_by_review_id(review_id)["objects"]
    for item in items:
        if str(item["id"]) in syncsketch_link:
            return item["id"]
    print("ERROR: can't find an item matching the URL provided")
    return None


def get_name(syncsketch_link):
    s = connect_to_syncsketch()
    if s:
        print("Successfully connected to syncsketch")
    project_id = get_project_id(s)
    if project_id is None:
        return
    review_id = get_review_id(s, project_id, syncsketch_link)
    if review_id is None:
        return
    item_id = get_item_id(s, review_id, syncsketch_link)
    if item_id is None:
        return
    item = s.get_item(item_id)
    return item["name"]


def max_post_comment(s, item_id, comment, review_id, start_frame):
    # need the frame offset from the item.
    item = s.get_item(item_id)
    ff = item["first_frame"]
    frame = start_frame + ff
    print(f"Posting to frame: {frame}")
    s.add_comment(item_id, comment, review_id, start_frame)


def upload(episode: Episode, syncsketch_link: str):
    print("Starting to upload notes to syncsketch")

    s = connect_to_syncsketch()
    if s:
        print("Successfully connected to syncsketch")
    project_id = get_project_id(s)
    if project_id is None:
        return
    review_id = get_review_id(s, project_id, syncsketch_link)
    if review_id is None:
        return
    item_id = get_item_id(s, review_id, syncsketch_link)
    if item_id is None:
        return

    comments_missing_tag = []

    print(f"Found {len(episode.notes)} comments to upload")
    for note in episode.notes:
        tagged = len(note.tags) > 0
        if not tagged:
            comments_missing_tag.append(note)
        tag_string = " ".join(str(tag) for tag in note.tags)
        max_post_comment(s, item_id, f"{tag_string} {note.text}", review_id, note.sf)
    print("Successfully uploaded notes to syncsketch")
    if len(comments_missing_tag) > 0:
        warning = "Warning, found thefollowing comments missing tags. Please review\n"
        for note in comments_missing_tag:
            warning += f"Start frame: {note.sf} {note.text[0:10]} ...\n"
        return warning
    return ""
