from simple_term_menu import TerminalMenu
from src.modules.evaluator_score import EvaluatorScore
from src.modules.odds_of_failing import OddsOfFailing
from src.modules.feature_request import FeatureRequest
from src.modules.analyze_feedback import FeedbackAnalyzer
from src.request import Request
import os
import logging
import sys

logging.basicConfig(level=logging.WARNING)
welcome_message = "\rwhat would you like to know?\n"


class Interface:

    def __init__(self):
        request = Request()
        self.api = request.api
        self.logs = logging.getLogger("logs")
        self.modules = {
            "average score as an evaluator": EvaluatorScore(self.api),
            "odds of failing next project": OddsOfFailing(self.api),
            "i have another question": FeatureRequest(self.api),
            "analyze my weaknesses": FeedbackAnalyzer(self.api),
        }
        try:
            self.welcome_user()
        except KeyboardInterrupt:
            os.system("clear")
            sys.exit(1)

    def error(self, message: str):
        self.logs.error(message)
        if self.prompt(["go back", "quit"]) == "quit":
            os.system("clear")
            sys.exit(0)
        else:
            self.welcome_user()

    def prompt(self, options: list) -> str:
        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()

        if menu_entry_index is None:
            print("Bye")
            sys.exit(0)

        return options[menu_entry_index]

    def welcome_user(self) -> None:
        os.system("clear")
        print(welcome_message)
        options = list(self.modules.keys()) + ["quit"]
        request = self.prompt(options)
        result = ""
        if request in self.modules:
            try:
                result = self.modules[request].run()
            except Exception as e:
                self.error(f"\rerror: {e}")
            self.show_result(result=result)
        elif request == "quit":
            os.system("clear")
            sys.exit(0)

    def show_result(self, result: str):
        os.system("clear")
        print(f"\r{result}")
        if self.prompt(["go back", "quit"]) == "quit":
            os.system("clear")
            sys.exit(0)
        else:
            self.welcome_user()
