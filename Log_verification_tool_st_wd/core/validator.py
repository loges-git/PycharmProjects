import re
from pathlib import Path
from typing import List, Dict, Optional


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

        self.invalid_mismatch: bool = False
        self.execution_mismatch: bool = False

    # ==========================================================
    # 1️⃣ ERROR VALIDATION
    # ==========================================================

    @staticmethod
    def _extract_errors_from_file(file_path: Path) -> List[str]:
        errors: List[str] = []

        pattern = re.compile(r"(ORA-\d+|PLS-\d+|compilation errors)", re.IGNORECASE)

        with open(file_path, "r", errors="ignore") as f:
            for line in f:
                match = pattern.search(line)
                if match:
                    errors.append(match.group(0).upper())

        return errors

    def validate_errors(self) -> bool:
        # Main log errors
        self.detected_errors.extend(
            self._extract_errors_from_file(self.main_log_path)
        )

        # oracle_error file errors (if exists)
        if self.error_log_path is not None:
            self.detected_errors.extend(
                self._extract_errors_from_file(self.error_log_path)
            )

        # Remove ignorable errors
        self.filtered_errors = [
            err for err in self.detected_errors
            if err not in self.ignorable_errors
        ]

        return len(self.filtered_errors) == 0

    # ==========================================================
    # 2️⃣ INVALID DELTA VALIDATION
    # ==========================================================

    def validate_invalid_delta(self) -> bool:
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
            self.invalid_mismatch = True
            return False

        if start_count != end_count:
            self.invalid_mismatch = True
            return False

        return True

    # ==========================================================
    # 3️⃣ EXECUTION INTEGRITY VALIDATION
    # ==========================================================

    def validate_execution_integrity(self) -> bool:
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
            self.execution_mismatch = True
            return False

        if start_set != end_set:
            self.execution_mismatch = True
            return False

        return True

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
        error_valid = self.validate_errors()
        invalid_valid = self.validate_invalid_delta()
        execution_valid = self.validate_execution_integrity()

        if not error_valid:
            return self._build_result("FAIL", "Non-ignorable errors detected")

        if not invalid_valid:
            return self._build_result("FAIL", "Invalid object mismatch detected")

        if not execution_valid:
            return self._build_result("FAIL", "Execution start/end mismatch detected")

        return self._build_result("PASS", "Deployment validated successfully")

    def _build_result(self, status: str, message: str) -> Dict:
        return {
            "status": status,
            "message": message,
            "detected_errors": self.detected_errors,
            "filtered_errors": self.filtered_errors,
            "invalid_mismatch": self.invalid_mismatch,
            "execution_mismatch": self.execution_mismatch
        }
