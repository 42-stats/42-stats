from src.InterfaceResult import InterfaceResult
from src.Spinner import Spinner
from src.modules.base import BaseModule
from src.utils import Utils, clear_terminal, prompt, prompt_select
from collections import Counter
from collections import defaultdict
import numpy as np
import pandas as pd
import os
import json


class FriendsEval(BaseModule):
    """A class that performs evaluation network analysis for a user"""



    def format_result(
        self, corrected: dict, corrector: dict, user_login: str, top_n=None
    ) -> str:
        """Format the result of the evaluation network analysis.

        Args:
            corrected (dict): A dictionary containing the corrected data.
            corrector (dict): A dictionary containing the corrector data.
            user_login (str): The login of the user.
            top_n (int, optional): Number of top results to show.

        Returns:
            str: A string containing the formatted result.
        """
        # Sort
        sorted_counts1 = sorted(corrected.items(), key=lambda x: x[1][0], reverse=True)[:top_n]
        sorted_counts2 = sorted(corrector.items(), key=lambda x: x[1][0], reverse=True)[:top_n]

        # Combine both dicts
        combined_dict = dict(corrected)
        for login, (count, avg_score) in corrector.items():
            if login in combined_dict:
                existing_count, existing_avg_score = combined_dict[login]
                combined_dict[login] = (existing_count + count, (existing_avg_score * existing_count + avg_score * count) / (existing_count + count))
            else:
                combined_dict[login] = (count, avg_score)

        # Sorting combined dict 
        sorted_combined_counts = sorted(combined_dict.items(), key=lambda x: x[1][0], reverse=True)[:top_n]

        column_width = 15
        
        # Formatting 
        top_lines = []
        for i in range(max(len(sorted_counts1), len(sorted_counts2), len(sorted_combined_counts))):
            login1, (count1, avg1) = sorted_counts1[i] if i < len(sorted_counts1) else ("", (0, 0))
            login2, (count2, avg2) = sorted_counts2[i] if i < len(sorted_counts2) else ("", (0, 0))
            login3, (count3, avg3) = sorted_combined_counts[i] if i < len(sorted_combined_counts) else ("", (0, 0))

            count1_str = f"{count1:<10}" if login1 else " " * 10
            avg1_str = f"{avg1:<10.2f}" if login1 else " " * 10

            count2_str = f"{count2:<10}" if login2 else " " * 10
            avg2_str = f"{avg2:<10.2f}" if login2 else " " * 10

            line = (f"{login1: <{column_width}} {count1_str} {avg1_str} | "
                    f"{login2: <{column_width}} {count2_str} {avg2_str} | "
                    f"{login3: <{column_width}} {count3: <10}")
            top_lines.append(line)

        result_string = (f"Evaluation Network Analysis for {user_login} - Top Most Interacted With:\n\n"
                        f"Your Evaluator, times, average score  | You Evaluated, times, average score   | Combined\n"
                        f"{'-' * (3 * column_width + 55)}\n")
        result_string += "\n".join(top_lines)
        return result_string + "\n"


    def show_formatted_result(
    self, corrected_counter, corrector_counter, login
    ):
        """Show the formatted result of the evaluation network analysis.

        Args:
            corrected_counter: A dictionary containing the corrected data.
            corrector_counter: A dictionary containing the corrector data.
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



    def process_as_corrector_data(self, as_corrector_df):
        login_marks = {}

        for index, row in as_corrector_df.iterrows():
            correcteds = row.get('correcteds', [])
            final_mark = row.get('final_mark', np.nan)

            for corrected in correcteds:
                login = corrected.get('login')
                
                if login in login_marks:
                    login_marks[login].append(final_mark)
                else:
                    login_marks[login] = [final_mark]

        repeating_logins = {}
        for login, marks in login_marks.items():
            if len(marks) > 0:
                avg_mark = np.nanmean(marks) 
                repeating_logins[login] = (len(marks), avg_mark)
        
        return repeating_logins


    def process_as_corrected_data(self, as_corrected_df):
        corrector_marks = {}

        for index, row in as_corrected_df.iterrows():
            corrector = row.get('corrector', {})
            corrector_login = corrector.get('login')
            final_mark = row.get('final_mark', np.nan)

            if corrector_login:
                if corrector_login in corrector_marks:
                    corrector_marks[corrector_login].append(final_mark)
                else:
                    corrector_marks[corrector_login] = [final_mark]

        corrector_stats = {}
        for corrector, marks in corrector_marks.items():
            if len(marks) > 0:
                avg_mark = np.nanmean(marks) 
                corrector_stats[corrector] = (len(marks), avg_mark)

        return corrector_stats


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

                corrector_counter = self.process_as_corrector_data(as_corrector_df)
                corrected_counter = self.process_as_corrected_data(as_corrected_df)

            except Exception as e:
                raise Exception(f"An error occurred: {e}")

        return self.show_formatted_result(corrected_counter, corrector_counter, login)
