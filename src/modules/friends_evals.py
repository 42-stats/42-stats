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
            login_counts (dict): A dictionary containing the login counts of friends.
            user_login (str): The login of the user.

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

        sorted_combined_counts = sorted(combined_dict.items(), key=lambda x: x[1], reverse=True)[:top_n]

        column_width = 20
        
        top_lines = []
        for i in range(max(len(sorted_counts1), len(sorted_counts2), len(sorted_combined_counts))):
            login1, count1 = sorted_counts1[i] if i < len(sorted_counts1) else ("", "")
            login2, count2 = sorted_counts2[i] if i < len(sorted_counts2) else ("", "")
            login3, count3 = sorted_combined_counts[i] if i < len(sorted_combined_counts) else ("", "")

            line = (f"{login1: <{column_width}} {count1: <10} | "
                    f"{login2: <{column_width}} {count2: <10} | "
                    f"{login3: <{column_width}} {count3: <10}")
            top_lines.append(line)

        result_string = (f"Evaluation Network Analysis for {user_login} - Top Most Interacted With:\n\n"
                        f"Corrected (They evaluated you)  | Corrector (You evaluated them)  | Combined\n"
                        f"{'-' * (3 * column_width + 20)}\n")
        result_string += "\n".join(top_lines)
        return result_string + "\n"


    def show_formatted_result(
        self, corrected_counter, corrector_counter, login
    ):
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


    def process_corrector_data(corrector_data):
        login_marks = {}
        
        # Iterate over each evaluation in the corrector data
        for evaluation in corrector_data:
            corrected_login = evaluation['correcteds'][0]['login']
            final_mark = evaluation['final_mark']
            
            # Collect the marks for each login
            if corrected_login in login_marks:
                login_marks[corrected_login].append(final_mark)
            else:
                login_marks[corrected_login] = [final_mark]
        
        # Calculate the number of repeating logins and their average marks
        repeating_logins = {}
        for login, marks in login_marks.items():
            if len(marks) > 1:
                avg_mark = sum(marks) / len(marks)
                repeating_logins[login] = (len(marks), avg_mark)
        
        return repeating_logins

    # Example usage
    corrector_json_data = [
        # JSON data
    ]
    result = process_corrector_data(corrector_json_data)
    print(result)


    def process_as_corrector_data(self, as_corrector_df):
        login_marks = {}

        # Iterate over each row in the DataFrame
        for index, row in as_corrector_df.iterrows():
            # Get the list of correcteds and the final mark from each row
            correcteds = row.get('correcteds', [])
            final_mark = row.get('final_mark', np.nan)

            # Process each corrected login
            for corrected in correcteds:
                login = corrected.get('login')
                
                # Collect the marks for each login
                if login in login_marks:
                    login_marks[login].append(final_mark)
                else:
                    login_marks[login] = [final_mark]

        # Calculate the number of repeating logins and their average marks
        repeating_logins = {}
        for login, marks in login_marks.items():
            if len(marks) > 0:
                avg_mark = np.nanmean(marks)  # Use nanmean to handle NaN values
                repeating_logins[login] = (len(marks), avg_mark)
        
        return repeating_logins

    def process_as_corrected_data(self, as_corrected_df):
        corrector_marks = {}

        # Iterate over each row in the DataFrame
        for index, row in as_corrected_df.iterrows():
            # Get the corrector login and the final mark from each row
            corrector = row.get('corrector', {})
            corrector_login = corrector.get('login')
            final_mark = row.get('final_mark', np.nan)

            # Collect the marks for each corrector
            if corrector_login:
                if corrector_login in corrector_marks:
                    corrector_marks[corrector_login].append(final_mark)
                else:
                    corrector_marks[corrector_login] = [final_mark]

        # Calculate the number of appearances and the average marks for each corrector
        corrector_stats = {}
        for corrector, marks in corrector_marks.items():
            if len(marks) > 0:
                avg_mark = np.nanmean(marks)  # Use nanmean to handle NaN values
                corrector_stats[corrector] = (len(marks), avg_mark)

        return corrector_stats


#TODO REmove: just for testing
    def load_json_data(self, filename: str) -> pd.DataFrame:
        """Load JSON data from a file and convert it to a DataFrame.

        Args:
            filename (str): The path to the JSON file.

        Returns:
            pd.DataFrame: The data loaded into a DataFrame.
        """
        with open(filename, 'r') as file:
            data = json.load(file)
        return pd.DataFrame(data)


    def run(self) -> str:
        """Run the evaluation network analysis.

        Returns:
            str: The result of the evaluation network analysis.
        """
        login = prompt("Login: ")

        with Spinner(f"Fetching all evaluations involving {login}") as spinner:
            try:
                user_id = Utils.get_user_id(self.api, login)
                as_corrected_df = self.load_json_data("./as_corrected.json")
                as_corrector_df = self.load_json_data("./as_corrector.json")

                corrector_counter = self.process_as_corrector_data(as_corrector_df)
                corrected_counter = self.process_as_corrected_data(as_corrected_df)

            except Exception as e:
                raise Exception(f"An error occurred: {e}")

        return self.show_formatted_result(corrected_counter, corrector_counter, login)
