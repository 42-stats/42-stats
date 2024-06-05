from src.InterfaceResult import InterfaceResult
from src.Spinner import Spinner
from src.modules.base import BaseModule
from src.utils import Utils, clear_terminal, prompt, prompt_select
from collections import Counter
import pandas as pd
import os


class FriendsEval(BaseModule):
    """A class that performs evaluation network analysis for a user"""

    def get_top_10(self, login_counts: dict, user_login: str) -> str:
        """Get the top 10 most interacted with users.

        Args:
            login_counts (dict): A dictionary containing the login counts of friends.
            user_login (str): The login of the user.

        Returns:
            str: A string containing the top 10 most interacted with friends.
        """
        sorted_counts = sorted(login_counts.items(), key=lambda x: x[1], reverse=True)
        top_10 = []
        for i in range(min(10, len(sorted_counts))):
            login, count = sorted_counts[i]
            top_10.append(f"{login}: {count}")
        result_string = f"Evaluation Network Analysis for {user_login} - Top 10 Most Interacted With:\n\n"
        result_string += "\n".join(top_10)
        return result_string + "\n"

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
        self, login_counts: dict, user_login: str, entries_per_line=6
    ) -> str:
        """Format the result of the evaluation network analysis.

        Args:
            login_counts (dict): A dictionary containing the login counts of friends.
            user_login (str): The login of the user.
            entries_per_line (int, optional): The number of entries per line. Defaults to 6.

        Returns:
            str: A string containing the formatted result.
        """
        sorted_counts = sorted(login_counts.items(), key=lambda x: x[1], reverse=True)
        total_entries = len(sorted_counts)
        total_lines = (total_entries + entries_per_line - 1) // entries_per_line
        formatted_lines = self.append_sorted_counts_to_lines(
            sorted_counts, total_lines, entries_per_line, total_entries
        )

        result_string = (
            f"Full Evaluation Network Analysis for {user_login}:\n\n{formatted_lines}\n"
        )
        return result_string

    def count_logins(
        self, as_corrected_df: pd.DataFrame, as_corrector_df: pd.DataFrame
    ) -> Counter:
        """Count the logins of users.

        Args:
            as_corrected_df (pd.DataFrame): A DataFrame containing evaluations where the user is corrected.
            as_corrector_df (pd.DataFrame): A DataFrame containing evaluations where the user is the corrector.

        Returns:
            Counter: A Counter object containing the login counts of users.
        """
        corrected_logins = [
            d["login"] for d in as_corrected_df["corrector"] if "login" in d
        ]
        corrector_logins = [
            d["login"] for d in as_corrector_df["correcteds"].explode() if "login" in d
        ]
        logins = list(corrected_logins + corrector_logins)
        return Counter(logins)

    def show_formatted_result(self, login_counts, login):
        """Show the formatted result of the evaluation network analysis.

        Args:
            login_counts: A Counter object containing the login counts of users.
            login: The login of the user.

        Returns:
            InterfaceResult: The result of the interface.
        """
        os.system("clear")
        print(self.get_top_10(login_counts, login))
        if prompt_select(["get full list", "go back"]) == "go back":
            clear_terminal()
            return InterfaceResult.Skip

        clear_terminal()
        print(self.format_result(login_counts, login))
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
                login_counts = self.count_logins(as_corrected_df, as_corrector_df)

            except Exception as e:
                raise Exception(f"An error occurred: {e}")

        return self.show_formatted_result(login_counts, login)
