from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import pandas as pd

class Utils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def get_users(api: OAuth2Session, campus_id: int) -> list:
        users = []
        page = 1
        while True:
            params = {'page': page, 'per_page': 100}
            response = api.get(f'https://api.intra.42.fr/v2/campus/{campus_id}/users', params=params)
            data = response.json()

            if not data:
                break

            for user in data:
                if user.get('active?', False):
                    users.append(user['login'])

            page += 1

        users = sorted(users)

        with open('users.txt', 'w') as users_txt:
            for user in users:
                users_txt.write(user + '\n')

        return users

    @staticmethod
    def get_user_id(api: OAuth2Session, login: str, campus_id: int) -> int:
        page = 1
        while True:
            params = {'page': page, 'per_page': 100}
            response = api.get(f'https://api.intra.42.fr/v2/campus/{campus_id}/users', params=params)
            users = response.json()

            if not users:
                break

            for user in users:
                if user['login'] == login:
                    return user['id']

            page += 1

        return None
