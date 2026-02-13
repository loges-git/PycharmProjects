# validators/repo_validator.py

from pathlib import Path

from services import git_service


class RepoValidationError(Exception):
    """Raised when repository validation fails."""


def validate_repo_exists(repo_path: Path) -> None:
    """
    Ensure path exists and is a git repository.
    """
    if not repo_path.exists():
        raise RepoValidationError(
            f"Repository path does not exist: {repo_path}"
        )

    if not git_service.is_repo(repo_path):
        raise RepoValidationError(
            f"Path is not a git repository: {repo_path}"
        )


def validate_working_tree_clean(repo_path: Path) -> None:
    """
    Ensure no uncommitted changes exist.
    """
    if not git_service.is_working_tree_clean(repo_path):
        raise RepoValidationError(
            "Working tree is not clean. "
            "Please commit, stash, or discard changes before proceeding."
        )


def validate_on_branch(
    repo_path: Path,
    expected_branch: str
) -> None:
    """
    Ensure repo is on expected branch.
    """
    current_branch = git_service.get_current_branch(repo_path)

    if current_branch != expected_branch:
        raise RepoValidationError(
            f"Repository is on branch '{current_branch}', "
            f"but expected '{expected_branch}'."
        )
# --------------------------------------------------
# Alias for release_service compatibility
# --------------------------------------------------

def ensure_clean_working_tree(repo_path: Path) -> None:
    """
    Alias used by release_service.
    Internally delegates to validate_working_tree_clean.
    """
    validate_working_tree_clean(repo_path)
