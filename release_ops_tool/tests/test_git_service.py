import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from services.git_service import (
    get_remote_branch_head,
    get_file_blob_hash,
    GitCommandError,
    _run_git_command
)


@pytest.fixture
def mock_repo_path():
    return Path("/tmp/mock_repo")


@patch("subprocess.run")
def test_get_remote_branch_head_success(mock_run, mock_repo_path):
    # Setup mock
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = "abc123456789\n"
    mock_run.return_value = mock_process

    # Test
    result = get_remote_branch_head(mock_repo_path, "main")

    # Verify
    assert result == "abc123456789"
    mock_run.assert_called_with(
        ["git", "rev-parse", "origin/main"],
        cwd=mock_repo_path,
        stdout=-1,
        stderr=-1,
        text=True
    )


@patch("subprocess.run")
def test_get_remote_branch_head_failure(mock_run, mock_repo_path):
    # Setup mock failure
    mock_process = MagicMock()
    mock_process.returncode = 128
    mock_process.stdout = ""
    mock_process.stderr = "fatal: ambiguous argument..."
    mock_run.return_value = mock_process

    # Test
    with pytest.raises(GitCommandError) as exc:
        get_remote_branch_head(mock_repo_path, "non-existent")

    assert "Git command failed" in str(exc.value)
    assert exc.value.stderr == "fatal: ambiguous argument..."


@patch("subprocess.run")
def test_get_file_blob_hash(mock_run, mock_repo_path):
    mock_process = MagicMock()
    mock_process.returncode = 0
    mock_process.stdout = "def456\n"
    mock_run.return_value = mock_process

    result = get_file_blob_hash(mock_repo_path, "file.txt")

    assert result == "def456"
    mock_run.assert_called_with(
        ["git", "hash-object", "file.txt"],
        cwd=mock_repo_path,
        stdout=-1,
        stderr=-1,
        text=True
    )
