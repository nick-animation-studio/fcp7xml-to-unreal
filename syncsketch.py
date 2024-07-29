import sys

import syncsketch

from matm.Episode import *
from matm.helpers import *


def connect_to_syncsketch():

    if sys.platform == "win32":
        sys.path.append(r"O:\Tools\nasutilities")
    elif sys.platform == "darwin":
        sys.path.append(r"/Volumes/anim/Tools/nasutilities")

    import common_utils

    username = "ChrisPerryTools"
    api_key = common_utils.getKeyPublic("ss_max_public.cfg", username)

    s = syncsketch.SyncSketchAPI(username, api_key)

    return s


def get_project_id(s):
    projects = s.get_projects()["objects"]
    if len(projects) != 1:
        print(f"ERROR: there is not exactly one project associated with this account")
        return None
    return projects[0]["id"]


def get_review_id(s, project_id, syncsketch_link):
    reviews = s.get_reviews_by_project_id(project_id)["objects"]
    syncsketch_link = syncsketch_link.replace("nick.", "www.")
    syncsketch_link = syncsketch_link.replace("#/", "/")
    for review in reviews:
        if review["reviewURL"] in syncsketch_link:
            return review["id"]
    print(f"ERROR: can't find a review matching the URL provided")
    return None


def get_item_id(s, review_id, syncsketch_link):
    items = s.get_media_by_review_id(review_id)["objects"]
    for item in items:
        if str(item["id"]) in syncsketch_link:
            return item["id"]
    print(f"ERROR: can't find an item matching the URL provided")
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
