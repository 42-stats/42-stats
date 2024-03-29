from json.decoder import JSONDecodeError
import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
)

from src.utils import Utils
from src.request import Request
from requests_oauthlib import OAuth2Session
import pandas as pd
import json


def get_comments_for_user(api: OAuth2Session, login: str) -> any:
    try:
        user_id = Utils.get_user_id(api=api, login=login)
    except JSONDecodeError:
        return "skip"
    teams = Utils.get_evaluations_for_user(
        api=api, user_id=user_id, side="as_corrected"
    )
    if "comment" in teams.columns and not teams["comment"].isnull().all():
        return teams["comment"].tolist()
    else:
        return "skip"


import csv


def get_comments_for_campus(api: OAuth2Session, campus_id: int = 53):
    users = Utils.get_active_users_for_campus(api=api, campus_id=campus_id)
    with open("data.csv", "w", newline="") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerow(["login", "comment"])
        for user in users:
            comments = get_comments_for_user(api=api, login=user)
            if comments == "skip":
                continue
            for comment in comments:
                if comment is None:
                    continue
                writer.writerow([user, comment.replace("\n", " ")])


api = Request().api

get_comments_for_campus(api=api)
