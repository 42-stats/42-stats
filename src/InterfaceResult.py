from enum import Enum


from enum import Enum


class InterfaceResult(Enum):
    """
    Enum representing the possible results of an interface operation.

    Attributes:
        Exit (int): Represents the result when the interface should exit.
        Skip (int): Represents the result when the interface should skip to the next operation.
        Success (int): Represents the result when the interface operation is successful.
    """

    Exit = 0
    Skip = 1
    Success = 2
    GoBack = 3
