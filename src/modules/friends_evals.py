from src.modules.base import BaseModule
from src.utils import Utils
import threading
from src.animation_utils import start_animation

class FriendsEval(BaseModule):

    def run(self) -> list:
        login = input("Login: ")
        try:
            done_event = threading.Event()
            loading_thread = start_animation(done_event, "Fetching data...")

            user_id = Utils.get_user_id(self.api, login)
            as_corrected_df = Utils.get_evaluations_for_user(self.api, user_id, side="as_corrected")
            as_corrector_df = Utils.get_evaluations_for_user(self.api, user_id, side="as_corrector")

            done_event.set()
            loading_thread.join()

            corrected_logins = [d['login'] for d in as_corrected_df['corrector'] if 'login' in d]
            corrector_logins = [d['login'] for d in as_corrector_df['correcteds'].explode() if 'login' in d]

            evals = list(corrected_logins + corrector_logins)

        except Exception as e:
            evals = []
            raise Exception(f"An error occurred: {e}")

        return evals

