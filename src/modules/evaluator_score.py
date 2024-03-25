from src.modules.base               import BaseModule
from requests_oauthlib import OAuth2Session
from src.utils              import Utils
import threading
import time 
import pandas as pd

class EvaluatorScore(BaseModule):

    def run(self) -> str:

        login = input('login: ')

        def animation():
            chars = ['|', '/', '-', '\\']
            idx = 0
            while not done.is_set():
                print(f'\rintra fighting for its life rn {chars[idx % len(chars)]}', end="")
                idx += 1
                time.sleep(0.1)

        
        done = threading.Event()
        loading_thread = threading.Thread(target=animation)
        loading_thread.start()

        try:
            user_id = Utils.get_user_id(api=self.api, login=login)
            evals = pd.DataFrame(Utils.get_evaluations(api=self.api, user_id=user_id, side='as_corrector'))
        except Exception as e:
            done.set()
            loading_thread.join()
            raise Exception(f'could not get evaluation average: {e}')
        
        done.set()
        loading_thread.join()

        try:
            evals = evals.dropna(subset=['final_mark'])
            average = evals['final_mark'].mean()
        except Exception as e:
            raise Exception(f'could not get evaluation average: {e}')

        result = average

        return f'\rresult: {round(result, 2)}%\n'