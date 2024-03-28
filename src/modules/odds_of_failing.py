from src.modules.base import BaseModule
from src.utils import Utils
import threading
from src.animation_utils import Animation


class OddsOfFailing(BaseModule):

    def run(self) -> str:
        login = input("login: ")
        loading_animation = Animation(f"Fetching groups for {login}")

        try:
            user_id = Utils.get_user_id(api=self.api, login=login)
            evals = Utils.get_evaluations_for_user(
                api=self.api, user_id=user_id, side="as_corrected"
            )
            evals = evals.dropna(subset=["final_mark"])
            average = evals["final_mark"].mean()
            result = 100 - average
            return_message = f"\rresult: {round(result, 2)}%\n"
        except Exception as e:
            return_message = f"error: {e}"
        finally:
            loading_animation.stop_animation()

        return return_message
