import shutil
from pathlib import Path
import json

from core.folder_monitor import FolderMonitor
from core.msg_processor import MsgProcessor
from core.zip_processor import ZipProcessor
from core.validator import DeploymentValidator
from core.jira_extractor import JiraExtractor
from core.archiver import Archiver
from core.notifier import Notifier
from core.cycle_manager import CycleManager


# ==========================================================
# CONFIGURATION
# ==========================================================

INCOMING_PATH = Path(r"C:\Users\loges\Desktop\deployment_monitor\incoming")
PROCESSED_MSG_FOLDER = INCOMING_PATH / "processed_msg"

CONFIG_PATH = Path("config.json")


# ==========================================================
# LOAD CONFIG
# ==========================================================

def load_config():
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# ==========================================================
# MAIN SERVICE
# ==========================================================

def main():

    print("=== Deployment Automation Service Started ===")

    config = load_config()
    base_audit_path = Path(config["base_audit_path"])

    # Read poll interval from config (default 30 seconds)
    poll_interval = config.get("poll_interval_seconds", 30)

    print(f"Polling interval set to: {poll_interval} seconds")

    # Ensure processed_msg folder exists
    PROCESSED_MSG_FOLDER.mkdir(parents=True, exist_ok=True)

    # Generate deployment cycle
    cycle_manager = CycleManager(base_audit_path)
    cycle_name = cycle_manager.generate_cycle_name()
    cycle_manager.ensure_cycle_folder(cycle_name)

    archiver = Archiver(base_audit_path, cycle_name)
    notifier = Notifier()

    monitor = FolderMonitor(INCOMING_PATH, poll_interval=poll_interval)

    for file in monitor.start_polling():

        print(f"\nDetected file: {file.name}")

        try:
            zip_files_to_process = []

            # --------------------------------------------------
            # If MSG file → extract ZIP
            # --------------------------------------------------
            if file.suffix.lower() == ".msg":
                print("Extracting ZIP from MSG...")
                msg_processor = MsgProcessor(file, INCOMING_PATH)
                extracted_zips = msg_processor.extract_zip_attachments()

                if not extracted_zips:
                    print("No ZIP attachment found inside MSG.")
                else:
                    zip_files_to_process.extend(extracted_zips)

                # Move MSG to processed folder
                shutil.move(str(file), PROCESSED_MSG_FOLDER / file.name)

            # --------------------------------------------------
            # If ZIP file → process directly
            # --------------------------------------------------
            elif file.suffix.lower() == ".zip":
                zip_files_to_process.append(file)

            # --------------------------------------------------
            # Process ZIP files
            # --------------------------------------------------
            for zip_path in zip_files_to_process:

                print(f"Processing ZIP: {zip_path.name}")

                zip_processor = ZipProcessor(zip_path, config)
                metadata = zip_processor.process()

                validator = DeploymentValidator(metadata, config)
                validation_result = validator.validate_all()

                status = validation_result["status"]
                message = validation_result["message"]

                jira_extractor = JiraExtractor(metadata["main_log_path"])
                jira_units = jira_extractor.extract()

                final_folder = archiver.archive(
                    status=status,
                    cluster=metadata["cluster"],
                    instance=metadata["instance"],
                    original_zip_path=zip_path,
                    jira_units=jira_units
                )

                print(f"Validation Status: {status}")
                print(f"Archived To: {final_folder}")

                notifier.notify(
                    f"Cluster: {metadata['cluster'].upper()}\n"
                    f"Instance: {metadata['instance']}\n"
                    f"Status: {status}\n\n"
                    f"{message}\n\n"
                    f"Please review and release flag if PASS."
                )

                zip_processor.cleanup()

            monitor.mark_as_processed(file)

        except Exception as e:
            print(f"ERROR while processing {file.name}: {e}")

    print("Service stopped.")


if __name__ == "__main__":
    main()
