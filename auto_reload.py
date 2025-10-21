import os
import sys
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class RestartOnChangeHandler(FileSystemEventHandler):
    def __init__(self, command):
        self.command = command
        self.process = subprocess.Popen(self.command, shell=True)

    def on_any_event(self, event):
        if event.src_path.endswith(".py"):
            print(f"Change detected in {event.src_path}. Restarting...")
            self.process.kill()
            self.process = subprocess.Popen(self.command, shell=True)

if __name__ == "__main__":
    path = "."  # directory to watch
    command = "python app.py"  # your app start command
    os.environ["DATABASE_PATH"] = os.getcwd()
    event_handler = RestartOnChangeHandler(command)
    observer = Observer()
    observer.schedule(event_handler, path=path, recursive=True)
    observer.start()

    print(f"Watching for changes in {path}...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
