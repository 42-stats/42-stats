import threading
import time


def start_animation(done_event: threading.Event, message: str):
    def animation():
        chars = ["|", "/", "-", "\\"]
        idx = 0
        while not done_event.is_set():
            print(f"\r{message} {chars[idx % len(chars)]}", end="")
            idx += 1
            time.sleep(0.1)

    loading_thread = threading.Thread(target=animation)
    loading_thread.start()
    return loading_thread
