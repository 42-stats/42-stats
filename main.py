from src.CLInterface import Interface
from src.modules.evaluator_score import EvaluatorScore
from src.modules.feature_request import FeatureRequest
from src.modules.friends_evals import FriendsEval
from src.modules.odds_of_failing import OddsOfFailing
from src.modules.piscine import Piscine
from src.request import Request


def main():
    """
    Entry point of the program.

    This function initializes the necessary objects and modules, and starts the main interface loop.
    If any unhandled exception occurs, it prints an error message and returns 1.
    """
    try:
        request = Request()
        api = request.api

        modules = {
            "Average score as an evaluator": EvaluatorScore(api),
            "Odds of failing next project": OddsOfFailing(api),
            "Evaluation network analysis": FriendsEval(api),
            "I have another question": FeatureRequest(api),
            "Piscine": Piscine(api),
        }

        interface = Interface("What would you like to know?", modules)
        interface.loop()
    except Exception as e:
        print(
            "\r\nunhandled error:",
            e,
            "please open an issue at https://github.com/winstonallo/42-stats/issues",
        )
        return 1


if __name__ == "__main__":
    main()
