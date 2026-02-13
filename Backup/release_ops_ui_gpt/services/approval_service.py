# services/approval_service.py

import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, UTC

from models.release_context import Environment, ReleaseType


class ApprovalServiceError(Exception):
    """Raised when approval service fails."""


def create_approval_record(
        approval_dir: Path,
        approval_id: str,
        environment: Environment,
        release_type: ReleaseType,
        base_branch: str,
        base_commit: str,
        approved_files: Dict[str, str],
        release_jira: Optional[str] = None,
        cluster: Optional[str] = None,
        shared_path: Optional[str] = None,
        search_tag: Optional[str] = None
) -> Path:
    """
    Persist approval record to disk.
    """

    approval_dir.mkdir(parents=True, exist_ok=True)

    approval_file = approval_dir / f"{approval_id}.json"

    record = {
        "approval_id": approval_id,
        "environment": environment.value,
        "release_type": release_type.value,
        "base_branch": base_branch,
        "base_commit": base_commit,
        "approved_files": approved_files,
        "approved_at": datetime.now(UTC).isoformat(),
        "release_jira": release_jira,
        "cluster": cluster,
        "shared_path": shared_path,
        "search_tag": search_tag,
        "consumed": False,
        "consumed_at": None,
        "revoked": False,
        "revoked_at": None,
        "revoked_by": None,
        "revoke_reason": None
    }

    with approval_file.open("w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)

    return approval_file


def load_approval_record(
        approval_file: Path
) -> dict:
    """
    Load approval record from disk.
    """

    if not approval_file.exists():
        raise ApprovalServiceError(
            f"Approval record not found: {approval_file}"
        )

    with approval_file.open("r", encoding="utf-8") as f:
        return json.load(f)


def mark_approval_consumed(approval_file: Path) -> None:
    """
    Mark an approval as consumed (used in a release).
    """
    approval_data = load_approval_record(approval_file)
    approval_data["consumed"] = True
    approval_data["consumed_at"] = datetime.now(UTC).isoformat()

    with approval_file.open("w", encoding="utf-8") as f:
        json.dump(approval_data, f, indent=2)


def revoke_approval(approval_file: Path, revoked_by: str, reason: str) -> None:
    """
    Revoke an approval (manager changed mind, found issue, etc.)
    """
    approval_data = load_approval_record(approval_file)

    if approval_data.get("consumed", False):
        raise ApprovalServiceError(
            "Cannot revoke approval that has already been consumed in a release"
        )

    approval_data["revoked"] = True
    approval_data["revoked_at"] = datetime.now(UTC).isoformat()
    approval_data["revoked_by"] = revoked_by
    approval_data["revoke_reason"] = reason

    with approval_file.open("w", encoding="utf-8") as f:
        json.dump(approval_data, f, indent=2)