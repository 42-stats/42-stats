import logging

from src.InterfaceResult import InterfaceResult


class BaseModule:
    def __init__(self, api):
        self.api = api
        self.logs = logging.getLogger("logs")

    def run(self) -> InterfaceResult.Success:
        raise NotImplementedError
