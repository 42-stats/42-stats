from src.modules.base               import BaseModule
from src.utils              import Utils
import threading
from src.animation_utils import start_animation


class FriendsEval(BaseModule):

    def run(self) -> str:
        login = input('login: ')
        as_corrected = Utils.get_evaluations_for_user(self.api, Utils.get_user_id(self.api, login), side='as_corrected')
        
        correctors = as_corrected['corrector']
        correctors.to_json('evals.json', indent=4)
        evals = correctors.groupby('login').size()
