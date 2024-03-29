import os
from requests_oauthlib import OAuth2Session
import pandas as pd
import json
import time


def clear_terminal():
    # Since Windows likes to be special the command is `cls` and not `clear`
    os.system("cls" if os.name == "nt" else "clear")


class Utils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_active_users_for_campus(api: OAuth2Session, campus_id: int) -> list:
        users = []
        page = 1
        while True:
            params = {"page": page, "per_page": 100}
            response = api.get(
                f"https://api.intra.42.fr/v2/campus/{campus_id}/users", params=params
            )
            data = response.json()

            if not data:
                break

            for user in data:
                if user.get("active?", False):
                    users.append(user["login"])

            page += 1

        users = sorted(users)

        with open("users.txt", "w") as users_txt:
            for user in users:
                users_txt.write(user + "\n")

        return users

    @staticmethod
    def get_user_id(api: OAuth2Session, login: str):
        if not login or len(login) < 3:
            raise Exception("user not found")
        response = api.get(f"https://api.intra.42.fr/v2/users/{login}")
        user = response.json()
        id = user.get("id")
        if id is None:
            raise Exception("user not found")
        return id

    @staticmethod
    def get_evaluations_for_user(
        api: OAuth2Session, user_id: int, side: str
    ) -> pd.DataFrame:
        evaluations = []
        page = 1

        while True:
            response = Utils.make_request_with_backoff(
                api,
                f"https://api.intra.42.fr/v2/users/{user_id}/scale_teams/{side}",
                params={"page": page, "per_page": 100},
            )
            response.raise_for_status()

            data = response.json()
            if not data:
                break

            evaluations.extend(data)
            page += 1

        with open("evals.json", "w") as f:
            json.dump(evaluations, f, indent=4)
        df = pd.DataFrame(evaluations)
        return df

    @staticmethod
    def get_teams_for_user(api: OAuth2Session, user_id: int) -> list:
        teams = []
        page = 1

        while True:
            response = Utils.make_request_with_backoff(
                api,
                f"https://api.intra.42.fr/v2/users/{user_id}/projects_users",
                params={"page": page, "per_page": 100},
            )
            response.raise_for_status()

            data = response.json()
            if not data:
                break
            teams.extend(data)
            page += 1

        return teams

    @staticmethod
    def make_request_with_backoff(
        api: OAuth2Session, url: str, params: dict, max_retries: int = 5
    ):
        retry_wait = 1
        for attempt in range(max_retries):
            response = api.get(url, params=params)
            if response.status_code == 429:
                print(f"Rate limit hit, retrying in {retry_wait} seconds...")
                time.sleep(retry_wait)
                retry_wait *= 2
            else:
                return response
        raise Exception(f"Request {url} failed after max retries")
