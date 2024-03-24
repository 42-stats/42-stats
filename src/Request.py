from oauthlib.oauth2    import BackendApplicationClient
from requests_oauthlib  import OAuth2Session
import os
import dotenv

class Request:

    def __init__(self):
        self.api = self.set_api()

    def set_api(self):
        dotenv.load_dotenv()

        client_secret = os.getenv('API_SECRET')
        if client_secret is None:
        	raise ValueError('error: .env variable "API_SECRET" not found')
        client_id = os.getenv('API_UID')
        if client_id is None:
        	raise ValueError('error: .env variable "API_UID" not found')
        client = BackendApplicationClient(client_id=client_id)
        api = OAuth2Session(client=client)

        api.fetch_token(token_url='https://api.intra.42.fr/oauth/token', client_id=client_id, client_secret=client_secret)
        return api
