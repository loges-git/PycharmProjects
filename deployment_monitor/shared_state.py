"""
Shared State Module for Deployment Monitor
-------------------------------------------
This module holds thread-safe shared state (queues, buffers, events)
that must persist across Streamlit script reruns.

WHY A SEPARATE MODULE?
Streamlit re-executes the main app script via exec() on every rerun/interaction.
This means any module-level variables or class definitions in app.py are
re-created from scratch each time. However, Python's import system caches
modules in sys.modules — so this module's code runs ONLY ONCE during the
first import. All subsequent `import shared_state` calls return the cached
module object with the same variables, even across Streamlit reruns.

This guarantees that the background thread and the UI main thread always
reference the exact same queue/buffer/event objects.
"""

import queue
import threading
import time
from collections import deque


# ==========================================================
# These module-level variables are created ONCE and persist
# across all Streamlit reruns because this module is cached
# in sys.modules after the first import.
# ==========================================================

# Thread-safe queue for log messages (background → main thread)
log_queue = queue.Queue()

# Thread-safe queue for session state updates (background → main thread)
state_queue = queue.Queue()

# In-memory circular buffer — the authoritative log store
# The main thread copies this into st.session_state on each rerun
log_buffer = deque(maxlen=500)

# Lock for thread-safe access to log_buffer
buffer_lock = threading.Lock()

# Event to signal background thread to stop
stop_event = threading.Event()


# ==========================================================
# Thread-safe helper functions
# ==========================================================

def add_log(message: str):
    """Add a log message. Safe to call from ANY thread."""
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {message}"
    log_queue.put(formatted_msg)
    with buffer_lock:
        log_buffer.append(formatted_msg)


def set_status(status: str):
    """Queue a status update. Safe to call from ANY thread."""
    state_queue.put(("last_status", status))


def get_all_logs() -> list:
    """Get a snapshot of all logs from the buffer. Thread-safe."""
    with buffer_lock:
        return list(log_buffer)


def drain_queue():
    """Drain the log queue (prevents unbounded growth). Call from main thread."""
    while not log_queue.empty():
        try:
            log_queue.get_nowait()
        except queue.Empty:
            break


def drain_state_queue() -> list:
    """Drain state queue and return all updates. Call from main thread."""
    updates = []
    while not state_queue.empty():
        try:
            updates.append(state_queue.get_nowait())
        except queue.Empty:
            break
    return updates


def has_pending_logs(session_log_count: int) -> bool:
    """Check if there are logs in the buffer that aren't in session yet."""
    with buffer_lock:
        return len(log_buffer) > session_log_count
