# services/repo_sync_service.py

from pathlib import Path

from services import git_service


class RepoSyncError(Exception):
    """Raised when repo sync operation fails."""


def ensure_repo_cloned(
    repo_url: str,
    local_path: Path
) -> None:
    """
    Ensure repository exists locally.
    Clone if missing.
    """

    if local_path.exists():
        if not git_service.is_repo(local_path):
            raise RepoSyncError(
                f"Path exists but is not a git repository: {local_path}"
            )
        return

    git_service.clone(repo_url, local_path)


def refresh_repo(
    local_path: Path,
    base_branch: str
) -> None:
    """
    Fetch and pull latest changes on base branch.
    """

    if not git_service.is_repo(local_path):
        raise RepoSyncError(
            f"Not a git repository: {local_path}"
        )

    git_service.fetch(local_path)
    git_service.checkout(base_branch, local_path)
    git_service.pull(local_path)

