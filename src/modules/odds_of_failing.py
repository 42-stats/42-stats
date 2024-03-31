from src.InterfaceResult import InterfaceResult
from src.Spinner import Spinner
from src.modules.base import BaseModule
from src.utils import Utils, clear_terminal, prompt


class OddsOfFailing(BaseModule):
    """
    A module that calculates the odds of failing based on evaluation scores.

    This module prompts the user for a login, fetches the evaluation scores for the user,
    calculates the average score, and returns the odds of failing as a percentage.

    Attributes:
        api: The API object used for making API requests.

    Methods:
        run: Runs the module and returns the result as a string.
    """

    def run(self) -> str:
        """
        Runs the module and returns the result as a string.

        Returns:
            A string representing the result of the module.
        """
        login = prompt("login: ")

        with Spinner(f"Fetching groups for {login}") as spinner:
            try:
                user_id = Utils.get_user_id(api=self.api, login=login)
                evals = Utils.get_evaluations_for_user(
                    api=self.api, user_id=user_id, side="as_corrected", spinner=spinner
                )
                evals = evals.dropna(subset=["final_mark"])
                average = evals["final_mark"].clip(upper=100).mean()
                result = 100 - average
                return_message = f"\rresult: {round(result, 2)}%\n"
            except Exception as e:
                return_message = f"error: {e}"

        clear_terminal()
        print(return_message)

        return InterfaceResult.Success
