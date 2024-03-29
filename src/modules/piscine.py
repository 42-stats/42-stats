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
        print()

        year = input("Year of the Piscine: ")
        month = input("Month of the Piscine: ")

        users = Utils.get_users(
            self.api,
            pool_year=year,
            pool_month=month,
            cursus_id=21,
            primary_campus_id=53,
        )

        result = [
            "Pisciners registered to Kickoff:\n",
        ]

        if len(users) > 0:
            result.append(
                format_table_as_string(sorted([user["login"] for user in users]), 6)
            )

        result.append(f"\nTotal: {len(users)}\n")

        return "\n".join(result)


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
