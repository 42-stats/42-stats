import functools
import threading
import itertools
from typing import Optional

_spinners = {
    "dots": {
        "interval": 80,
        "frames": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
    }
}


class Spinner:
    """
    A class that represents a spinner animation.

    Attributes:
        CYAN_COLOR (str): The ANSI escape code for cyan color.
        RESET_COLOR (str): The ANSI escape code to reset the color.

    Methods:
        __init__(self, text: str, spinner: str = "dots", status_message: Optional[str] = None):
            Initializes a Spinner object.
        __enter__(self):
            Starts the spinner animation.
        __exit__(self, exc_type, exc_value, traceback):
            Stops the spinner animation.
        __call__(self, fn):
            Decorator that starts the spinner animation before calling the decorated function.
        start(self):
            Starts the spinner animation.
        stop(self):
            Stops the spinner animation.
        status_message(self, message: str):
            Sets the status message to be displayed alongside the spinner animation.

    """

    CYAN_COLOR = "\033[96m"
    RESET_COLOR = "\033[0m"

    _interval: int
    _cycle: list[str]

    _thread: Optional[threading.Thread] = None
    _stop_event: Optional[threading.Event] = None

    _status_message_count = 0
    _status_message: Optional[str] = None

    def __init__(
        self,
        text: str,
        spinner: str = "dots",
        status_message: Optional[str] = None,
    ):
        """
        Initializes a Spinner object.

        Args:
            text (str): The text to be displayed alongside the spinner animation.
            spinner (str, optional): The type of spinner animation to use. Defaults to "dots".
            status_message (str, optional): The initial status message to be displayed. Defaults to None.
        """
        self._text = text
        self._interval = _spinners[spinner]["interval"]
        self._cycle = itertools.cycle(_spinners[spinner]["frames"])
        self._status_message = status_message

    def __enter__(self):
        """
        Starts the spinner animation.

        Returns:
            Spinner: The Spinner object itself.
        """
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Stops the spinner animation.
        """
        self.stop()

    def __call__(self, fn):
        """
        Decorator that starts the spinner animation before calling the decorated function.

        Args:
            fn (function): The function to be decorated.

        Returns:
            function: The decorated function.
        """

        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            with self:
                return fn(*args, **kwargs)

        return wrapped

    def start(self):
        """
        Starts the spinner animation.
        """
        if self._thread is not None:
            return

        self._status_message_count = 0
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._spin)
        self._thread.daemon = True
        self._thread.start()

    def stop(self):
        """
        Stops the spinner animation.
        """
        if self._thread is None:
            return

        self._stop_event.set()
        self._thread.join()

        self._thread = None
        self._stop_event = None

        self._clear_line()

    def status_message(self, message: str):
        """
        Sets the status message to be displayed alongside the spinner animation.

        Args:
            message (str): The status message.
        """
        if self._status_message == message:
            self._status_message_count += 1
            return

        self._status_message_count = 1
        self._status_message = message

    def _spin(self):
        try:
            self._hide_cursor()

            while not self._stop_event.is_set():
                frame = next(self._cycle)

                print(
                    f"\r{self.CYAN_COLOR}{frame}{self.RESET_COLOR} {self._text}", end=""
                )

                if self._status_message:
                    print(f" {self._status_message}", end="")

                if self._status_message_count > 1:
                    print(f" ({self._status_message_count}x)", end="")

                self._stop_event.wait(self._interval / 1000)

        finally:
            self._show_cursor()

    def _hide_cursor(self):
        if self._hide_cursor:
            print("\033[?25l", end="")

    def _show_cursor(self):
        print("\033[?25h", end="")

    def _clear_line(self):
        print("\r\033[K", end="")
