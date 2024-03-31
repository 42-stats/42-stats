import sys
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import os
import dotenv


class Request:
    """
    Represents a request object used to interact with an API.
    """

    def __init__(self):
        self.api = self.set_api()

    def set_api(self):
        """
        Sets up the API client and fetches the access token.

        Returns:
            api (OAuth2Session): The API client with the access token.
        """
        dotenv.load_dotenv()

        client_secret = os.getenv("API_SECRET")
        client_id = os.getenv("API_UID")
        if client_secret is None or client_id is None:
            missing_vars = []
            if client_secret is None:
                missing_vars.append("API_SECRET")
            if client_id is None:
                missing_vars.append("API_UID")
            missing_vars = ", ".join(missing_vars)

            print(f"Error: There are some env variables missing: {missing_vars}")

            sys.exit(1)

        client = BackendApplicationClient(client_id=client_id)
        api = OAuth2Session(client=client)

        try:
            api.fetch_token(
                token_url="https://api.intra.42.fr/oauth/token",
                client_id=client_id,
                client_secret=client_secret,
            )
        except:
            print(
                "Failed to get access token.\nAre you sure that you provided the correct Id and Secret?"
            )

            sys.exit(1)
        return api
