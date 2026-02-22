#!/usr/bin/env python3
"""Test the queue mechanism independently of Streamlit"""

import queue
import threading
import time

# Simulating Streamlit session state
class FakeSessionState:
    def __init__(self):
        self.logs = []

# Thread-safe queue
log_queue = queue.Queue()
session_state = FakeSessionState()

def add_log(message: str):
    """Simulate add_log function"""
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {message}"
    log_queue.put(formatted_msg)
    print(f"✈️  Queued: {message} (queue_size={log_queue.qsize()})")

def flush_log_queue():
    """Simulate flush_log_queue function"""
    count = 0
    while not log_queue.empty():
        try:
            msg = log_queue.get_nowait()
            session_state.logs.append(msg)
            count += 1
        except queue.Empty:
            break
    if count > 0:
        print(f"✅ Flushed {count} messages. Total logs: {len(session_state.logs)}")

def background_worker():
    """Simulate background thread"""
    add_log("Background thread started")
    time.sleep(0.1)  # Small delay
    add_log("Processing file 1")
    time.sleep(0.1)
    add_log("Processing file 2")
    time.sleep(0.1)
    add_log("Background thread finished")

# Test
print("=" * 50)
print("Testing queue mechanism")
print("=" * 50)

# Main thread calls add_log
add_log("Main thread message 1")

# Start background thread
print("\n🔄 Starting background thread...")
thread = threading.Thread(target=background_worker, daemon=True)
thread.start()

# Give thread time to queue messages
time.sleep(0.5)

# Main thread flushes
print("\n🔄 Flushing queue...")
flush_log_queue()

# Display logs
print("\n📜 Final logs in session_state:")
for i, log in enumerate(session_state.logs, 1):
    print(f"  {i}. {log}")

print("\n" + "=" * 50)
print(f"✓ Success: {len(session_state.logs)} messages processed")
print("=" * 50)
