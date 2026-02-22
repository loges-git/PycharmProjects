import re
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger("deployment_monitor.validator")


class DeploymentValidator:

    def __init__(self, metadata: dict, config: dict):
        self.metadata = metadata
        self.config = config

        self.main_log_path: Path = metadata["main_log_path"]
        self.invalid_log_path: Path = metadata["invalid_log_path"]
        self.error_log_path: Optional[Path] = metadata["error_log_path"]

        self.ignorable_errors = set(config.get("ignorable_errors", []))

        self.detected_errors: List[str] = []
        self.filtered_errors: List[str] = []
        self.error_details: List[Dict] = []  # Store detailed error info
        self.invalid_objects: List[Dict] = []  # Store newly created invalid objects

        self.invalid_mismatch: bool = False
        self.execution_mismatch: bool = False

    # ==========================================================
    # 1️⃣ ERROR VALIDATION
    # ==========================================================

    @staticmethod
    def _extract_errors_from_file(file_path: Path) -> List[Dict]:
        """Extract error details from log file with code, message, unit context."""
        errors: List[Dict] = []
        pattern = re.compile(r"(ORA-\d+|PLS-\d+|compilation errors)", re.IGNORECASE)

        with open(file_path, "r", errors="ignore") as f:
            lines = f.readlines()

        for idx, line in enumerate(lines):
            match = pattern.search(line)
            if match:
                error_code = match.group(0).upper()
                unit_name = None
                
                # Look backward to find the unit/object being compiled
                for back_idx in range(idx - 1, max(0, idx - 20), -1):
                    back_line = lines[back_idx]
                    unit = DeploymentValidator._extract_unit_from_line(back_line)
                    if unit:
                        unit_name = unit
                        break
                
                errors.append({
                    "code": error_code,
                    "message": line.strip(),
                    "unit": unit_name or "Unknown Unit",
                    "file": file_path.name
                })

        return errors

    def validate_errors(self) -> bool:
        try:
            # Main log errors
            logger.info("Starting error validation from logs")
            main_errors = self._extract_errors_from_file(self.main_log_path)
            self.detected_errors.extend([e["code"] for e in main_errors])
            self.error_details.extend(main_errors)

            # oracle_error file errors (if exists)
            if self.error_log_path is not None:
                error_log_errors = self._extract_errors_from_file(self.error_log_path)
                self.detected_errors.extend([e["code"] for e in error_log_errors])
                self.error_details.extend(error_log_errors)

            # Remove ignorable errors
            self.filtered_errors = [
                err for err in self.detected_errors
                if err not in self.ignorable_errors
            ]
            
            # Also filter error_details
            filtered_error_codes = set(self.filtered_errors)
            self.error_details = [
                e for e in self.error_details
                if e["code"] in filtered_error_codes
            ]
            
            logger.info(f"Error validation complete: {len(self.detected_errors)} detected, {len(self.filtered_errors)} non-ignorable")
            return len(self.filtered_errors) == 0
        
        except FileNotFoundError as e:
            logger.error(f"Log file not found: {e}")
            return False
        except Exception as e:
            logger.error(f"Error validating errors: {e}", exc_info=True)
            return False

    def extract_invalid_objects(self) -> List[Dict]:
        """Extract invalid objects created during deployment."""
        try:
            logger.info("Extracting invalid objects from deployment logs")
            invalid_objects: List[Dict] = []

            with open(self.invalid_log_path, "r", errors="ignore") as f:
                lines = f.readlines()

            # Pattern to match invalid object listings
            # Typical format: SCHEMA_NAME.OBJECT_NAME (TYPE) or just OBJECT_NAME
            pattern = re.compile(r"^.*?([A-Z_][A-Z0-9_]*\.[A-Z_][A-Z0-9_]*|[A-Z_][A-Z0-9_]*)\s*(?:\(([^)]+)\))?", re.IGNORECASE)

            in_invalid_section = False
            for line in lines:
                line_lower = line.lower()
                line_stripped = line.strip()

                # Detect start of invalid objects list
                if "invalid object" in line_lower or ("--- " in line_stripped and "invalid" in line_lower):
                    in_invalid_section = True
                    continue

                # Detect end of section
                if in_invalid_section and ("---" in line_stripped or "number of invalids" in line_lower):
                    in_invalid_section = False
                    continue

                # Extract invalid objects
                if in_invalid_section and line_stripped and not line_stripped.startswith("--"):
                    match = pattern.match(line_stripped)
                    if match and match.group(1):
                        object_name = match.group(1)
                        object_type = match.group(2) or "UNKNOWN"
                        
                        if len(object_name) > 2:  # Filter out short lines
                            invalid_objects.append({
                                "object": object_name,
                                "type": object_type.strip(),
                                "source": "invalid_log"
                            })

            logger.info(f"Extracted {len(invalid_objects)} invalid objects")
            self.invalid_objects = invalid_objects
            return invalid_objects
        
        except FileNotFoundError as e:
            logger.error(f"Invalid log file not found: {e}")
            self.invalid_objects = []
            return []
        except Exception as e:
            logger.error(f"Error extracting invalid objects: {e}", exc_info=True)
            self.invalid_objects = []
            return []

    def validate_invalid_delta(self) -> bool:
        try:
            logger.info("Starting invalid delta validation")
            start_count: Optional[int] = None
            end_count: Optional[int] = None

            with open(self.invalid_log_path, "r", errors="ignore") as f:
                lines = f.readlines()

            for line in lines:
                line_lower = line.lower()

                if "number of invalids at start" in line_lower:
                    numbers = re.findall(r"\d+", line)
                    if numbers:
                        start_count = int(numbers[0])

                elif "number of invalids at end" in line_lower:
                    numbers = re.findall(r"\d+", line)
                    if numbers:
                        end_count = int(numbers[0])

            if start_count is None or end_count is None:
                logger.warning("Could not extract start/end invalid counts from log")
                self.invalid_mismatch = True
                return False

            if start_count != end_count:
                logger.warning(f"Invalid delta detected: start={start_count}, end={end_count}")
                self.invalid_mismatch = True
                return False

            logger.info(f"Invalid delta validation passed: {start_count} == {end_count}")
            return True
        
        except FileNotFoundError as e:
            logger.error(f"Invalid log file not found: {e}")
            self.invalid_mismatch = False
            return False
        except ValueError as e:
            logger.error(f"Error parsing invalid delta counts: {e}")
            self.invalid_mismatch = False
            return False
        except Exception as e:
            logger.error(f"Error validating invalid delta: {e}", exc_info=True)
            self.invalid_mismatch = False
            return False

    # ==========================================================
    # 3️⃣ EXECUTION INTEGRITY VALIDATION
    # ==========================================================

    def validate_execution_integrity(self) -> bool:
        try:
            logger.info("Starting execution integrity validation")
            execution_start: List[str] = []
            execution_end: List[str] = []

            with open(self.main_log_path, "r", errors="ignore") as f:
                for line in f:
                    line_lower = line.lower()

                    if "execution start" in line_lower:
                        unit = self._extract_unit_from_line(line)
                        if unit:
                            execution_start.append(unit)

                    elif "execution end" in line_lower:
                        unit = self._extract_unit_from_line(line)
                        if unit:
                            execution_end.append(unit)

            start_set = set(execution_start)
            end_set = set(execution_end)

            if len(execution_start) != len(execution_end):
                logger.warning(f"Execution count mismatch: {len(execution_start)} starts vs {len(execution_end)} ends")
                self.execution_mismatch = True
                return False

            if start_set != end_set:
                missing_ends = start_set - end_set
                missing_starts = end_set - start_set
                logger.warning(f"Execution set mismatch - Missing ends: {missing_ends}, Missing starts: {missing_starts}")
                self.execution_mismatch = True
                return False

            logger.info(f"Execution integrity validation passed: {len(execution_start)} units tracked successfully")
            self.execution_mismatch = False
            return True
        
        except FileNotFoundError as e:
            logger.error(f"Main log file not found for execution check: {e}")
            self.execution_mismatch = False
            return False
        except Exception as e:
            logger.error(f"Error validating execution integrity: {e}", exc_info=True)
            self.execution_mismatch = False
            return False

    @staticmethod
    def _extract_unit_from_line(line: str) -> Optional[str]:
        marker = " - execution"
        marker_index = line.lower().find(marker)

        if marker_index == -1:
            return None

        path_part = line[:marker_index].strip()
        unit = Path(path_part).name

        return unit if unit else None

    # ==========================================================
    # 4️⃣ MASTER VALIDATION
    # ==========================================================

    def validate_all(self) -> Dict:
        try:
            logger.info("Starting comprehensive deployment validation")
            
            error_valid = self.validate_errors()
            invalid_valid = self.validate_invalid_delta()
            execution_valid = self.validate_execution_integrity()
            
            # Extract invalid objects if validation failed on invalid delta
            if not invalid_valid:
                logger.info("Invalid delta detected, extracting invalid objects")
                self.invalid_objects = self.extract_invalid_objects()

            if not error_valid:
                logger.warning("Validation FAILED: Non-ignorable errors detected")
                return self._build_result("FAIL", "Non-ignorable errors detected")

            if not invalid_valid:
                logger.warning("Validation FAILED: Invalid object mismatch detected")
                return self._build_result("FAIL", "Invalid object mismatch detected")

            if not execution_valid:
                logger.warning("Validation FAILED: Execution start/end mismatch detected")
                return self._build_result("FAIL", "Execution start/end mismatch detected")

            logger.info("Validation PASSED: All checks successful")
            return self._build_result("PASS", "Deployment validated successfully")
        
        except Exception as e:
            logger.error(f"Unexpected error during validation: {e}", exc_info=True)
            return self._build_result("FAIL", f"Unexpected error during validation: {str(e)}")

    def _build_result(self, status: str, message: str) -> Dict:
        return {
            "status": status,
            "message": message,
            "detected_errors": self.detected_errors,
            "filtered_errors": self.filtered_errors,
            "error_details": self.error_details,
            "invalid_objects": self.invalid_objects,
            "invalid_mismatch": self.invalid_mismatch,
            "execution_mismatch": self.execution_mismatch
        }
