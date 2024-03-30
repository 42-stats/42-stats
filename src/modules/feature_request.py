from src.InterfaceResult import InterfaceResult
from src.modules.base import BaseModule
from src.utils import clear_terminal


class FeatureRequest(BaseModule):

    def run(self) -> str:

        clear_terminal()
        print(
            "for feature requests, please open an issue: https://github.com/42-stats/42-stats/issues/"
        )

        return InterfaceResult.Success
