from simple_term_menu import TerminalMenu
from src.modules.base import BaseModule
import sys

from src.utils import clear_terminal


class Interface:
    def __init__(self, title: str, modules: dict[str, BaseModule], can_go_back=False):
        self.can_go_back = can_go_back
        self.title = title
        self.modules = modules

    def loop(self):
        options = list(self.modules.keys())
        if self.can_go_back:
            options.append("go back")
        options.append("quit")

        while True:
            clear_terminal()
            print(self.title)

            selection = self.prompt(options)

            if selection == "quit":
                clear_terminal()
                print("Bye")
                sys.exit(0)

            if self.can_go_back and selection == "go back":
                return

            if selection not in self.modules:
                print(
                    f"Error: Non existent module selected (this should not happen): {selection}"
                )
                sys.exit(1)

            try:
                # TODO: The module should print the result itself
                result = self.modules[selection].run()

                if result is None:
                    continue

                self.show_result(result)
            except Exception as error:
                self.error(error)

    def show_result(self, result: str):
        clear_terminal()

        print(result)

        # TODO: better solution for this
        if result != "skip" and self.prompt(["go back", "quit"]) == "quit":
            clear_terminal()
            sys.exit(0)

    def error(self, error: Exception):
        # TODO: logger error?
        print("We have encountered an unhandled error:")
        print(error)
        print()

        if self.prompt(["continue", "quit"]) == "continue":
            return

        print("Bye")
        sys.exit(1)

    def prompt(self, options: list[str]) -> str:
        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()

        if menu_entry_index is None:
            clear_terminal()
            print("Bye")
            sys.exit(0)

        return options[menu_entry_index]
