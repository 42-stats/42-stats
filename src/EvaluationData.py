from src.Request            import Request
from src.Utils              import Utils
import threading
import time
import pandas as pd
import math
import os

class EvaluationData:

    def __init__(self):
        self.api = None

    def get_evaluations(self, user_id : int, side : str) -> pd.DataFrame:

        evaluations = []
        page = 1
        while True:
            params = {'page': page, 'per_page': 100}
            response = self.api.get(f'https://api.intra.42.fr/v2/users/{user_id}/scale_teams/{side}', params=params)

            data = response.json()

            if not data:
                break

            for evaluation in data:
                evaluations.append(evaluation)
            
            page += 1

        df = pd.DataFrame(evaluations)
        return df

    def get_eval_average(self, login : str, side : str) -> int:

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

        if self.api is None:
            request = Request()
            self.api = request.api

        user_id = Utils.get_user_id(api=self.api, login=login, campus_id=53)
        evals = self.get_evaluations(user_id, side)

        done.set()
        loading_thread.join()

        evals = evals.dropna(subset=['final_mark'])
        average = evals['final_mark'].mean()

        os.system('clear')
        if side == 'as_corrected':
            print(f'\rresult: {int(100 - average)}%\n')
        else:    
            print(f'\rresult: {int(average)}%\n')

