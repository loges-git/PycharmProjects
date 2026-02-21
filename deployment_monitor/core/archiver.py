import shutil
from pathlib import Path
from typing import Dict, List


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
        self.base_audit_path = Path(base_audit_path)
        self.cycle_name = cycle_name

        if not self.base_audit_path.exists():
            raise FileNotFoundError(
                f"Base audit path not accessible: {self.base_audit_path}"
            )

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
        """

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

        # ------------------------------------------------------
        # Copy ZIP
        # ------------------------------------------------------
        zip_destination = destination_folder / original_zip_path.name

        if zip_destination.exists():
            zip_destination = self._generate_unique_filename(
                destination_folder,
                original_zip_path.name
            )

        shutil.copy2(original_zip_path, zip_destination)

        # ------------------------------------------------------
        # Generate compiled_units.txt
        # ------------------------------------------------------
        self._generate_compiled_units_file(
            destination_folder,
            cluster,
            instance,
            jira_units
        )

        return destination_folder

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
        """

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
