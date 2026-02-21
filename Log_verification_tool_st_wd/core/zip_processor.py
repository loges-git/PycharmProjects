import zipfile
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Tuple


class ZipProcessor:
    def __init__(self, zip_path: str | Path, config: dict):
        self.zip_path: Path = Path(zip_path)
        self.config = config
        self.temp_dir: Optional[Path] = None

    # ==========================================================
    # ZIP EXTRACTION
    # ==========================================================

    def extract_zip(self) -> Path:
        """
        Extract ZIP into temporary directory.
        """
        if not zipfile.is_zipfile(self.zip_path):
            raise ValueError(f"Invalid ZIP file: {self.zip_path}")

        temp_dir = Path(tempfile.mkdtemp())
        self.temp_dir = temp_dir

        try:
            with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)
        except Exception as e:
            raise Exception(f"Failed to extract ZIP: {e}")

        return temp_dir

    # ==========================================================
    # LOG DISCOVERY
    # ==========================================================

    def _find_required_logs(self) -> Tuple[Optional[Path], Optional[Path], Optional[Path]]:
        """
        Identify:
        - *_oracle.log_completed.log
        - *_invalids_completed.log
        - oracle_error file (optional)
        """
        main_log: Optional[Path] = None
        invalid_log: Optional[Path] = None
        error_log: Optional[Path] = None

        if self.temp_dir is None:
            raise RuntimeError("ZIP must be extracted before searching logs.")

        for file_path in self.temp_dir.rglob("*"):
            if not file_path.is_file():
                continue

            file_lower = file_path.name.lower()

            if file_lower.endswith("_oracle.log_completed.log"):
                main_log = file_path

            elif file_lower.endswith("_invalids_completed.log"):
                invalid_log = file_path

            elif "oracle_error" in file_lower:
                error_log = file_path

        return main_log, invalid_log, error_log

    # ==========================================================
    # INSTANCE & CLUSTER DETECTION
    # ==========================================================

    @staticmethod
    def _extract_instance_from_filename(main_log_path: Path) -> str:
        """
        Extract instance from filename.
        Example:
        FSMHO1U_oracle.log_completed.log
        """
        filename = main_log_path.name
        return filename.split("_")[0]

    def _detect_cluster(self, instance: str) -> str:
        """
        Map instance to cluster using config.
        """
        for cluster, instances in self.config["clusters"].items():
            if instance in instances:
                return cluster

        raise ValueError(f"Instance '{instance}' not mapped to any cluster in config.")

    # ==========================================================
    # MAIN PROCESS METHOD
    # ==========================================================

    def process(self) -> dict:
        """
        Main processing method.
        Returns structured metadata.
        """
        self.extract_zip()

        main_log, invalid_log, error_log = self._find_required_logs()

        if main_log is None:
            raise FileNotFoundError("Main oracle log file not found in ZIP.")

        if invalid_log is None:
            raise FileNotFoundError("Invalid log file not found in ZIP.")

        instance = self._extract_instance_from_filename(main_log)
        cluster = self._detect_cluster(instance)

        return {
            "instance": instance,
            "cluster": cluster,
            "main_log_path": main_log,
            "invalid_log_path": invalid_log,
            "error_log_path": error_log,
            "temp_dir": self.temp_dir
        }

    # ==========================================================
    # CLEANUP
    # ==========================================================

    def cleanup(self):
        """
        Remove temporary extraction directory.
        """
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
