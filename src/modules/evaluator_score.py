from src.InterfaceResult import InterfaceResult
from src.modules.base import BaseModule
from src.utils import Utils, clear_terminal, prompt
import threading
from src.animation_utils import Animation


class EvaluatorScore(BaseModule):

    def run(self) -> str:
        login = prompt("login: ")
        loading_animation = Animation(
            f"Fetching evaluations involving {login} as a corrector"
        )

        try:
            user_id = Utils.get_user_id(api=self.api, login=login)
            evals = Utils.get_evaluations_for_user(
                api=self.api, user_id=user_id, side="as_corrector"
            )
            evals = evals.dropna(subset=["final_mark"])
            average = evals["final_mark"].mean()
            result = average
            return_message = f"\rresult: {round(result, 2)}%\n"
        except Exception as e:
            return_message = f"error: {e}"
        finally:
            loading_animation.stop_animation()

        clear_terminal()
        print(return_message)

        return InterfaceResult.Success
