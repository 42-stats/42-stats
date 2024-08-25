import logging
from simple_term_menu import TerminalMenu
from src.InterfaceResult import InterfaceResult
from src.modules.base import BaseModule
import sys

from src.utils import clear_terminal, prompt_select


class Interface:
    """
    Represents a command-line interface for interacting with modules.

    Attributes:
        can_go_back (bool): Indicates whether the interface allows going back to the previous menu.
        title (str): The title of the interface.
        modules (dict[str, BaseModule]): A dictionary of modules available in the interface.
        logs (logging.Logger): The logger used for logging interface events.
    """

    def __init__(self, title: str, modules: dict[str, BaseModule], can_go_back=False):
        """
        Initializes a new instance of the Interface class.

        Args:
            title (str): The title of the interface.
            modules (dict[str, BaseModule]): A dictionary of modules available in the interface.
            can_go_back (bool, optional): Indicates whether the interface allows going back to the previous menu. Defaults to False.
        """
        self.can_go_back = can_go_back
        self.title = title
        self.modules = modules
        self.logs = logging.getLogger("logs")

    def loop(self):
        """
        Starts the main loop of the interface, allowing the user to interact with the modules.
        """
        options = list(self.modules.keys())
        if self.can_go_back:
            options.append("Go Back")
        options.append("Quit")

        while True:
            clear_terminal()
            print(self.title)

            selection = prompt_select(options)

            if selection == "Quit":
                clear_terminal()
                print("Bye")
                sys.exit(0)

            if self.can_go_back and selection == "Go Back":
                return

            if selection not in self.modules:
                print(
                    f"Error: Non existent module selected (this should not happen): {selection}"
                )
                sys.exit(1)

            try:
                result = self.modules[selection].run()

                if result == InterfaceResult.Exit:
                    sys.exit(0)

                if result == InterfaceResult.Skip:
                    continue

                if result == InterfaceResult.GoBack:
                    return

                selection = prompt_select(["Go Back", "Quit"])
                if selection == "Quit" or selection == None:
                    sys.exit(0)

            except Exception as error:
                self.error(error)

    def show_result(self, result: str):
        """
        Displays the result of a module execution.

        Args:
            result (str): The result to be displayed.
        """
        clear_terminal()

        print(result)

        # TODO: better solution for this
        if result != "skip" and prompt_select(["Go Back", "Quit"]) == "Quit":
            clear_terminal()
            sys.exit(0)

    def error(self, error: Exception):
        """
        Handles an unhandled error encountered during module execution.

        Args:
            error (Exception): The error that occurred.
        """
        self.logs.error(f"We have encountered an unhandled error:\n{error}\n")

        if prompt_select(["Continue", "Quit"]) == "continue":
            return

        print("Bye")
        sys.exit(1)
