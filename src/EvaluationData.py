from src.Request            import Request
from src.Utils              import Utils
import threading
import time
import pandas as pd
from requests.exceptions import RequestException

class EvaluationData:

    def __init__(self):
        request = Request()
        self.api = request.api

    def get_evaluations(self, user_id : int, side : str) -> pd.DataFrame:

        evaluations = []
        page = 1

        while True:

            response = self.api.get(f'https://api.intra.42.fr/v2/users/{user_id}/scale_teams/{side}', params={'page': page, 'per_page': 100})
            response.raise_for_status()
            
            data = response.json()
            if not data:
                break

            evaluations.extend(data)
            page += 1

        df = pd.DataFrame(evaluations)
        return df

    def get_eval_average(self, login : str, side : str) -> str:

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
            evals = self.get_evaluations(user_id=user_id, side=side)
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
            raise Exception(f'{e}')

        result = average if side == 'as_corrector' else 100 - average

        return f'\rresult: {round(result, 2)}%\n'