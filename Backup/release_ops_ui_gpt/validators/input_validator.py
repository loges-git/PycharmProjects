# validators/input_validator.py

import re
from pathlib import Path


class InputValidationError(Exception):
    """Raised when user input validation fails."""


# -------------------------
# Jira validation
# -------------------------

EPIC_JIRA_PATTERN = re.compile(r"^[A-Z]+-\d+$")
RELEASE_JIRA_PATTERN = re.compile(r"^BANKING-\d{6}$")


def validate_epic_jira(epic_jira: str) -> None:
    if not EPIC_JIRA_PATTERN.match(epic_jira):
        raise InputValidationError(
            f"Invalid Epic Jira format: {epic_jira}"
        )


def validate_release_jira(release_jira: str) -> None:
    if not RELEASE_JIRA_PATTERN.match(release_jira):
        raise InputValidationError(
            f"Invalid Release Jira format: {release_jira}. "
            "Expected format: BANKING-XXXXXX"
        )


# -------------------------
# Branch validation
# -------------------------

BRANCH_NAME_PATTERN = re.compile(
    r"^(feature|bugfix|hotfix)/BANKING-\d{6}$"
)


def validate_branch_name(branch_name: str) -> None:
    if not BRANCH_NAME_PATTERN.match(branch_name):
        raise InputValidationError(
            f"Invalid branch name: {branch_name}"
        )


# -------------------------
# Path validation
# -------------------------

def validate_shared_path(shared_path: Path) -> None:
    if not shared_path.exists():
        raise InputValidationError(
            f"Shared path does not exist: {shared_path}"
        )

    if not shared_path.is_dir():
        raise InputValidationError(
            f"Shared path is not a directory: {shared_path}"
        )
