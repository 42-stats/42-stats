from simple_term_menu   import TerminalMenu
from src.EvaluationData     import EvaluationData
import os

welcome_message = '\rabied-ch: what would you like to know?'

class CLInterface:

    def __init__(self):
        try:
            self.evaluation_data = EvaluationData()
            self.welcome_user()
        except KeyboardInterrupt:
            return 1

    def open_an_issue(self):
        os.system('clear')
        print('\ropen an issue <3\n\nhttps://github.com/winstonallo/42-stats/issues\n')
        request = self.prompt(['go back', 'quit'])
        if request == 'quit':
            return 1
        else:
            self.welcome_user()

    def prompt(self, options : list) -> str:
        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()
        if menu_entry_index is not None:
            return options[menu_entry_index]

    def welcome_user(self) -> None:
        os.system('clear')
        print(welcome_message + '\n')
        request = self.prompt(['average score as an evaluator', 'odds that you will fail your next project', 'i have another question'])
        if request == 'i have another question':
            if self.open_an_issue() == 1:
                return
        else:
            login = input('login: ')
            self.evaluation_data.get_eval_average(login=login, side='as_corrector' if request == 'average score as an evaluator' else 'as_corrected')
            request = self.prompt(['go back', 'quit'])
            if request == 'quit':
                return 1
            else:
                self.welcome_user()
