import os
import sys
from typing import Optional
from requests_oauthlib import OAuth2Session
import pandas as pd
import json
import time
from simple_term_menu import TerminalMenu

from src.Spinner import Spinner


def clear_terminal():
    # Since Windows likes to be special the command is `cls` and not `clear`
    os.system("cls" if os.name == "nt" else "clear")


def clear_last_line():
    print("\033[A\033[K", end="")


def prompt(message: str):
    try:
        return input(message)
    except EOFError:
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)


def prompt_select(options: list, **kwargs):
    menu = TerminalMenu(
        options,
        menu_cursor="❯ ",
        menu_cursor_style=("fg_cyan", "bold"),
        menu_highlight_style=("bg_cyan", "fg_black"),
        **kwargs,
    )

    index = menu.show()

    if index is None:
        sys.exit(0)

    return options[index]


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
    def get_users(
        api: OAuth2Session,
        cursus_id: Optional[str | int] = None,
        pool_year: Optional[str | int] = None,
        pool_month: Optional[str | int] = None,
        primary_campus_id: Optional[str | int] = None,
    ) -> list:
        users = []

        params = {"per_page": 100}

        if cursus_id is not None:
            params["cursus_id"] = cursus_id

        if pool_year is not None:
            params["filter[pool_year]"] = pool_year

        if pool_month is not None:
            params["filter[pool_month]"] = pool_month

        if primary_campus_id is not None:
            params["filter[primary_campus_id]"] = primary_campus_id

        page = 1
        while True:
            params["page"] = page

            response = api.get("https://api.intra.42.fr/v2/users", params=params)
            data = response.json()

            if not data:
                break

            users.extend(data)

            page += 1

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
        api: OAuth2Session, user_id: int, side: str, spinner: Optional[Spinner] = None
    ) -> pd.DataFrame:
        evaluations = []
        page = 1

        while True:
            response = Utils.make_request_with_backoff(
                api,
                f"https://api.intra.42.fr/v2/users/{user_id}/scale_teams/{side}",
                params={"page": page, "per_page": 100},
                spinner=spinner,
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
    def get_projects_users(
        api: OAuth2Session,
        project_id: Optional[int] = None,
        campus_id: Optional[int] = None,
        cursus_id: Optional[int] = None,
        user_id: Optional[int | list[int]] = None,
    ) -> list:
        users = []

        params: dict = {"per_page": 100}

        if project_id is not None:
            params["filter[project_id]"] = project_id

        if campus_id is not None:
            params["filter[campus_id]"] = campus_id

        if cursus_id is not None:
            params["filter[cursus]"] = cursus_id

        if user_id is not None:
            params["filter[user_id]"] = id_list_to_string(user_id)

        page = 1
        while True:
            params["page"] = page

            response = api.get(
                f"https://api.intra.42.fr/v2/projects_users", params=params
            )
            data = response.json()

            if not data:
                break

            users.extend(data)

            page += 1

        return users

    @staticmethod
    def make_request_with_backoff(
        api: OAuth2Session,
        url: str,
        params: dict,
        max_retries: int = 5,
        spinner: Optional[Spinner] = None,
    ):
        retry_wait = 1
        for attempt in range(max_retries):
            response = api.get(url, params=params)
            if response.status_code == 429:
                if spinner is not None:
                    spinner.status_message(
                        f"Rate limit hit, retrying in {retry_wait} seconds..."
                    )
                else:
                    print(f"Rate limit hit, retrying in {retry_wait} seconds...")
                time.sleep(retry_wait)
                retry_wait *= 2
            else:
                return response
        raise Exception(f"Request {url} failed after max retries")


campuses = {
    "Paris": 1,
    "Lyon": 9,
    "Nineteen": 12,
    "Helsinki": 13,
    "Amsterdam": 14,
    "Khouribga": 16,
    "Sao_paulo": 20,
    "Benguerir": 21,
    "Madrid": 22,
    "Quebec": 25,
    "Tokyo": 26,
    "Rio De Janeiro": 28,
    "Seoul": 29,
    "Rome": 30,
    "Angouleme": 31,
    "Yerevan": 32,
    "Bangkok": 33,
    "Kuala Lumpur": 34,
    "Amman": 35,
    "Adelaide": 36,
    "Malaga": 37,
    "Lisboa": 38,
    "Heilbronn": 39,
    "Urduliz": 40,
    "Nice": 41,
    "Abu Dhabi": 43,
    "Wolfsburg": 44,
    "Alicante": 45,
    "Barcelona": 46,
    "Lausanne": 47,
    "Mulhouse": 48,
    "Istanbul": 49,
    "Kocaeli": 50,
    "Berlin": 51,
    "Florence": 52,
    "Vienna": 53,
    "Tétouan": 55,
    "Prague": 56,
    "London": 57,
    "Porto": 58,
    "Luxembourg": 59,
    "Perpignan": 60,
    "Belo Horizonte": 61,
    "Le Havre": 62,
    "Singapore": 64,
    "Antananarivo": 65,
    "Warsaw": 67,
    "Luanda": 68,
    "Gyeongsan": 69,
    "Nablus": 70,
    "Beirut": 71,
    "Milano": 72,
}


def prompt_campus(title="Select your campus\n") -> int:
    options = sorted(campuses.keys())
    # Promote 42 Vienna .-.
    campus = prompt_select(options, title=title, cursor_index=options.index("Vienna"))

    return campuses[campus]


def get_campus_name(campus_id: int) -> str:
    for name, id in campuses.items():
        if id == campus_id:
            return name
    return "Unknown"


def id_list_to_string(ids: int | list[int]):
    if isinstance(ids, int):
        return ids
    if isinstance(ids, list):
        return ",".join(map(str, ids))

    raise TypeError("ids must either be an int or a list of ints")
