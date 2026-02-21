
import time
import queue
from pathlib import Path
from typing import Set, Generator
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class NewFileHandler(FileSystemEventHandler):
    """
    Watchdog handler to push new ZIP/MSG files to a queue.
    """
    def __init__(self, file_queue: queue.Queue, processed_files: Set[str]):
        self.file_queue = file_queue
        self.processed_files = processed_files

    def on_created(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)
        if path.suffix.lower() in [".zip", ".msg"]:
            # Check if already processed (though unlikely for new creation events, 
            # good for safety if recreated)
            if path.name not in self.processed_files:
                self.file_queue.put(path)

    def on_moved(self, event):
        if event.is_directory:
            return

        path = Path(event.dest_path)
        if path.suffix.lower() in [".zip", ".msg"]:
            if path.name not in self.processed_files:
                self.file_queue.put(path)


class FolderMonitor:
    """
    Real-time folder watcher for new ZIP or MSG files using watchdog.
    """

    def __init__(self, incoming_path: str | Path):
        self.incoming_path = Path(incoming_path)
        self.processed_files: Set[str] = set()
        self.file_queue = queue.Queue()
        self.observer = Observer()

        if not self.incoming_path.exists():
            raise FileNotFoundError(
                f"Incoming folder not found: {self.incoming_path}"
            )

    def mark_as_processed(self, file: Path):
        self.processed_files.add(file.name)

    def _scan_existing_files(self):
        """
        Initial scan to catch files already present before watcher starts.
        """
        for file in self.incoming_path.iterdir():
            if file.is_file() and file.suffix.lower() in [".zip", ".msg"]:
                if file.name not in self.processed_files:
                    self.file_queue.put(file)

    def start_polling(self) -> Generator[Path, None, None]:
        print("Real-time Folder Watcher Started...")
        print(f"Watching: {self.incoming_path}")
        print("-" * 50)

        # 1. Scan existing files first
        self._scan_existing_files()

        # 2. Setup Watchdog
        event_handler = NewFileHandler(self.file_queue, self.processed_files)
        self.observer.schedule(event_handler, str(self.incoming_path), recursive=False)
        self.observer.start()

        try:
            while True:
                # Block until a file is available in the queue
                # Use timeout to allow checking for stop signal if needed (though generator usually breaks)
                try:
                    file_path = self.file_queue.get(timeout=1)
                    yield file_path
                except queue.Empty:
                    # Yield nothing or confirm liveness? 
                    # Actually, if we yield, the loop in app.py continues. 
                    # If we block here, app.py blocks. 
                    # Since app.py is running in a thread, blocking is fine.
                    # But if we yield nothing, we need to handle it.
                    # The generator expects to yield Paths.
                    # So we just continue looping inside start_polling until we get a file.
                    continue
        except GeneratorExit:
            # Cleanup when generator is closed
            self.observer.stop()
            self.observer.join()
            print("Folder Watcher Stopped.")
        except Exception as e:
            print(f"Error in watcher: {e}")
            self.observer.stop()
            self.observer.join()
