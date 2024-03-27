import threading
import time



class Animation:

    def __init__(self, message: str):
        self.message = message
        self.loading_animation()

    def start_animation(self, done_event: threading.Event):
        def animation():
            chars = ["|", "/", "-", "\\"]
            idx = 0
            while not done_event.is_set():
                print(f"\r{self.message} {chars[idx % len(chars)]}", end="")
                idx += 1
                time.sleep(0.1)

        loading_thread = threading.Thread(target=animation)
        loading_thread.start()
        self.loading_thread = loading_thread

    def loading_animation(self):
        self.done_event = threading.Event()
        self.start_animation(self.done_event)

    def stop_animation(self):
        self.done_event.set()
        self.loading_thread.join()

