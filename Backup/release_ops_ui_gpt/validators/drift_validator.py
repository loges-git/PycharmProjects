# validators/drift_validator.py

from pathlib import Path
import subprocess
import hashlib
import json

class DriftReadError(Exception):
    """Raised when approved file cannot be read from remote branch."""

class DriftDetectedError(Exception):
    def __init__(self, drifted_files: list[str]):
        self.drifted_files = drifted_files
        super().__init__(
            "Drift detected in approved files:\n" + "\n".join(drifted_files)
        )


def _hash_content(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _git_fetch(repo_path: Path) -> None:
    subprocess.run(
        ["git", "fetch"],
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        text=True
    )


def _git_show_file(
    repo_path: Path,
    branch: str,
    file_path: str
) -> str | None:
    """
    Read file content directly from remote branch.
    Returns None if file doesn't exist in remote (new file).
    """
    cmd = [
        "git",
        "show",
        f"origin/{branch}:{file_path}"
    ]

    result = subprocess.run(
        cmd,
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        # File doesn't exist in remote branch (new file being added)
        return None

    return result.stdout


def validate_no_drift(
    repo_path: Path,
    base_branch: str,
    approval_file: Path
) -> dict:
    """
    Validate approved files against remote base branch.

    Returns per-file status:
    {
        "file.sql": {
            "approved": True,
            "drifted": False,
            "new_file": True/False
        }
    }

    Raises DriftDetectedError if any file drifted.
    """

    # 🔒 Always sync with remote first
    _git_fetch(repo_path)

    with approval_file.open("r", encoding="utf-8") as f:
        approval_data = json.load(f)

    approved_files = approval_data.get("approved_files", {})
    status_map = {}
    drifted_files = []

    for rel_path, approved_hash in approved_files.items():
        remote_content = _git_show_file(
            repo_path=repo_path,
            branch=base_branch,
            file_path=rel_path
        )

        if remote_content is None:
            # New file being added - cannot drift
            status_map[rel_path] = {
                "approved": True,
                "drifted": False,
                "new_file": True
            }
        else:
            # Existing file - check for drift
            remote_hash = _hash_content(remote_content)
            is_drifted = remote_hash != approved_hash

            status_map[rel_path] = {
                "approved": True,
                "drifted": is_drifted,
                "new_file": False
            }

            if is_drifted:
                drifted_files.append(rel_path)

    if drifted_files:
        raise DriftDetectedError(drifted_files)

    return status_map