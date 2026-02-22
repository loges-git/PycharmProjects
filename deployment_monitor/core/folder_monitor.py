
import time
import os
import logging
import hashlib
from pathlib import Path
from typing import Set, Generator, List, Dict, Tuple

logger = logging.getLogger("deployment_monitor.folder_monitor")
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    import queue
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False


class FolderMonitor:
    """
    Standard polling-based folder watcher with deduplication.
    Preferred for VDI environments with limited filesystem event support.
    """

    def __init__(self, incoming_path: str | Path, poll_interval: int = 30):
        try:
            self.incoming_path = Path(incoming_path)
            self.poll_interval = poll_interval
            self.processed_files: Set[str] = set()
            self.file_fingerprints: Dict[str, Tuple[int, float]] = {}  # filename -> (size, mtime)

            logger.debug(f"Initializing FolderMonitor - path: {self.incoming_path}, interval: {poll_interval}s")

            if not self.incoming_path.exists():
                raise FileNotFoundError(
                    f"Incoming folder not found: {self.incoming_path}"
                )
            
            logger.info(f"FolderMonitor initialized successfully")
        
        except FileNotFoundError as e:
            logger.error(f"Initialization failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during FolderMonitor initialization: {e}")
            raise

    def _get_file_fingerprint(self, file_path: Path) -> Tuple[int, float]:
        """
        Generate fingerprint of file for deduplication.
        Uses file size and modification time (faster than hash).
        
        Args:
            file_path: Path to file
            
        Returns:
            Tuple of (file_size, modification_time)
        """
        try:
            stat = file_path.stat()
            return (stat.st_size, stat.st_mtime)
        except Exception as e:
            logger.warning(f"Could not fingerprint {file_path.name}: {e}")
            return (0, 0)
    
    def _is_duplicate(self, file_path: Path) -> bool:
        """
        Check if file is a duplicate (same name and fingerprint) or has been modified.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if duplicate or unchanged, False if new version
        """
        if file_path.name not in self.file_fingerprints:
            return False
        
        current_fp = self._get_file_fingerprint(file_path)
        previous_fp = self.file_fingerprints[file_path.name]
        
        return current_fp == previous_fp

    def mark_as_processed(self, file: Path):
        """Mark file as processed and store its fingerprint."""
        try:
            self.processed_files.add(file.name)
            self.file_fingerprints[file.name] = self._get_file_fingerprint(file)
            logger.debug(f"Marked as processed with fingerprint: {file.name}")
        except Exception as e:
            logger.error(f"Error marking file as processed: {e}")

    def scan_for_new_files(self) -> List[Path]:
        """
        Returns list of new ZIP or MSG files, excluding duplicates.
        Deduplication uses file size and modification time.
        
        Returns:
            List of Path objects for new or modified files
        """
        new_files = []
        try:
            for file in self.incoming_path.iterdir():
                if file.is_file() and file.suffix.lower() in [".zip", ".msg"]:
                    # Skip if already processed AND has not changed (duplicate)
                    if file.name in self.processed_files and self._is_duplicate(file):
                        logger.debug(f"Skipping duplicate: {file.name}")
                        continue
                    
                    # New file or modified file
                    if file.name not in self.processed_files:
                        new_files.append(file)
                        logger.debug(f"Found new file: {file.name}")
                    else:
                        # File was processed but has been modified
                        new_files.append(file)
                        logger.debug(f"Found modified file: {file.name}")
            
            if new_files:
                logger.info(f"Scan found {len(new_files)} new/modified files")
        
        except FileNotFoundError as e:
            logger.error(f"Directory not found during scan: {e}")
        except PermissionError as e:
            logger.error(f"Permission denied scanning directory: {e}")
        except Exception as e:
            logger.error(f"Error scanning directory: {e}", exc_info=True)
        
        return new_files

    def start_polling(self) -> Generator[Path, None, None]:
        """
        Start polling for new files.
        
        Yields:
            Path objects for new files as they are detected
        """
        logger.info("Polling Folder Monitor Started...")
        logger.info(f"Monitoring: {self.incoming_path} every {self.poll_interval}s")

        while True:
            try:
                new_files = self.scan_for_new_files()

                for file in new_files:
                    logger.debug(f"Yielding file for processing: {file.name}")
                    yield file

                time.sleep(self.poll_interval)
            
            except Exception as e:
                logger.error(f"Error during polling loop: {e}", exc_info=True)
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
            logger.info("Real-time Folder Monitor Started (Watchdog)...")
            logger.info(f"Monitoring: {self.incoming_path}")
            
            event_handler = NewFileHandler(self.file_queue, self.processed_files)
            self.observer.schedule(event_handler, str(self.incoming_path), recursive=False)
            self.observer.start()
            logger.debug("Watchdog observer started")
            
            try:
                while True:
                    try:
                        file_path = self.file_queue.get(timeout=1)
                        logger.debug(f"File event detected: {file_path.name}")
                        yield file_path
                    except queue.Empty:
                        continue
            except Exception as e:
                logger.error(f"Error in real-time monitoring loop: {e}", exc_info=True)
            finally:
                logger.info("Stopping Watchdog observer...")
                self.observer.stop()
                self.observer.join()
                logger.debug("Watchdog observer stopped")
