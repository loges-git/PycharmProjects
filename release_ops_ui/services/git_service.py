import subprocess
from pathlib import Path
from typing import List


class GitCommandError(Exception):
    """Raised when a git command fails."""

    def __init__(self, message: str, command: List[str], stdout: str, stderr: str):
        super().__init__(message)
        self.command = command
        self.stdout = stdout
        self.stderr = stderr


def _run_git_command(
    args: List[str],
    repo_path: Path,
    check: bool = True
) -> str:
    """
    Internal helper to run git commands safely.
    """

    process = subprocess.run(
        args,
        cwd=repo_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if check and process.returncode != 0:
        raise GitCommandError(
            message="Git command failed",
            command=args,
            stdout=process.stdout.strip(),
            stderr=process.stderr.strip()
        )

    return process.stdout.strip()


# -------------------------
# Read-only helpers
# -------------------------

def get_current_branch(repo_path: Path) -> str:
    return _run_git_command(
        ["git", "branch", "--show-current"],
        repo_path
    )


def is_repo(repo_path: Path) -> bool:
    try:
        _run_git_command(
            ["git", "rev-parse", "--is-inside-work-tree"],
            repo_path
        )
        return True
    except GitCommandError:
        return False


def is_working_tree_clean(repo_path: Path) -> bool:
    status = _run_git_command(
        ["git", "status", "--porcelain"],
        repo_path
    )
    return status == ""


def get_remote_branch_head(
    repo_path: Path,
    branch: str
) -> str:
    """
    Get commit hash of remote branch HEAD.
    """
    return _run_git_command(
        ["git", "rev-parse", f"origin/{branch}"],
        repo_path
    )


def get_file_blob_hash(
    repo_path: Path,
    file_path: str
) -> str:
    """
    Get blob hash of a file in working tree.
    """
    return _run_git_command(
        ["git", "hash-object", file_path],
        repo_path
    )


# -------------------------
# Branch operations
# -------------------------

def fetch(repo_path: Path) -> None:
    _run_git_command(["git", "fetch"], repo_path)


def checkout(branch: str, repo_path: Path) -> None:
    _run_git_command(["git", "checkout", branch], repo_path)


def checkout_new_branch(
    branch: str,
    base_branch: str,
    repo_path: Path
) -> None:
    _run_git_command(["git", "checkout", base_branch], repo_path)
    _run_git_command(["git", "pull"], repo_path)
    _run_git_command(["git", "checkout", "-b", branch], repo_path)


# -------------------------
# Commit & push
# -------------------------

def add_files(files: List[str], repo_path: Path) -> None:
    _run_git_command(["git", "add", *files], repo_path)


def commit(message: str, repo_path: Path) -> None:
    _run_git_command(["git", "commit", "-m", message], repo_path)


def push(branch: str, repo_path: Path) -> None:
    _run_git_command(["git", "push", "-u", "origin", branch], repo_path)


def pull(repo_path: Path) -> None:
    _run_git_command(["git", "pull"], repo_path)


# -------------------------
# Clone
# -------------------------

def clone(repo_url: str, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "clone", repo_url, str(target_path)],
        check=True
    )


# =========================================================
# ADDITIVE WRAPPERS (for release_service compatibility)
# =========================================================

def run_git_command(cmd: List[str], cwd: Path) -> str:
    """
    Public wrapper for validators & services.
    """
    return _run_git_command(cmd, cwd)


def checkout_branch(repo_path: Path, branch: str) -> None:
    checkout(branch, repo_path)


def create_or_checkout_branch(
    repo_path: Path,
    branch_name: str,
    base_branch: str
) -> None:
    """
    Create branch if missing, else checkout.
    """
    branches = _run_git_command(
        ["git", "branch", "--list", branch_name],
        repo_path
    )

    if branches.strip():
        checkout(branch_name, repo_path)
    else:
        checkout_new_branch(branch_name, base_branch, repo_path)


def stage_all(repo_path: Path) -> None:
    _run_git_command(["git", "add", "."], repo_path)


def commit_changes(repo_path: Path, message: str) -> None:
    commit(message, repo_path)


def push_branch(repo_path: Path, branch: str) -> None:
    push(branch, repo_path)
