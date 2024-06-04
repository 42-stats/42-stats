from enum import Enum


class InterfaceResult(Enum):
    Exit = 0
    Skip = 1
    Success = 2
    GoBack = 3
