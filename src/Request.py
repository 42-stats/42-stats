from oauthlib.oauth2    import BackendApplicationClient
from requests_oauthlib  import OAuth2Session
from os                 import environ
import dotenv

class Request:
    
    def __init__(self):
        self.api = self.set_api()
    
    def set_api(self):
        dotenv.load_dotenv()

        client_secret = environ['API_SECRET']
        client_id = environ['API_UID']

        client = BackendApplicationClient(client_id=client_id)
        api = OAuth2Session(client=client)
        
        api.fetch_token(token_url='https://api.intra.42.fr/oauth/token', client_id=client_id, client_secret=client_secret)
        return api