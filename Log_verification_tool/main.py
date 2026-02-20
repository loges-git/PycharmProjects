import json
from pathlib import Path
from core.cycle_manager import CycleManager
from core.zip_processor import ZipProcessor
from core.validator import DeploymentValidator
from core.jira_extractor import JiraExtractor
from core.archiver import Archiver


def load_config(config_path: Path) -> dict:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    print("=== Deployment Validation Engine (Phase 1) ===\n")

    # ---------------------------------------------------------
    # Load Configuration
    # ---------------------------------------------------------
    config_path = Path("config.json")
    config = load_config(config_path)

    base_audit_path = Path(config["base_audit_path"])

    # ---------------------------------------------------------
    # Generate Deployment Cycle
    # ---------------------------------------------------------
    cycle_manager = CycleManager(base_audit_path)
    cycle_name = cycle_manager.generate_cycle_name()
    cycle_folder = cycle_manager.ensure_cycle_folder(cycle_name)

    print(f"Deployment Cycle: {cycle_name}")
    print(f"Cycle Folder: {cycle_folder}\n")

    # ---------------------------------------------------------
    # Locate Test ZIPs
    # ---------------------------------------------------------
    test_zip_folder = Path("test_zips")

    if not test_zip_folder.exists():
        raise FileNotFoundError("test_zips folder not found.")

    zip_files = list(test_zip_folder.glob("*.zip"))

    if not zip_files:
        print("No ZIP files found in test_zips folder.")
        return

    # ---------------------------------------------------------
    # Initialize Archiver
    # ---------------------------------------------------------
    archiver = Archiver(base_audit_path, cycle_name)

    # ---------------------------------------------------------
    # Process Each ZIP
    # ---------------------------------------------------------
    for zip_path in zip_files:
        print(f"Processing ZIP: {zip_path.name}")

        zip_processor = ZipProcessor(zip_path, config)

        try:
            metadata = zip_processor.process()

            instance = metadata["instance"]
            cluster = metadata["cluster"]

            print(f"  Instance: {instance}")
            print(f"  Cluster: {cluster}")

            # -------------------------------------------------
            # Validate Deployment
            # -------------------------------------------------
            validator = DeploymentValidator(metadata, config)
            validation_result = validator.validate_all()

            status = validation_result["status"]
            message = validation_result["message"]

            print(f"  Validation Status: {status}")
            print(f"  Message: {message}")

            # -------------------------------------------------
            # Extract JIRA Mapping
            # -------------------------------------------------
            jira_extractor = JiraExtractor(metadata["main_log_path"])
            jira_units = jira_extractor.extract()

            # -------------------------------------------------
            # Archive Results
            # -------------------------------------------------
            final_folder = archiver.archive(
                status=status,
                cluster=cluster,
                instance=instance,
                original_zip_path=zip_path,
                jira_units=jira_units
            )

            print(f"  Archived To: {final_folder}")

        except Exception as e:
            print(f"  ERROR: {e}")

        finally:
            zip_processor.cleanup()

        print("-" * 60)

    print("\n=== Phase 1 Execution Complete ===")


if __name__ == "__main__":
    main()
