# validators/approval_validator.py

from typing import Dict

from models.release_context import Environment


class ApprovalValidationError(Exception):
    """Raised when approval validation fails."""


def validate_approval_exists(
    approval_id: str | None,
    approved_files: Dict[str, str]
) -> None:
    if not approval_id:
        raise ApprovalValidationError(
            "No approval record found."
        )

    if not approved_files:
        raise ApprovalValidationError(
            "Approval exists but no files were approved."
        )


def validate_approval_environment(
    approval_environment: Environment,
    current_environment: Environment
) -> None:
    if approval_environment != current_environment:
        raise ApprovalValidationError(
            f"Approval environment '{approval_environment.value}' "
            f"does not match current environment '{current_environment.value}'."
        )
