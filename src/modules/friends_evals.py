from src.modules.base import BaseModule
from src.utils import Utils
from src.animation_utils import Animation
from collections import Counter
import pandas as pd
import os


class FriendsEval(BaseModule):

    def get_top_10(self, login_counts: dict, user_login: str) -> str:
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
        formatted_lines = []
        for line in range(total_lines):
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
        corrected_logins = [
            d["login"] for d in as_corrected_df["corrector"] if "login" in d
        ]
        corrector_logins = [
            d["login"] for d in as_corrector_df["correcteds"].explode() if "login" in d
        ]
        logins = list(corrected_logins + corrector_logins)
        return Counter(logins)

    def show_formatted_result(self, login_counts, login):
        os.system("clear")
        print(self.get_top_10(login_counts, login))
        if self.prompt(["get full list", "go back"]) == "go back":
            return "skip"
        return self.format_result(login_counts, login)

    def run(self) -> str:
        login = input("Login: ")
        try:
            loading_animation = Animation(f"Fetching all evaluations involving {login}")
            user_id = Utils.get_user_id(self.api, login)
            as_corrected_df = Utils.get_evaluations_for_user(
                self.api, user_id, side="as_corrected"
            )
            as_corrector_df = Utils.get_evaluations_for_user(
                self.api, user_id, side="as_corrector"
            )
            login_counts = self.count_logins(as_corrected_df, as_corrector_df)
            loading_animation.stop_animation()

        except Exception as e:
            loading_animation.stop_animation()
            raise Exception(f"An error occurred: {e}")

        return self.show_formatted_result(login_counts, login)
