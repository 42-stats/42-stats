from simple_term_menu import TerminalMenu
import logging


class BaseModule:
    def __init__(self, api):
        self.api = api
        self.logs = logging.getLogger("logs")

    def prompt(self, options: list):
        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()
        return options[menu_entry_index]

    def run(self):
        raise NotImplementedError
