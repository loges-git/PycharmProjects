import zipfile
import tempfile
import shutil
import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger("deployment_monitor.zip_processor")


class ZipProcessor:
    @staticmethod
    def _validate_extract_path(extract_dir: Path, member_path: str) -> Path:
        """
        Validate that extracted file stays within extraction directory.
        Prevents directory traversal attacks (e.g., ../../etc/passwd).
        
        Args:
            extract_dir: The directory files are being extracted to
            member_path: The path of the file being extracted
            
        Returns:
            Validated absolute path
            
        Raises:
            ValueError: If path traversal detected
        """
        member_abs = (extract_dir / member_path).resolve()
        extract_abs = extract_dir.resolve()
        
        try:
            member_abs.relative_to(extract_abs)
            return member_abs
        except ValueError:
            logger.error(f"Path traversal detected: {member_path}")
            raise ValueError(f"Malicious path detected in ZIP: {member_path}")
    
    def __init__(self, zip_path: str | Path, config: dict):
        self.zip_path: Path = Path(zip_path)
        self.config = config
        self.temp_dir: Optional[Path] = None

    # ==========================================================
    # ZIP EXTRACTION
    # ==========================================================

    def extract_zip(self) -> Path:
        """
        Extract ZIP into temporary directory with path traversal protection.
        
        Returns:
            Path to extracted directory
            
        Raises:
            ValueError: If file is not a valid ZIP or contains malicious paths
            IOError: If extraction fails
        """
        try:
            logger.info(f"Starting ZIP extraction with path validation: {self.zip_path}")
            
            if not self.zip_path.exists():
                raise FileNotFoundError(f"ZIP file not found: {self.zip_path}")
            
            if not zipfile.is_zipfile(self.zip_path):
                raise ValueError(f"Invalid ZIP file: {self.zip_path}")

            temp_dir = Path(tempfile.mkdtemp())
            self.temp_dir = temp_dir
            logger.debug(f"Created temporary directory: {temp_dir}")

            with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
                for member in zip_ref.namelist():
                    # Validate member path
                    self._validate_extract_path(temp_dir, member)
                    zip_ref.extract(member, temp_dir)
            
            logger.info(f"ZIP extraction successful: {len(list(temp_dir.rglob('*')))} files extracted")
            return temp_dir
        
        except FileNotFoundError as e:
            logger.error(f"ZIP file not found: {e}")
            raise
        except ValueError as e:
            logger.error(f"ZIP validation failed: {e}")
            raise
        except zipfile.BadZipFile as e:
            logger.error(f"Corrupted ZIP file: {e}")
            raise ValueError(f"ZIP file is corrupted: {e}")
        except Exception as e:
            logger.error(f"ZIP extraction failed: {e}", exc_info=True)
            raise

    # ==========================================================
    # LOG DISCOVERY
    # ==========================================================

    def _find_required_logs(self) -> Tuple[Optional[Path], Optional[Path], Optional[Path]]:
        """
        Identify:
        - *_oracle.log_completed.log
        - *_invalids_completed.log
        - oracle_error file (optional)
        
        Returns:
            Tuple of (main_log, invalid_log, error_log)
            
        Raises:
            RuntimeError: If ZIP not extracted yet
        """
        try:
            logger.info("Starting log file discovery in extracted ZIP")
            
            if self.temp_dir is None:
                raise RuntimeError("ZIP must be extracted before searching logs.")

            main_log: Optional[Path] = None
            invalid_log: Optional[Path] = None
            error_log: Optional[Path] = None

            for file_path in self.temp_dir.rglob("*"):
                if not file_path.is_file():
                    continue

                file_lower = file_path.name.lower()

                if file_lower.endswith("_oracle.log_completed.log"):
                    main_log = file_path
                    logger.debug(f"Found main log: {file_path.name}")

                elif file_lower.endswith("_invalids_completed.log"):
                    invalid_log = file_path
                    logger.debug(f"Found invalid log: {file_path.name}")

                elif "oracle_error" in file_lower:
                    error_log = file_path
                    logger.debug(f"Found error log: {file_path.name}")

            logger.info(f"Log discovery complete - main: {main_log is not None}, invalid: {invalid_log is not None}, error: {error_log is not None}")
            return main_log, invalid_log, error_log
        
        except RuntimeError as e:
            logger.error(f"Runtime error during log discovery: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during log discovery: {e}", exc_info=True)
            raise

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
        
        Args:
            instance: Instance name (e.g., "FSMHO1U")
            
        Returns:
            Cluster name
            
        Raises:
            ValueError: If instance not found in config
        """
        try:
            logger.debug(f"Detecting cluster for instance: {instance}")
            
            for cluster, instances in self.config["clusters"].items():
                if instance in instances:
                    logger.info(f"Instance {instance} mapped to cluster: {cluster}")
                    return cluster

            raise ValueError(f"Instance '{instance}' not mapped to any cluster in config.")
        
        except ValueError as e:
            logger.error(f"Cluster detection failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error detecting cluster: {e}", exc_info=True)
            raise

    # ==========================================================
    # MAIN PROCESS METHOD
    # ==========================================================

    def process(self) -> dict:
        """
        Main processing method.
        Returns structured metadata.
        
        Returns:
            Dictionary with instance, cluster, and log paths
            
        Raises:
            FileNotFoundError: If required log files not found
            ValueError: If instance not in cluster config
        """
        try:
            logger.info(f"Starting ZIP processing: {self.zip_path}")
            
            self.extract_zip()

            main_log, invalid_log, error_log = self._find_required_logs()

            if main_log is None:
                raise FileNotFoundError("Main oracle log file not found in ZIP.")

            if invalid_log is None:
                raise FileNotFoundError("Invalid log file not found in ZIP.")

            instance = self._extract_instance_from_filename(main_log)
            logger.debug(f"Extracted instance: {instance}")
            
            cluster = self._detect_cluster(instance)

            metadata = {
                "instance": instance,
                "cluster": cluster,
                "main_log_path": main_log,
                "invalid_log_path": invalid_log,
                "error_log_path": error_log,
                "temp_dir": self.temp_dir
            }
            
            logger.info(f"ZIP processing complete: {instance}/{cluster}")
            return metadata
        
        except FileNotFoundError as e:
            logger.error(f"Required log file missing: {e}")
            raise
        except ValueError as e:
            logger.error(f"Instance validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during ZIP processing: {e}", exc_info=True)
            raise

    # ==========================================================
    # CLEANUP AND CONTEXT MANAGER
    # ==========================================================

    def __enter__(self):
        """Context manager entry point."""
        logger.debug("Entering ZipProcessor context manager")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit point - ensures cleanup on any exit."""
        try:
            logger.debug("Exiting ZipProcessor context manager")
            if exc_type is not None:
                logger.warning(f"Exception in context: {exc_type.__name__}: {exc_val}")
            self.cleanup()
            return False
        except Exception as e:
            logger.error(f"Error during context cleanup: {e}", exc_info=True)
            raise

    def cleanup(self):
        """
        Remove temporary extraction directory.
        """
        try:
            if self.temp_dir and self.temp_dir.exists():
                logger.info(f"Cleaning up temporary directory: {self.temp_dir}")
                shutil.rmtree(self.temp_dir)
                logger.debug("Temporary directory cleanup complete")
            else:
                logger.debug("No temporary directory to clean up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
            raise
