
import time
import os
from pathlib import Path
from typing import Set, Generator, List

# Optional Watchdog Import for future use
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    import queue
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


class FolderMonitor:
    """
    Standard polling-based folder watcher.
    Preferred for VDI environments with limited filesystem event support.
    """

    def __init__(self, incoming_path: str | Path, poll_interval: int = 30):
        self.incoming_path = Path(incoming_path)
        self.poll_interval = poll_interval
        self.processed_files: Set[str] = set()

        if not self.incoming_path.exists():
            raise FileNotFoundError(
                f"Incoming folder not found: {self.incoming_path}"
            )

    def mark_as_processed(self, file: Path):
        self.processed_files.add(file.name)

    def scan_for_new_files(self) -> List[Path]:
        """
        Returns list of new ZIP or MSG files.
        """
        new_files = []
        try:
            for file in self.incoming_path.iterdir():
                if file.is_file() and file.suffix.lower() in [".zip", ".msg"]:
                    if file.name not in self.processed_files:
                        new_files.append(file)
        except Exception as e:
            print(f"Error scanning directory: {e}")
        
        return new_files

    def start_polling(self) -> Generator[Path, None, None]:
        print("Polling Folder Monitor Started...")
        print(f"Monitoring: {self.incoming_path} every {self.poll_interval}s")
        print("-" * 50)

        while True:
            new_files = self.scan_for_new_files()

            for file in new_files:
                yield file

            time.sleep(self.poll_interval)


# ==========================================================
# RETAINED WATCHDOG CODE (FOR FUTURE USE)
# ==========================================================

if WATCHDOG_AVAILABLE:
    class NewFileHandler(FileSystemEventHandler):
        def __init__(self, file_queue, processed_files):
            self.file_queue = file_queue
            self.processed_files = processed_files
            
        def on_created(self, event):
            if not event.is_directory:
                path = Path(event.src_path)
                if path.suffix.lower() in [".zip", ".msg"] and path.name not in self.processed_files:
                    self.file_queue.put(path)

        def on_moved(self, event):
            if not event.is_directory:
                path = Path(event.dest_path)
                if path.suffix.lower() in [".zip", ".msg"] and path.name not in self.processed_files:
                    self.file_queue.put(path)

    class RealTimeFolderMonitor:
        """
        Retained real-time watcher implementation.
        """
        def __init__(self, incoming_path: str | Path):
            self.incoming_path = Path(incoming_path)
            self.processed_files: Set[str] = set()
            self.file_queue = queue.Queue()
            self.observer = Observer()

        def start_polling(self) -> Generator[Path, None, None]:
            event_handler = NewFileHandler(self.file_queue, self.processed_files)
            self.observer.schedule(event_handler, str(self.incoming_path), recursive=False)
            self.observer.start()
            try:
                while True:
                    try:
                        file_path = self.file_queue.get(timeout=1)
                        yield file_path
                    except queue.Empty:
                        continue
            finally:
                self.observer.stop()
                self.observer.join()
