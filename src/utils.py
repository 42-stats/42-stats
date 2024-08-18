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
    """
    Clears the terminal screen.
    """
    os.system("cls" if os.name == "nt" else "clear")


def prompt(message: str):
    """
    Prompts the user for input with the given message.

    Args:
        message (str): The message to display to the user.

    Returns:
        str: The user's input.
    """
    try:
        return input(message)
    except EOFError:
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)


def prompt_select(options: list, **kwargs):
    """
    Displays a menu with the given options and prompts the user to select an option.

    Args:
        options (list): The list of options to display in the menu.

    Returns:
        str: The selected option.
    """
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
        """
        Retrieves the list of active users for a given campus.

        Args:
            api (OAuth2Session): The OAuth2Session object for making API requests.
            campus_id (int): The ID of the campus.

        Returns:
            list: The list of active users.
        """
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
        """
        Retrieves the ID of a user based on their login.

        Args:
            api (OAuth2Session): The OAuth2Session object for making API requests.
            login (str): The login of the user.

        Returns:
            int: The ID of the user.

        Raises:
            Exception: If the user is not found.
        """
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
        """
        Retrieves the evaluations for a user.

        Args:
            api (OAuth2Session): The OAuth2Session object for making API requests.
            user_id (int): The ID of the user.
            side (str): The side of the evaluations (e.g., "beginner", "advanced").
            spinner (Spinner, optional): The Spinner object for displaying a loading spinner. Defaults to None.

        Returns:
            pd.DataFrame: The evaluations as a pandas DataFrame.
        """
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

        with open(f"{side}.json", "w") as f:
            json.dump(evaluations, f, indent=4)
        df = pd.DataFrame(evaluations)
        return df

    @staticmethod
    def get_teams_for_user(api: OAuth2Session, user_id: int) -> list:
        """
        Retrieves the teams for a user.

        Args:
            api (OAuth2Session): The OAuth2Session object for making API requests.
            user_id (int): The ID of the user.

        Returns:
            list: The list of teams.
        """
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
        api: OAuth2Session,
        url: str,
        params: dict,
        max_retries: int = 5,
        spinner: Optional[Spinner] = None,
    ):
        """
        Makes a request to the API with exponential backoff for rate limiting.

        Args:
            api (OAuth2Session): The OAuth2Session object for making API requests.
            url (str): The URL to make the request to.
            params (dict): The parameters for the request.
            max_retries (int, optional): The maximum number of retries. Defaults to 5.
            spinner (Spinner, optional): The Spinner object for displaying a loading spinner. Defaults to None.

        Returns:
            requests.Response: The response object.

        Raises:
            Exception: If the request fails after the maximum number of retries.
        """
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
