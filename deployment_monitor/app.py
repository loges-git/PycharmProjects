import streamlit as st
import threading
import time
import json
import os
import queue
from pathlib import Path

from core.folder_monitor import FolderMonitor
from core.msg_processor import MsgProcessor
from core.zip_processor import ZipProcessor
from core.validator import DeploymentValidator
from core.jira_extractor import JiraExtractor
from core.archiver import Archiver
from core.cycle_manager import CycleManager
from core.email_sender import EmailSender
from styles import load_css

# Import shared state from SEPARATE MODULE (persists across Streamlit reruns)
import shared_state


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

if "logs" not in st.session_state:
    st.session_state.logs = []
    # Sync with buffer in case service was already running (e.g. page refresh)
    st.session_state.logs = shared_state.get_all_logs()

if "last_status" not in st.session_state:
    st.session_state.last_status = None

if "last_sound_status" not in st.session_state:
    st.session_state.last_sound_status = None


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


poll_interval = st.number_input("Poll Interval (seconds)", 5, 300, 5)
st.markdown('</div>', unsafe_allow_html=True)


# ==========================================================
# BACKGROUND SERVICE FUNCTION
# ==========================================================

def run_service(incoming_path_str: str, base_path_str: str, interval: int, send_email: bool = False):
    """Background thread service for monitoring and processing deployments.
    
    NOTE: This runs in a background thread. It must NOT access st.session_state
    or any Streamlit API. All communication with the UI happens through shared_state.
    
    Args:
        incoming_path_str: Path to incoming folder
        base_path_str: Path to base audit folder
        interval: Poll interval in seconds
        send_email: Whether to send email notifications (captured from UI at start time)
    """
    log = shared_state.add_log  # Local alias for convenience
    stop = shared_state.stop_event  # Local alias
    
    try:
        log("🔍 Background service thread started...")
        
        incoming_path = Path(incoming_path_str)
        base_audit_path = Path(base_path_str)
        config_path = Path("config.json")

        if not config_path.exists():
            log("❌ config.json not found.")
            return

        if not incoming_path.exists():
            log(f"❌ Incoming path not found: {incoming_path}")
            return

        if not base_audit_path.exists():
            log(f"❌ Base audit path not found: {base_audit_path}")
            return

        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        cycle_manager = CycleManager(base_audit_path)
        cycle_name = cycle_manager.generate_cycle_name()
        cycle_manager.ensure_cycle_folder(cycle_name)

        archiver = Archiver(base_audit_path, cycle_name)
        monitor = FolderMonitor(incoming_path, poll_interval=interval)

        log("✅ Service Started (Polling Method).")

        for file in monitor.start_polling():
            if stop.is_set():
                log("🛑 Service Stopped.")
                break

            try:
                log(f"📄 Detected file: {file.name}")

                zip_files_to_process = []
                file_suffix = file.suffix.lower()

                if file_suffix == ".msg":
                    log("📨 Extracting ZIP from MSG...")
                    msg_processor = MsgProcessor(file, incoming_path)
                    extracted_zips = msg_processor.extract_zip_attachments()
                    zip_files_to_process.extend(extracted_zips)

                elif file_suffix == ".zip":
                    zip_files_to_process.append(file)

                for zip_path in zip_files_to_process:
                    log(f"📦 Processing ZIP: {zip_path.name}")

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

                    shared_state.set_status(status)  # Thread-safe status update
                    log(f"Status: {status}")
                    log(f"Details: {message}")
                    
                    # Display detailed error information
                    if result.get("error_details"):
                        log("━ Error Details ━")
                        for error in result["error_details"]:
                            log(f"  • Unit: {error['unit']} | Code: {error['code']}")
                            log(f"    Message: {error['message'][:100]}...")
                    
                    # Display invalid objects created
                    if result.get("invalid_objects"):
                        log("━ Invalid Objects Created ━")
                        for invalid in result["invalid_objects"]:
                            log(f"  • Object: {invalid['object']} (Type: {invalid['type']})")
                    
                    # Send email notification if enabled (flag captured at start time)
                    if send_email:
                        try:
                            email_sender = EmailSender(config)
                            success, email_msg = email_sender.send_deployment_summary(
                                status=status,
                                cluster=metadata["cluster"],
                                instance=metadata["instance"],
                                message=message
                            )
                            if success:
                                log(f"📧 {email_msg}")
                            else:
                                log(f"⚠️ Email Error: {email_msg}")
                        except Exception as e:
                            log(f"⚠️ Email Exception: {str(e)}")

                    zip_processor.cleanup()
                    log(f"✅ Finished processing: {zip_path.name}")

                monitor.mark_as_processed(file)

            except Exception as e:
                log(f"❌ Error: {str(e)}")
                import traceback
                log(f"Traceback: {traceback.format_exc()}")
                
    except Exception as e:
        shared_state.add_log(f"❌ CRITICAL: {str(e)}")
        import traceback
        shared_state.add_log(f"Traceback: {traceback.format_exc()}")


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
        if not st.session_state.service_running:
            st.session_state.service_running = True
            shared_state.stop_event.clear()  # Clear stop flag
            shared_state.add_log("🚀 Service started via UI button")
            # Capture email setting NOW (safe, on main thread) and pass to thread
            email_enabled = st.session_state.get("send_email_notification", False)
            if email_enabled:
                shared_state.add_log("☑ Email notifications enabled")
            thread = threading.Thread(
                target=run_service,
                args=(incoming_input, base_input, poll_interval, email_enabled),
                daemon=True,
                name="DeploymentServiceWorker"
            )
            thread.start()

with col6:
    if st.button("⏹ Stop Service"):
        if st.session_state.service_running:
            st.session_state.service_running = False
            shared_state.stop_event.set()  # Signal thread to stop
            shared_state.add_log("🛑 Stop signal sent.")


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
# LIVE LOG DISPLAY
# ==========================================================

st.subheader("📜 Live Logs")

# Flush logs from shared_state buffer → session_state (MAIN THREAD)
shared_state.drain_queue()
st.session_state.logs = shared_state.get_all_logs()

# Flush state updates (e.g., last_status)
for key, value in shared_state.drain_state_queue():
    st.session_state[key] = value

# Display logs (last 100)
log_text = "\n".join(st.session_state.logs[-100:])
st.text_area("Logs", log_text, height=300, label_visibility="collapsed")


# ==========================================================
# AUTO REFRESH
# ==========================================================

if st.session_state.service_running:
    if shared_state.has_pending_logs(len(st.session_state.logs)):
        # New messages available — refresh quickly to show them
        time.sleep(0.3)
    else:
        # No new messages — poll less aggressively
        time.sleep(2.0)
    st.rerun()
