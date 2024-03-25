from simple_term_menu                   import TerminalMenu

class BaseModule:
    def __init__(self, api):
        self.api = api
    
    def prompt(self, options: list):
        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()    
        return options[menu_entry_index]
    
    def run(self):
        raise NotImplementedError