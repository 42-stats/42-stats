from src.InterfaceResult import InterfaceResult
from src.modules.base import BaseModule
from src.utils import clear_terminal


class FeatureRequest(BaseModule):
    """
    A class representing a feature request module.

    This module is responsible for handling feature requests and providing a way to open an issue on GitHub.

    Attributes:
        None

    Methods:
        run: Executes the feature request module and prints a message with a link to open an issue on GitHub.

    """

    def run(self) -> str:
        """
        Executes the feature request module.

        This method clears the terminal, prints a message with a link to open an issue on GitHub,
        and returns a success message.

        Returns:
            str: A success message indicating that the feature request module has been executed successfully.

        """
        clear_terminal()
        print(
            "For feature requests, please open an issue: https://github.com/42-stats/42-stats/issues/"
        )

        return InterfaceResult.Success
