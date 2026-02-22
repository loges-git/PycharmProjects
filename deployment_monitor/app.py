import streamlit as st
import threading
import time
import json
import os
import queue
from pathlib import Path
from datetime import datetime

from core.folder_monitor import FolderMonitor
from core.msg_processor import MsgProcessor
from core.zip_processor import ZipProcessor
from core.validator import DeploymentValidator
from core.jira_extractor import JiraExtractor
from core.archiver import Archiver
from core.cycle_manager import CycleManager
from core.email_sender import EmailSender
from styles import load_css

# Thread-safe queue for background thread logging
log_queue = queue.Queue()
state_queue = queue.Queue()  # For thread-safe session state updates
service_stop_event = threading.Event()  # Thread-safe stop signal

# Debug log file
DEBUG_LOG_FILE = Path("queue_debug.log")

def debug_log(message: str):
    """Write to file for debugging (non-blocking)"""
    try:
        with open(DEBUG_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] {message}\n")
    except:
        pass  # Silently fail if writing fails


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(page_title="Deployment Log Automation", layout="wide")

# 🎨 Apply Luxury Theme
load_css()

st.title("🚀 Deployment Log Verification Automation")


# ==========================================================
# SESSION STATE INITIALIZATION
# ==========================================================

if "service_running" not in st.session_state:
    st.session_state.service_running = False
    debug_log("🔧 Initialized: service_running = False")

if "logs" not in st.session_state:
    st.session_state.logs = []
    debug_log("🔧 Initialized: logs = []")

if "last_status" not in st.session_state:
    st.session_state.last_status = None
    debug_log("🔧 Initialized: last_status = None")

if "last_sound_status" not in st.session_state:
    st.session_state.last_sound_status = None
    debug_log("🔧 Initialized: last_sound_status = None")


# ==========================================================
# LOG FUNCTION (THREAD-SAFE)
# ==========================================================

def add_log(message: str):
    """Add log message to thread-safe queue"""
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {message}"
    log_queue.put(formatted_msg)
    debug_log(f"⬅️ QUEUE.PUT (depth={log_queue.qsize()}): {message}")


def flush_log_queue():
    """Process all messages from queue and add to session state (MAIN THREAD ONLY)"""
    count = 0
    while not log_queue.empty():
        try:
            msg = log_queue.get_nowait()
            st.session_state.logs.append(msg)
            debug_log(f"➡️ FLUSHED (count={count+1}): {msg[:50]}")
            count += 1
        except queue.Empty:
            break
    if count > 0:
        debug_log(f"✅ FLUSH COMPLETE: {count} messages processed")


def set_status(status: str):
    """Queue a status update from background thread (THREAD-SAFE)"""
    state_queue.put(("last_status", status))
    debug_log(f"📤 Queued status update: {status}")


def flush_state_queue():
    """Process all state updates from queue (MAIN THREAD ONLY)"""
    count = 0
    while not state_queue.empty():
        try:
            key, value = state_queue.get_nowait()
            st.session_state[key] = value
            debug_log(f"✅ State update: {key} = {value}")
            count += 1
        except queue.Empty:
            break
    if count > 0:
        debug_log(f"✅ STATE FLUSH: {count} updates applied")


# ==========================================================
# INPUT SECTION WITH OPEN FOLDER BUTTONS
# ==========================================================

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("### 📥 Configuration")

col1, col2 = st.columns([4, 1], gap="medium")

with col1:
    incoming_input = st.text_input(
        "Incoming Folder Path",
        r"C:\Users\loges\Desktop\deployment_monitor\incoming"
    )

with col2:
    st.write("")  # Align button with input
    if st.button("📂 Open Incoming", use_container_width=True):
        if Path(incoming_input).exists():
            os.startfile(incoming_input)
        else:
            st.error("Incoming path does not exist.")


col3, col4 = st.columns([4, 1], gap="medium")

with col3:
    base_input = st.text_input(
        "Base Audit Path",
        r"C:\deployment_audit_test"
    )

with col4:
    st.write("")  # Align button with input
    if st.button("📁 Open Base", use_container_width=True):
        if Path(base_input).exists():
            os.startfile(base_input)
        else:
            st.error("Base path does not exist.")


poll_interval = st.number_input("Poll Interval (seconds)", 5, 300, 30)
st.markdown('</div>', unsafe_allow_html=True)


# ==========================================================
# BACKGROUND SERVICE FUNCTION
# ==========================================================

def run_service(incoming_path_str: str, base_path_str: str, interval: int):
    """Background thread service for monitoring and processing deployments."""
    try:
        add_log("🔍 Background service thread started...")
        debug_log(f"THREAD: run_service() called with incoming={incoming_path_str}, base={base_path_str}, interval={interval}")
        
        incoming_path = Path(incoming_path_str)
        debug_log(f"THREAD: Created incoming_path object: {incoming_path}")
        
        base_audit_path = Path(base_path_str)
        debug_log(f"THREAD: Created base_audit_path object: {base_audit_path}")
        
        config_path = Path("config.json")
        debug_log(f"THREAD: Created config_path object: {config_path}")

        debug_log(f"THREAD: config_path.exists() = {config_path.exists()}")
        if not config_path.exists():
            add_log("❌ config.json not found.")
            debug_log("THREAD: Returning due to missing config.json")
            return

        debug_log(f"THREAD: incoming_path.exists() = {incoming_path.exists()}")
        if not incoming_path.exists():
            add_log(f"❌ Incoming path not found: {incoming_path}")
            debug_log(f"THREAD: Returning due to missing incoming path: {incoming_path}")
            return

        debug_log(f"THREAD: base_audit_path.exists() = {base_audit_path.exists()}")
        if not base_audit_path.exists():
            add_log(f"❌ Base audit path not found: {base_audit_path}")
            debug_log(f"THREAD: Returning due to missing base path: {base_audit_path}")
            return

        debug_log("THREAD: All paths validated, loading config...")
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        debug_log("THREAD: Config loaded successfully")

        debug_log("THREAD: Creating CycleManager...")
        cycle_manager = CycleManager(base_audit_path)
        debug_log("THREAD: Generating cycle name...")
        cycle_name = cycle_manager.generate_cycle_name()
        debug_log(f"THREAD: Cycle name generated: {cycle_name}")
        debug_log("THREAD: Ensuring cycle folder...")
        cycle_manager.ensure_cycle_folder(cycle_name)
        debug_log("THREAD: Cycle folder ensured")

        debug_log("THREAD: Creating Archiver...")
        archiver = Archiver(base_audit_path, cycle_name)
        debug_log("THREAD: Archiver created")
        
        debug_log(f"THREAD: Creating FolderMonitor for {incoming_path} with interval {interval}...")
        monitor = FolderMonitor(incoming_path, poll_interval=interval)
        debug_log("THREAD: FolderMonitor created")

        add_log("✅ Service Started (Polling Method).")
        debug_log("THREAD: Service setup complete, about to enter polling loop")

        for file in monitor.start_polling():
            debug_log(f"THREAD: Got file from polling: {file.name}")

            if service_stop_event.is_set():
                add_log("🛑 Service Stopped.")
                debug_log("THREAD: Stop event detected, breaking")
                break

            try:
                debug_log(f"THREAD: Processing file: {file.name}")
                add_log(f"Detected file: {file.name}")
                debug_log(f"THREAD: Added log for file detection")

                zip_files_to_process = []
                debug_log(f"THREAD: Created zip_files_to_process list")

                file_suffix = file.suffix.lower()
                debug_log(f"THREAD: file.suffix.lower() = {file_suffix}")

                if file_suffix == ".msg":
                    debug_log(f"THREAD: File is .msg, extracting ZIP...")
                    add_log("Extracting ZIP from MSG...")
                    msg_processor = MsgProcessor(file, incoming_path)
                    extracted_zips = msg_processor.extract_zip_attachments()
                    zip_files_to_process.extend(extracted_zips)
                    debug_log(f"THREAD: Extracted {len(extracted_zips)} ZIPs from MSG")

                elif file_suffix == ".zip":
                    debug_log(f"THREAD: File is .zip, adding to processing list")
                    zip_files_to_process.append(file)

                debug_log(f"THREAD: Will process {len(zip_files_to_process)} ZIP files")

                for zip_path in zip_files_to_process:
                    debug_log(f"THREAD: Processing ZIP: {zip_path.name}")

                    add_log(f"Processing ZIP: {zip_path.name}")

                    zip_processor = ZipProcessor(zip_path, config)
                    metadata = zip_processor.process()

                    validator = DeploymentValidator(metadata, config)
                    result = validator.validate_all()

                    status = result["status"]
                    message = result["message"]

                    jira_extractor = JiraExtractor(metadata["main_log_path"])
                    jira_units = jira_extractor.extract()

                    archiver.archive(
                        status=status,
                        cluster=metadata["cluster"],
                        instance=metadata["instance"],
                        original_zip_path=zip_path,
                        jira_units=jira_units
                    )

                    set_status(status)  # Thread-safe status update
                    add_log(f"Status: {status}")
                    add_log(f"Details: {message}")
                    
                    # Display detailed error information
                    if result.get("error_details"):
                        add_log("━ Error Details ━")
                        for error in result["error_details"]:
                            add_log(f"  • Unit: {error['unit']} | Code: {error['code']}")
                            add_log(f"    Message: {error['message'][:100]}...")
                    
                    # Display invalid objects created
                    if result.get("invalid_objects"):
                        add_log("━ Invalid Objects Created ━")
                        for invalid in result["invalid_objects"]:
                            add_log(f"  • Object: {invalid['object']} (Type: {invalid['type']})")
                    
                    # Send email notification if enabled
                    if st.session_state.get("send_email_notification", False):
                        try:
                            email_sender = EmailSender(config)
                            success, email_msg = email_sender.send_deployment_summary(
                                status=status,
                                cluster=metadata["cluster"],
                                instance=metadata["instance"],
                                message=message
                            )
                            
                            if success:
                                add_log(f"📧 {email_msg}")
                            else:
                                add_log(f"⚠️ Email Error: {email_msg}")
                        except Exception as e:
                            add_log(f"⚠️ Email Exception: {str(e)}")

                    zip_processor.cleanup()
                    debug_log(f"THREAD: ZIP processing complete for {zip_path.name}")

                debug_log(f"THREAD: Marking file as processed: {file.name}")
                monitor.mark_as_processed(file)
                debug_log(f"THREAD: File marked as processed")

            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                add_log(error_msg)
                debug_log(f"THREAD: EXCEPTION in file processing: {str(e)}")
                import traceback
                debug_log(f"THREAD: Traceback: {traceback.format_exc()}")
                
    except Exception as e:
        error_msg = f"❌ CRITICAL: {str(e)}"
        add_log(error_msg)
        debug_log(f"THREAD: CRITICAL EXCEPTION: {str(e)}")
        import traceback
        debug_log(f"THREAD: Traceback: {traceback.format_exc()}")


# ==========================================================
# CONTROL BUTTONS
# ==========================================================

col_email = st.columns(1)[0]
with col_email:
    st.session_state.send_email_notification = st.checkbox(
        "📧 Enable Auto Email Notification",
        value=st.session_state.get("send_email_notification", False)
    )

col5, col6 = st.columns(2)

with col5:
    if st.button("▶ Start Service"):
        debug_log(f"🖱️  START button clicked. service_running={st.session_state.service_running}")
        if not st.session_state.service_running:
            st.session_state.service_running = True
            service_stop_event.clear()  # Clear stop flag
            debug_log(f"🚦 Setting service_running=True, creating thread...")
            add_log("🚀 Service started via UI button")
            debug_log(f"📝 Added UI button log (queue size={log_queue.qsize()})")
            thread = threading.Thread(
                target=run_service,
                args=(incoming_input, base_input, poll_interval),
                daemon=True,
                name="DeploymentServiceWorker"
            )
            debug_log(f"🧵 Thread created: {thread.name}")
            thread.start()
            debug_log(f"🧵 Thread started (is_alive={thread.is_alive()})")

with col6:
    if st.button("⏹ Stop Service"):
        debug_log(f"🖱️  STOP button clicked. service_running={st.session_state.service_running}")
        if st.session_state.service_running:
            st.session_state.service_running = False
            service_stop_event.set()  # Signal thread to stop
            debug_log("🛑 Setting service_running=False and service_stop_event=set()")


# ==========================================================
# SERVICE STATUS INDICATOR
# ==========================================================

st.subheader("🟢 Service Status")

if st.session_state.service_running:
    st.success("Service is RUNNING")
else:
    st.warning("Service is STOPPED")


# ==========================================================
# DEPLOYMENT STATUS DISPLAY
# ==========================================================

st.subheader("📊 Latest Deployment Status")

if st.session_state.last_status == "PASS":
    st.success("Deployment PASSED ✅")
elif st.session_state.last_status == "FAIL":
    st.error("Deployment FAILED ❌")
else:
    st.info("No deployment processed yet.")


# ==========================================================
# SOUND ALERT (plays once per status change)
# ==========================================================

if (
    st.session_state.last_status in ["PASS", "FAIL"]
    and st.session_state.last_status != st.session_state.last_sound_status
):
    st.session_state.last_sound_status = st.session_state.last_status

    st.markdown(
        """
        <audio autoplay>
        <source src="https://www.soundjay.com/buttons/sounds/beep-07.mp3" type="audio/mpeg">
        </audio>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# LIVE LOG DISPLAY (with queue flushing)
# ==========================================================

debug_log(f"📺 Rendering logs section. Queue size: {log_queue.qsize()}, Logs count: {len(st.session_state.logs)}")

st.subheader("📜 Live Logs")

# Flush any messages from background thread queue
flush_log_queue()
flush_state_queue()  # Also flush any state updates

debug_log(f"📺 After flush: Queue size: {log_queue.qsize()}, Logs count: {len(st.session_state.logs)}")

# Display logs
log_text = "\n".join(st.session_state.logs[-100:])
debug_log(f"📺 Displaying {len(st.session_state.logs[-100:])} of {len(st.session_state.logs)} logs (last 100)")
st.text_area("Logs", log_text, height=300, label_visibility="collapsed")


# ==========================================================
# AUTO REFRESH
# ==========================================================

# Only rerun if service is running AND there are pending messages
if st.session_state.service_running and not log_queue.empty():
    debug_log(f"♻️  Service running with {log_queue.qsize()} pending messages, rerunning...")
    time.sleep(0.5)  # Small delay to batch log messages
    st.rerun()
elif st.session_state.service_running:
    # Service is running but no new messages - check less frequently
    debug_log(f"♻️  Service running but queue empty, light rerun after 2s...")
    time.sleep(2)
    st.rerun()
