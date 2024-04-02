from src.InterfaceResult import InterfaceResult
from src.Spinner import Spinner
from src.modules.base import BaseModule
from src.utils import Utils, clear_terminal, prompt


class OddsOfFailing(BaseModule):

    def run(self) -> str:
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
