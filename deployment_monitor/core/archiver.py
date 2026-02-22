import shutil
import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger("deployment_monitor.archiver")


class Archiver:
    """
    Responsible for saving:
    - Original ZIP file
    - compiled_units.txt
    Into proper deployment cycle structure.
    """

    def __init__(
        self,
        base_audit_path: str | Path,
        cycle_name: str,
    ):
        try:
            self.base_audit_path = Path(base_audit_path)
            self.cycle_name = cycle_name
            
            logger.debug(f"Initializing Archiver - base: {self.base_audit_path}, cycle: {cycle_name}")

            if not self.base_audit_path.exists():
                raise FileNotFoundError(
                    f"Base audit path not accessible: {self.base_audit_path}"
                )
            
            logger.info(f"Archiver initialized successfully")
        
        except FileNotFoundError as e:
            logger.error(f"Initialization failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during Archiver initialization: {e}")
            raise

    # ==========================================================
    # PUBLIC ARCHIVE METHOD
    # ==========================================================

    def archive(
        self,
        status: str,
        cluster: str,
        instance: str,
        original_zip_path: Path,
        jira_units: Dict[str, List[str]],
    ) -> Path:
        """
        Archives the deployment result.

        Returns final folder path where files were saved.
        
        Raises:
            ValueError: If status is not PASS or FAIL
            OSError: If file operations fail
        """
        try:
            logger.info(f"Starting archive for {cluster}/{instance} - {status}")
            
            if status not in {"PASS", "FAIL"}:
                raise ValueError("Status must be either 'PASS' or 'FAIL'.")

            destination_folder = (
                self.base_audit_path
                / self.cycle_name
                / ("Processed" if status == "PASS" else "Failed")
                / cluster
                / instance
            )

            destination_folder.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created destination folder: {destination_folder}")

            # Copy ZIP
            zip_destination = destination_folder / original_zip_path.name

            if zip_destination.exists():
                zip_destination = self._generate_unique_filename(
                    destination_folder,
                    original_zip_path.name
                )
                logger.debug(f"ZIP already exists, generating unique name: {zip_destination.name}")

            shutil.copy2(original_zip_path, zip_destination)
            logger.info(f"Copied ZIP: {original_zip_path.name}")

            # Generate compiled_units.txt
            self._generate_compiled_units_file(
                destination_folder,
                cluster,
                instance,
                jira_units
            )
            
            logger.info(f"Archive complete for {cluster}/{instance} in {destination_folder}")
            return destination_folder
        
        except ValueError as e:
            logger.error(f"Invalid status value: {e}")
            raise
        except FileNotFoundError as e:
            logger.error(f"File not found during archive: {e}")
            raise
        except OSError as e:
            logger.error(f"File operation failed during archive: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during archive: {e}", exc_info=True)
            raise

    # ==========================================================
    # INTERNAL HELPERS
    # ==========================================================

    @staticmethod
    def _generate_unique_filename(folder: Path, filename: str) -> Path:
        """
        Generate unique filename if same ZIP already exists.
        """
        base = Path(filename).stem
        suffix = Path(filename).suffix

        counter = 1
        while True:
            new_name = f"{base}_{counter}{suffix}"
            candidate = folder / new_name
            if not candidate.exists():
                return candidate
            counter += 1

    def _generate_compiled_units_file(
        self,
        folder: Path,
        cluster: str,
        instance: str,
        jira_units: Dict[str, List[str]],
    ) -> None:
        """
        Create compiled_units.txt file.
        
        Raises:
            IOError: If file write fails
        """
        try:
            logger.debug(f"Generating compiled_units.txt in {folder}")
            
            compiled_file_path = folder / "compiled_units.txt"

            with open(compiled_file_path, "w", encoding="utf-8") as f:
                f.write(f"Deployment Cycle: {self.cycle_name}\n")
                f.write(f"Cluster: {cluster.upper()}\n")
                f.write(f"Instance: {instance}\n")
                f.write("\n")

                for jira, units in sorted(jira_units.items()):
                    f.write("---------------------------------------\n")
                    f.write(f"JIRA: {jira}\n")
                    f.write("---------------------------------------\n")

                    for index, unit in enumerate(units, start=1):
                        f.write(f"{index}. {unit}\n")

                    f.write("\n")
            
            logger.info(f"Created compiled_units.txt with {sum(len(u) for u in jira_units.values())} total units")
        
        except IOError as e:
            logger.error(f"Error writing compiled_units.txt: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error generating units file: {e}", exc_info=True)
            raise
