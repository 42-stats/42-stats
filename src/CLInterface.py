import logging
from simple_term_menu import TerminalMenu
from src.InterfaceResult import InterfaceResult
from src.modules.base import BaseModule
import sys

from src.utils import clear_terminal, prompt_select


class Interface:
    def __init__(self, title: str, modules: dict[str, BaseModule], can_go_back=False):
        self.can_go_back = can_go_back
        self.title = title
        self.modules = modules
        self.logs = logging.getLogger("logs")

    def loop(self):
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

                selection = prompt_select(["Go Back", "Quit"])
                if selection == "Quit" or selection == None:
                    sys.exit(0)

            except Exception as error:
                self.error(error)

    def show_result(self, result: str):
        clear_terminal()

        print(result)

        # TODO: better solution for this
        if result != "skip" and prompt_select(["Go Back", "Quit"]) == "Quit":
            clear_terminal()
            sys.exit(0)

    def error(self, error: Exception):
        self.logs.error(f"We have encountered an unhandled error:\n{error}\n")

        if prompt_select(["Continue", "Quit"]) == "continue":
            return

        print("Bye")
        sys.exit(1)
