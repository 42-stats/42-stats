from src.modules.base               import BaseModule
from src.utils              import Utils
import threading
from src.animation_utils        import start_animation

class OddsOfFailing(BaseModule):

    def run(self) -> str:
        login = input('login: ')
        done_event = threading.Event()
        loading_thread = start_animation(done_event)

        try:
            user_id = Utils.get_user_id(api=self.api, login=login)
            evals = Utils.get_evaluations_for_user(api=self.api, user_id=user_id, side='as_corrected')
            evals = evals.dropna(subset=['final_mark'])
            average = evals['final_mark'].mean()
            result = 100 - average
            return_message = f'\rresult: {round(result, 2)}%\n'
        except Exception as e:
            return_message = f'error: {e}'
        finally:
            done_event.set()
            loading_thread.join()

        return return_message