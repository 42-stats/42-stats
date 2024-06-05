from src.Spinner import Spinner
from src.InterfaceResult import InterfaceResult
from src.modules.base import BaseModule
from src.utils import Utils, clear_terminal, prompt


class EvaluatorScore(BaseModule):
    """
    A class representing the evaluator score module.

    This module fetches evaluations involving a specific user as a corrector,
    calculates the average final mark, and returns the result.

    Attributes:
        api (API): The API object used for making API requests.

    Methods:
        run: Runs the evaluator score module and returns the result.
    """

    def run(self) -> str:
        login = prompt("login: ")

        with Spinner(f"Fetching evaluations involving {login} as a corrector"):
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

        clear_terminal()
        print(return_message)

        return InterfaceResult.Success
