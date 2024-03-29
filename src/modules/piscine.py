import datetime
from src.CLInterface import Interface
from src.modules.base import BaseModule
from src.utils import Utils


class Piscine(BaseModule):
    def run(self) -> None:
        modules = {
            "Accepted Pisciners": AcceptedPisciners(self.api),
        }

        interface = Interface("Analyze Piscine Data", modules, can_go_back=True)
        interface.loop()


class AcceptedPisciners(BaseModule):
    def run(self) -> str:
        print("Gets the Pisciners which got accepted to 42.")
        print(
            "Note: Only accepted Pisciners who already registered to the Kickoff are shown in this list."
        )

        # TODO: should this be an input too?
        year = datetime.date.today().year
        month = input("In which month did this Piscine start?")

        users = Utils.get_users(
            self.api,
            pool_year=year,
            pool_month=month,
            cursus_id=21,
            primary_campus_id=53,
        )

        data = [user["login"] for user in users]
        data = sorted(data)

        data.insert(0, "Accepted Pisciners registered to Kickoff:\n")
        data.append("\nTotal: " + str(len(users)))

        return "\n".join(data) + "\n"


def format_table(strings, num_columns) -> str:
    # Calculate the necessary rows
    num_rows = -(-len(strings) // num_columns)  # Ceiling division

    # Prepare a list of lists for easier column width calculation
    table = [strings[i : i + num_rows] for i in range(0, len(strings), num_rows)]

    # Calculate max width for each column
    col_widths = [max(len(item) for item in col) for col in table]

    result = ""

    # Print the table
    for row_idx in range(num_rows):
        for col_idx, col in enumerate(table):
            # Print item with padding, if the item exists in the current row
            if row_idx < len(col):
                print(f"{col[row_idx]:<{col_widths[col_idx]}}", end="    ")
        print()  # Newline after each row
