from src.modules.base import BaseModule


class FeatureRequest(BaseModule):

    def run(self) -> str:
        return "for feature requests, please open an issue: https://github.com/42-stats/42-stats/issues/"
