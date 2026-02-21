import re
from pathlib import Path
from typing import Dict, List, Set, Optional


class JiraExtractor:
    """
    Extract JIRA -> compiled units mapping from main log file.
    """

    JIRA_PATTERN = re.compile(r"\b[A-Z]+-\d+\b")
    EXECUTION_START_PATTERN = re.compile(r"- execution start", re.IGNORECASE)

    def __init__(self, main_log_path: Path):
        self.main_log_path = Path(main_log_path)

    # ==========================================================
    # PUBLIC METHOD
    # ==========================================================

    def extract(self) -> Dict[str, List[str]]:
        """
        Returns:
        {
            "BANKING-408942": ["UNIT_A.INC", "UNIT_B.DBP"],
            "BANKING-123444": ["UNIT_X.SQL"]
        }
        """

        jira_unit_map: Dict[str, Set[str]] = {}
        current_jira: Optional[str] = None

        with open(self.main_log_path, "r", errors="ignore") as f:
            for line in f:
                # --------------------------------------------------
                # Detect JIRA
                # --------------------------------------------------
                jira_match = self.JIRA_PATTERN.search(line)
                if jira_match:
                    current_jira = jira_match.group(0).upper()
                    if current_jira not in jira_unit_map:
                        jira_unit_map[current_jira] = set()

                # --------------------------------------------------
                # Detect Execution Start
                # --------------------------------------------------
                if self.EXECUTION_START_PATTERN.search(line):
                    unit = self._extract_unit_from_line(line)

                    if unit is not None and current_jira is not None:
                        jira_unit_map[current_jira].add(unit)

        # Convert sets to sorted lists
        final_map: Dict[str, List[str]] = {
            jira: sorted(units)
            for jira, units in jira_unit_map.items()
        }

        return final_map

    # ==========================================================
    # INTERNAL HELPERS
    # ==========================================================

    @staticmethod
    def _extract_unit_from_line(line: str) -> Optional[str]:
        """
        Extract unit name from:
        .../EG1_EGYPT_ISO_BRNPRM.INC - execution start
        """

        marker = " - execution"
        marker_index = line.lower().find(marker)

        if marker_index == -1:
            return None

        path_part = line[:marker_index].strip()

        # Split using both Unix and Windows separators safely
        unit = Path(path_part).name

        return unit if unit else None
