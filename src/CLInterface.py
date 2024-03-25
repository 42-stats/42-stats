from simple_term_menu   import TerminalMenu
from src.EvaluationData     import EvaluationData
import os
import logging
import sys

logging.basicConfig(level=logging.WARNING)
welcome_message = '\rwhat would you like to know?\n'

class CLInterface:

    def __init__(self):
        self.logs = logging.getLogger('logs')
        try:
            self.evaluation_data = EvaluationData()
            self.welcome_user()
        except KeyboardInterrupt:
            sys.exit(1)

    def open_an_issue(self) -> str:
        os.system('clear')
        print('\rfor feature requests, please open an issue: https://github.com/winstonallo/42-stats/issues\n')
        request = self.prompt(['go back', 'quit'])
        if request == 'quit':
            sys.exit(0)
        else:
            self.welcome_user()
        return 0
    def prompt(self, options : list) -> str:
        terminal_menu = TerminalMenu(options)
        menu_entry_index = terminal_menu.show()
        if menu_entry_index is not None:
            return options[menu_entry_index]
        return ""

    def welcome_user(self) -> None:
        os.system('clear')
        print(welcome_message)
        prompt = [	'average score as an evaluator',
        			'odds that you will fail your next project',
              		'i have another question',
                    'quit']
        request = self.prompt(prompt)
        if request == 'quit':
            sys.exit(0)
        elif request == 'i have another question':
            self.open_an_issue() == 'quit'
        else:
            login = input('login: ')
            try:
                self.evaluation_data.get_eval_average(login=login, side='as_corrector' if request == 'average score as an evaluator' else 'as_corrected')
            except ValueError as e:
                self.logs.error(f' login not found in 42 network users: {e}')
            request = self.prompt(['go back', 'quit'])
            if request == 'quit':
                return
            else:
                self.welcome_user()
