from src.InterfaceResult import InterfaceResult
from src.Spinner import Spinner
from src.modules.base import BaseModule
from src.utils import Utils, clear_terminal, prompt, prompt_select
from collections import Counter
import pandas as pd
import os


class FriendsEval(BaseModule):
    """A class that performs evaluation network analysis for a user"""

    def append_sorted_counts_to_lines(
        self, sorted_counts, total_lines, entries_per_line, total_entries
    ) -> str:
        """Append sorted counts to lines for formatting.

        Args:
            sorted_counts: A list of sorted counts.
            total_lines: The total number of lines.
            entries_per_line: The number of entries per line.
            total_entries: The total number of entries.

        Returns:
            str: A string containing the formatted lines.
        """
        formatted_lines = []
        for line in range(total_lines):
            line_entries = []
            for i in range(entries_per_line):
                index = line * entries_per_line + i
                if index < total_entries:
                    login, count = sorted_counts[index]
                    if len(login) < 5:
                        login += "  "
                    line_entries.append(f"{login}: {count}")
            formatted_lines.append("\t".join(line_entries))
        return "\n".join(formatted_lines)

    def format_result(
        self, corrected: dict, corrector: dict, user_login: str, top_n=None
    ) -> str:
        """Format the result of the evaluation network analysis.

        Args:
            login_counts (dict): A dictionary containing the login counts of friends.
            user_login (str): The login of the user.
            entries_per_line (int, optional): The number of entries per line. Defaults to 6.

        Returns:
            str: A string containing the formatted result.
        """
        sorted_counts1 = sorted(corrected.items(), key=lambda x: x[1], reverse=True)[:top_n]
        sorted_counts2 = sorted(corrector.items(), key=lambda x: x[1], reverse=True)[:top_n]

        combined_dict = dict(corrected)
        for login, count in corrector.items():
            if login in combined_dict:
                combined_dict[login] += count
            else:
                combined_dict[login] = count

        sorted_combined_counts = sorted(combined_dict.items(), key=lambda x: x[1], reverse=True)

        column_width = 20
        
        top_10_lines = []
        for i in range(max(len(sorted_counts1), len(sorted_counts2))):
            login1, count1 = sorted_counts1[i] if i < len(sorted_counts1) else ("", "")
            login2, count2 = sorted_counts2[i] if i < len(sorted_counts2) else ("", "")
            login3, count3 = sorted_combined_counts[i] if i < len(sorted_combined_counts) else ("", "")

            line = (f"{login1: <{column_width}} {count1: <10} | "
                    f"{login2: <{column_width}} {count2: <10} | "
                    f"{login3: <{column_width}} {count3: <10}")
            top_10_lines.append(line)

        result_string = (f"Evaluation Network Analysis for {user_login} - Top Most Interacted With:\n\n"
                        f"Corrected (They evaluated you)  | Corrector (You evaluated them)  | Combined\n"
                        f"{'-' * (3 * column_width + 20)}\n")
        result_string += "\n".join(top_10_lines)
        return result_string + "\n"

    def count_corrector_logins(self, as_corrector_df: pd.DataFrame) -> Counter:
        """
        Count the logins of users where the user is the corrector.

        Args:
            as_corrector_df (pd.DataFrame): A DataFrame containing evaluations where the user is the corrector.

        Returns:
            Counter: A Counter object containing the login counts of users where the user is the corrector.
        """
        corrector_logins = [
            d["login"] for d in as_corrector_df["correcteds"].explode() if isinstance(d, dict) and "login" in d
        ]
        return Counter(corrector_logins)
    

    def count_corrected_logins(self, as_corrected_df: pd.DataFrame) -> Counter:
        """
        Count the logins of users where the user is corrected.

        Args:
            as_corrected_df (pd.DataFrame): A DataFrame containing evaluations where the user is corrected.

        Returns:
            Counter: A Counter object containing the login counts of users where the user is corrected.
        """
        corrected_logins = [
            d["login"] for d in as_corrected_df["corrector"] if isinstance(d, dict) and "login" in d
        ]
        return Counter(corrected_logins)


    def show_formatted_result(self, corrected_counter, corrector_counter, login):
        """Show the formatted result of the evaluation network analysis.

        Args:
            login_counts: A Counter object containing the login counts of users.
            login: The login of the user.

        Returns:
            InterfaceResult: The result of the interface.
        """
        os.system("clear")
        print(self.format_result(corrected_counter, corrector_counter, login, 10))
        if prompt_select(["get full list", "go back"]) == "go back":
            clear_terminal()
            return InterfaceResult.Skip

        clear_terminal()
        print(self.format_result(corrected_counter, corrector_counter, login))
        return InterfaceResult.Success

    def run(self) -> str:
        """Run the evaluation network analysis.

        Returns:
            str: The result of the evaluation network analysis.
        """
        login = prompt("Login: ")

        with Spinner(f"Fetching all evaluations involving {login}") as spinner:
            try:
                user_id = Utils.get_user_id(self.api, login)
                as_corrected_df = Utils.get_evaluations_for_user(
                    self.api, user_id, side="as_corrected", spinner=spinner
                )
                as_corrector_df = Utils.get_evaluations_for_user(
                    self.api, user_id, side="as_corrector", spinner=spinner
                )
                corrected_counter = self.count_corrected_logins(as_corrected_df)
                corrector_counter = self.count_corrector_logins(as_corrector_df)

            except Exception as e:
                raise Exception(f"An error occurred: {e}")

        return self.show_formatted_result(corrected_counter, corrector_counter, login)
