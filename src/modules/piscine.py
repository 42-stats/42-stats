from datetime import datetime
from prompt_toolkit import prompt
from src.CLInterface import Interface
from src.InterfaceResult import InterfaceResult
from src.Spinner import Spinner
from src.modules.base import BaseModule
from src.utils import (
    Utils,
    clear_last_line,
    clear_terminal,
    get_campus_name,
    prompt_campus,
    prompt_select,
)


class Piscine(BaseModule):
    def run(self) -> InterfaceResult:
        modules = {
            "Accepted Pisciners": AcceptedPisciners(self.api),
            "Pisciners not correctly subscribed to the Exam": ExamImpostors(self.api),
            "Projects Status": ProjectsStatus(self.api),
        }

        interface = Interface("Analyze Piscine Data", modules, can_go_back=True)
        interface.loop()

        return InterfaceResult.Skip


class AcceptedPisciners(BaseModule):
    def run(self):
        title = (
            "Gets the Pisciners which got accepted to 42.\n"
            "Note: Only accepted Pisciners who already registered to the Kickoff are shown in this list.\n"
            "\n"
            "Select your campus: "
        )

        campus = prompt_campus(title + "\n")
        print(title + get_campus_name(campus))

        year = prompt("Year of the Piscine: ", default=str(datetime.now().year))
        month = month_prompt("Month of the Piscine")
        print("Month of the Piscine: " + month.capitalize())

        users = Utils.get_users(
            self.api,
            pool_year=year,
            pool_month=month,
            cursus_id=21,
            primary_campus_id=campus,
        )

        print("\nPisciners registered to Kickoff:\n")

        if len(users) > 0:
            print(format_table_as_string(sorted([user["login"] for user in users]), 6))

        print(f"\nTotal: {len(users)}\n")


class ExamImpostors(BaseModule):
    def run(self):
        title = (
            "Gets the current project status summary of Pisciners.\n"
            "\n"
            "Select your campus: "
        )

        campus = prompt_campus(title + "\n")
        print(title + get_campus_name(campus))

        # year = prompt("Year of the Piscine: ", default=str(datetime.now().year))
        # month = month_prompt("Month of the Piscine")
        # print("Month of the Piscine: " + month.capitalize())
        year = datetime.now().year

        month = [
            "january",
            "february",
            "march",
            "april",
            "may",
            "june",
            "july",
            "august",
            "september",
            "october",
            "november",
            "december",
        ][datetime.now().month - 1]

        with Spinner("Fetching Exams"):
            exams = Utils.get_exams(
                self.api, campus_id=campus, future=True, visible=True
            )

            if not len(exams):
                clear_terminal()
                print("No Exam found")
                return InterfaceResult.Success

        exams = [exam for exam in exams if "Piscine" in exam["name"]]

        if len(exams) > 1:
            exams_list = [exam["name"] for exam in exams]
            selection = prompt_select(exams_list)
            if not selection:
                return InterfaceResult.Success

            exam = exams[exams_list.index(selection)]
        else:
            exam = exams[0]

        with Spinner("Fetching Project Users"):
            project_users = Utils.get_users(
                self.api,
                project_id=exam["projects"][0]["id"],
                primary_campus_id=campus,
                pool_year=year,
                pool_month=month,
            )

        # clear_terminal()

        print(f'Information for {exam["name"]}')
        print("")
        print(f'Registered to Event: {exam["nbr_subscribers"]}')
        print(f"Registered to Project: {len(project_users)}")
        print(f'Difference: {abs(exam["nbr_subscribers"] - len(project_users))}')


class ProjectsStatus(BaseModule):
    def run(self):
        title = (
            "Gets the current project status summary of Pisciners.\n"
            "\n"
            "Select your campus: "
        )

        campus = prompt_campus(title + "\n")
        print(title + get_campus_name(campus))

        year = prompt("Year of the Piscine: ", default=str(datetime.now().year))
        month = month_prompt("Month of the Piscine")
        print("Month of the Piscine: " + month.capitalize())

        with Spinner("Fetching Pisciners"):
            users = Utils.get_users(
                self.api,
                pool_year=year,
                pool_month=month,
                cursus_id=9,
                primary_campus_id=campus,
            )

        if not len(users):
            clear_terminal()
            print(f"The {month} Piscine in {year} does not have any pisciners.")
            return

        with Spinner("Fetching Projects"):
            projects = Utils.get_projects_users(
                self.api, user_id=[user["id"] for user in users]
            )

            # Maybe there is a way to only get the Piscine projects in a nice way for now filtering it is.
            projects = [project for project in projects if 9 in project["cursus_ids"]]

        clear_terminal()

        if not len(projects):
            print(f"No projects could be found for the {month} Piscine in {year}.")
            return

        last_selection_index = 0
        while True:
            clear_terminal()

            self.print_overview(users, projects)

            menu = sorted(set([project["project"]["name"] for project in projects]))
            menu.append("Go Back")
            menu.append("Quit")

            # Note to myself: cursor is not spelled curser
            selection = prompt_select(menu, cursor_index=last_selection_index)
            if selection == "Quit" or selection is None:
                return InterfaceResult.Exit

            if selection == "Go Back":
                return InterfaceResult.Skip

            last_selection_index = menu.index(selection)
            result = self.print_project_overview(users, selection, projects)

            if result == InterfaceResult.Exit:
                return InterfaceResult.Exit

    def print_overview(self, users, projects):
        print(f"There are a total of {len(users)} Pisciners.\n")

        project_statuses = {}
        project_marks = {}
        for project in projects:
            project_name = project["project"]["name"]
            status = project["status"]

            if project_name not in project_statuses:
                project_statuses[project_name] = {}

            if status not in project_statuses[project_name]:
                project_statuses[project_name][status] = 0

            if project_name not in project_marks:
                project_marks[project_name] = []

            project_statuses[project_name][status] += 1

            if project["final_mark"] is not None:
                project_marks[project_name].append(project["final_mark"])

        for project in sorted(project_statuses):
            total_project_users = sum(project_statuses[project].values())
            print(
                f"{project} ({total_project_users} Pisciners - {total_project_users / len(users) * 100:.2f}%):"
            )

            average_mark = 0
            if len(project_marks[project]):
                average_mark = sum(project_marks[project]) / len(project_marks[project])

            print(f"  Average Grade: {average_mark:.2f}")

            for status in sorted(project_statuses[project]):
                if status == "searching_a_group":
                    pretty_status = "Searching For A Group"
                elif status == "in_progress":
                    pretty_status = "In Progress"
                elif status == "waiting_for_correction":
                    pretty_status = "Waiting For Evaluation"
                elif status == "finished":
                    pretty_status = "Finished"
                else:
                    pretty_status = status

                count = project_statuses[project][status]
                print(
                    f"    {pretty_status}: {count} ({count / total_project_users * 100:.2f}%)",
                )

            print("")

    def print_project_overview(self, users, project_name, projects):
        clear_terminal()

        projects = [
            project
            for project in projects
            if project["project"]["name"] == project_name
        ]

        print(f"Overview of {project_name}")

        total_project_users = len(projects)
        statuses = {}
        marks = []
        average_mark = 0
        total_tries = 0
        for project in projects:
            total_tries += len(project["teams"])

            if len(project["teams"]) and project["teams"][-1]["final_mark"] is None:
                total_tries -= 1

            status = project["status"]
            if status not in statuses:
                statuses[status] = 0
            statuses[status] += 1

            if project["final_mark"] is None:
                continue

            marks.append(project["final_mark"])

        if len(marks):
            average_mark = sum(marks) / len(marks)

        print(
            f"Pisciners: {total_project_users} (out of {len(users)} - {total_project_users / len(users) * 100:.2f}%)"
        )
        print(f"Tries: {total_tries}")
        print(f"Average Grade: {average_mark:.2f}")

        for status in sorted(statuses):
            if status == "searching_a_group":
                pretty_status = "Searching For A Group"
            elif status == "in_progress":
                pretty_status = "In Progress"
            elif status == "waiting_for_correction":
                pretty_status = "Waiting For Evaluation"
            elif status == "finished":
                pretty_status = "Finished"
            else:
                pretty_status = status

            count = statuses[status]
            print(
                f"{pretty_status}: {count} ({count / total_project_users * 100:.2f}%)",
            )

        print("\n")

        for project in sorted(projects, key=lambda project: project["user"]["login"]):
            print(
                f'{project["user"]["login"]} {len(project["teams"]) - 1 if len(project["teams"]) else 0} {"try" if len(project["teams"]) == 2 else "tries"} Final Mark {project["final_mark"] if project["final_mark"] is not None else "None"}:'
            )
            if project["teams"]:
                for team in project["teams"]:

                    status = project["status"]
                    if status == "searching_a_group":
                        pretty_status = "Searching For A Group"
                    elif status == "in_progress":
                        pretty_status = "In Progress"
                    elif status == "waiting_for_correction":
                        pretty_status = "Waiting For Evaluation"
                    elif status == "finished":
                        pretty_status = "Finished"
                    else:
                        pretty_status = status

                    print(
                        f'    {team["name"]}: {team["final_mark"] if team["final_mark"] is not None else pretty_status}'
                    )

            if project["status"] == "searching_a_group":
                print("Searching A Group")

            print("")

        selection = prompt_select(["Go Back", "Quit"])
        if selection == "Quit" or selection is None:
            return InterfaceResult.Exit

        if selection == "Go Back":
            return InterfaceResult.GoBack


def month_prompt(title="Select a month") -> str:
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    month = prompt_select(
        months,
        title=title,
        cursor_index=datetime.now().month - 1,
    )

    return month.lower()


def format_table_as_string(strings, num_columns):
    # Calculate the necessary rows
    num_rows = -(-len(strings) // num_columns)  # Ceiling division

    # Prepare a list of lists for easier column width calculation
    table = [strings[i : i + num_rows] for i in range(0, len(strings), num_rows)]

    # Calculate max width for each column
    col_widths = [max(len(item) for item in col) for col in table]

    # Accumulate the table into a string
    table_str = ""
    for row_idx in range(num_rows):
        for col_idx, col in enumerate(table):
            # Append item with padding, if the item exists in the current row
            if row_idx < len(col):
                table_str += f"{col[row_idx]:<{col_widths[col_idx]}}    "
        table_str += "\n"  # Newline after each row

    return table_str.strip()  # Remove trailing newline
