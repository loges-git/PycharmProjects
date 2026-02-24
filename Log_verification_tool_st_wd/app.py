import streamlit as st
import threading
import time
import json
import os
import subprocess
from pathlib import Path

from core.folder_monitor import FolderMonitor
from core.msg_processor import MsgProcessor
from core.zip_processor import ZipProcessor
from core.validator import DeploymentValidator
from core.jira_extractor import JiraExtractor
from core.archiver import Archiver
from core.cycle_manager import CycleManager
from styles import load_css


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

if "last_status" not in st.session_state:
    st.session_state.last_status = None

if "last_sound_status" not in st.session_state:
    st.session_state.last_sound_status = None


# ==========================================================
# LOG FUNCTION
# ==========================================================

def add_log(message: str):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.logs.append(f"[{timestamp}] {message}")


# ==========================================================
# INPUT SECTION WITH OPEN FOLDER BUTTONS
# ==========================================================

st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.markdown("### 📥 Configuration")

col1, col2 = st.columns([4, 1])

with col1:
    incoming_input = st.text_input(
        "Incoming Folder Path",
        r"C:\Users\loges\Desktop\deployment_monitor\incoming"
    )

with col2:
    st.write("") # Spacer for alignment
    st.write("")
    if st.button("📂 Open Incoming", use_container_width=True):
        if Path(incoming_input).exists():
            try:
                # Use subprocess with explorer for proper window display
                subprocess.Popen(['explorer', '/select,', incoming_input])
            except Exception as e:
                st.error(f"Could not open folder: {e}")
        else:
            st.error("Incoming path does not exist.")


col3, col4 = st.columns([4, 1])

with col3:
    base_input = st.text_input(
        "Base Audit Path",
        r"C:\deployment_audit_test"
    )

with col4:
    st.write("") # Spacer
    st.write("")
    if st.button("📁 Open Base", use_container_width=True):
        if Path(base_input).exists():
            try:
                # Use subprocess with explorer for proper window display
                subprocess.Popen(['explorer', '/select,', base_input])
            except Exception as e:
                st.error(f"Could not open folder: {e}")
        else:
            st.error("Base path does not exist.")


st.markdown('</div>', unsafe_allow_html=True)


# ==========================================================
# BACKGROUND SERVICE FUNCTION
# ==========================================================

def run_service(incoming_path_str: str, base_path_str: str):

    incoming_path = Path(incoming_path_str)
    base_audit_path = Path(base_path_str)

    config_path = Path("config.json")

    if not config_path.exists():
        add_log("❌ config.json not found.")
        return

    if not incoming_path.exists():
        add_log("❌ Incoming path not found.")
        return

    if not base_audit_path.exists():
        add_log("❌ Base audit path not found.")
        return

    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    cycle_manager = CycleManager(base_audit_path)
    cycle_name = cycle_manager.generate_cycle_name()
    cycle_manager.ensure_cycle_folder(cycle_name)

    archiver = Archiver(base_audit_path, cycle_name)
    monitor = FolderMonitor(incoming_path)

    add_log("✅ Service Started (Real-Time).")

    for file in monitor.start_polling():

        if not st.session_state.service_running:
            add_log("🛑 Service Stopped.")
            break

        try:
            add_log(f"Detected file: {file.name}")

            zip_files_to_process = []

            if file.suffix.lower() == ".msg":
                add_log("Extracting ZIP from MSG...")
                msg_processor = MsgProcessor(file, incoming_path)
                extracted_zips = msg_processor.extract_zip_attachments()
                zip_files_to_process.extend(extracted_zips)

            elif file.suffix.lower() == ".zip":
                zip_files_to_process.append(file)

            for zip_path in zip_files_to_process:

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

                st.session_state.last_status = status
                add_log(f"Status: {status}")
                add_log(f"Details: {message}")

                zip_processor.cleanup()

            monitor.mark_as_processed(file)

        except Exception as e:
            add_log(f"❌ Error: {str(e)}")


# ==========================================================
# CONTROL BUTTONS
# ==========================================================

col5, col6 = st.columns(2)

with col5:
    if st.button("▶ Start Service") and not st.session_state.service_running:
        st.session_state.service_running = True
        thread = threading.Thread(
            target=run_service,
            args=(incoming_input, base_input),
            daemon=True
        )
        thread.start()

with col6:
    if st.button("⏹ Stop Service") and st.session_state.service_running:
        st.session_state.service_running = False


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
st.text_area("", "\n".join(st.session_state.logs[-100:]), height=300)


# ==========================================================
# AUTO REFRESH
# ==========================================================

if st.session_state.service_running:
    time.sleep(5)
    st.rerun()
