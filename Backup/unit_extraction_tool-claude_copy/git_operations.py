"""
Git operations module for repository management
"""

import os
import re
import subprocess
from pathlib import Path
from typing import Optional
import git
from git import Repo, GitCommandError
from config import BRANCH_MAPPING, CLONE_URLS
from utils import escape_jira_for_grep, should_skip_fe_file


def check_repo_exists(base_path: str, repo_name: str) -> bool:
    """Check if repository exists locally"""
    repo_path = Path(base_path) / repo_name
    return repo_path.exists() and (repo_path / '.git').exists()


def clone_repository(base_path: str, logical_repo: str, variant: str, custom_url: str = None) -> tuple:
    """
    Clone repository if not exists

    Args:
        base_path: Base directory
        logical_repo: Logical repo name (e.g., 'ssa')
        variant: 'db' or 'fe'
        custom_url: Optional custom clone URL (overrides config)

    Returns: (success: bool, message: str, repo_path: str)
    """
    try:
        # Get clone URL from config or use custom
        if custom_url:
            clone_url = custom_url
        else:
            if logical_repo not in CLONE_URLS or variant not in CLONE_URLS[logical_repo]:
                return False, f"Clone URL not configured for {logical_repo}.{variant}", ""
            clone_url = CLONE_URLS[logical_repo][variant]

        # Create repo directory name
        repo_dir_name = f"{logical_repo}.{variant}"
        repo_path = Path(base_path) / repo_dir_name

        if repo_path.exists():
            return False, f"Directory {repo_path} already exists", str(repo_path)

        Repo.clone_from(clone_url, repo_path)
        return True, f"Successfully cloned {logical_repo}.{variant}", str(repo_path)

    except GitCommandError as e:
        return False, f"Git clone failed: {str(e)}", ""
    except Exception as e:
        return False, f"Error cloning repository: {str(e)}", ""


def get_repo_object(repo_path: str) -> tuple:
    """
    Get GitPython Repo object
    Returns: (success: bool, repo_object or error_message)
    """
    try:
        repo = Repo(repo_path)
        if repo.bare:
            return False, "Repository is bare"
        return True, repo
    except Exception as e:
        return False, f"Error accessing repository: {str(e)}"


def get_current_branch(repo_path: str) -> Optional[str]:
    """Get currently checked out branch"""
    try:
        repo = Repo(repo_path)
        return repo.active_branch.name
    except Exception:
        return None


def check_uncommitted_changes(repo_path: str) -> tuple:
    """
    Check for uncommitted changes
    Returns: (has_changes: bool, status_message: str)
    """
    try:
        repo = Repo(repo_path)

        # Check for modified files
        if repo.is_dirty(untracked_files=True):
            changed_files = [item.a_path for item in repo.index.diff(None)]
            untracked_files = repo.untracked_files

            status_msg = ""
            if changed_files:
                status_msg += f"Modified files: {', '.join(changed_files[:5])}"
                if len(changed_files) > 5:
                    status_msg += f" and {len(changed_files) - 5} more"
            if untracked_files:
                if status_msg:
                    status_msg += "\n"
                status_msg += f"Untracked files: {', '.join(untracked_files[:5])}"
                if len(untracked_files) > 5:
                    status_msg += f" and {len(untracked_files) - 5} more"

            return True, status_msg

        return False, "No uncommitted changes"

    except Exception as e:
        return False, f"Error checking status: {str(e)}"


def stash_changes(repo_path: str) -> tuple:
    """
    Stash uncommitted changes
    Returns: (success: bool, stash_name: str or error_message)
    """
    try:
        repo = Repo(repo_path)
        from datetime import datetime

        stash_name = f"extraction_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        repo.git.stash('push', '-u', '-m', stash_name)

        return True, stash_name

    except Exception as e:
        return False, f"Error stashing changes: {str(e)}"


def checkout_branch(repo_path: str, branch_name: str) -> tuple:
    """
    Checkout to specific branch
    Returns: (success: bool, message: str)
    """
    try:
        repo = Repo(repo_path)

        # Check if branch exists locally
        if branch_name not in [ref.name for ref in repo.references]:
            # Try with origin prefix
            origin_branch = f"origin/{branch_name}"
            if origin_branch in [ref.name for ref in repo.references]:
                # Create local branch tracking remote
                repo.git.checkout('-b', branch_name, origin_branch)
                return True, f"Checked out new branch {branch_name} tracking {origin_branch}"
            else:
                return False, f"Branch {branch_name} does not exist"

        repo.git.checkout(branch_name)
        return True, f"Checked out to {branch_name}"

    except GitCommandError as e:
        return False, f"Git checkout failed: {str(e)}"
    except Exception as e:
        return False, f"Error during checkout: {str(e)}"


def pull_latest(repo_path: str) -> tuple:
    """
    Pull latest changes from remote
    Returns: (success: bool, message: str)
    """
    try:
        repo = Repo(repo_path)
        origin = repo.remotes.origin

        # Fetch first
        origin.fetch()

        # Pull with rebase to avoid merge commits
        pull_info = origin.pull()

        if pull_info:
            return True, f"Successfully pulled latest changes"
        else:
            return True, "Already up to date"

    except GitCommandError as e:
        error_msg = str(e)
        if 'CONFLICT' in error_msg or 'conflict' in error_msg:
            return False, "Pull failed: Merge conflicts detected. Please resolve manually."
        return False, f"Git pull failed: {error_msg}"
    except Exception as e:
        return False, f"Error during pull: {str(e)}"


def get_files_for_jira(repo_path: str, branch_name: str, jira_no: str, variant: str) -> dict:
    """
    Get all files committed under a Jira number in a specific branch

    Args:
        repo_path: Path to repository
        branch_name: Branch to search
        jira_no: Jira number
        variant: 'db' or 'fe' (used for filtering)

    Returns: {
        'existing_files': [(file_path, commit_sha), ...],
        'deleted_files': [(file_path, commit_sha), ...],
        'commit_count': int,
        'commits': [commit_sha, ...]
    }
    """
    try:
        repo = Repo(repo_path)

        # Escape jira number for grep
        jira_pattern = escape_jira_for_grep(jira_no)

        # Get commits with this Jira number in the specific branch
        git_log_cmd = [
            'git', 'log', branch_name,
            '--grep', jira_pattern,
            '--name-status',
            '--pretty=format:COMMIT:%H'
        ]

        result = subprocess.run(
            git_log_cmd,
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )

        if not result.stdout.strip():
            return {
                'existing_files': [],
                'deleted_files': [],
                'commit_count': 0,
                'commits': []
            }

        # Parse output
        commits = []
        file_status_map = {}  # {file_path: (status, commit_sha)}
        current_commit = None

        for line in result.stdout.split('\n'):
            line = line.strip()
            if not line:
                continue

            if line.startswith('COMMIT:'):
                current_commit = line.replace('COMMIT:', '')
                commits.append(current_commit)
            elif current_commit and '\t' in line:
                # Line format: STATUS\tFILE_PATH
                parts = line.split('\t')
                if len(parts) >= 2:
                    status = parts[0][0]  # First character (A, M, D, R, etc.)
                    file_path = parts[-1]  # Last part is the file path

                    # Skip FE files that don't have .fmb extension
                    if should_skip_fe_file(file_path, variant):
                        continue

                    # Keep only the latest status for each file
                    if file_path not in file_status_map:
                        file_status_map[file_path] = (status, current_commit)

        # Categorize files
        existing_files = []
        deleted_files = []

        for file_path, (status, commit_sha) in file_status_map.items():
            # Check if file currently exists in working tree
            file_full_path = Path(repo_path) / file_path

            if status == 'D':
                # File was deleted in this commit
                deleted_files.append((file_path, commit_sha))
            elif file_full_path.exists():
                # File exists in current state
                existing_files.append((file_path, commit_sha))
            else:
                # File doesn't exist now (deleted later or renamed)
                deleted_files.append((file_path, commit_sha))

        return {
            'existing_files': existing_files,
            'deleted_files': deleted_files,
            'commit_count': len(commits),
            'commits': commits
        }

    except subprocess.CalledProcessError as e:
        # Git command failed (likely no commits found)
        return {
            'existing_files': [],
            'deleted_files': [],
            'commit_count': 0,
            'commits': []
        }
    except Exception as e:
        raise Exception(f"Error getting files for Jira: {str(e)}")


def process_multi_variant_extraction(base_path: str, repo_variants: dict,
                                     branch_name: str, jira_no: str) -> dict:
    """
    Process extraction across multiple repository variants (db, fe)

    Args:
        base_path: Base directory path
        repo_variants: Dict from scan_repositories()
        branch_name: Branch to extract from (e.g., 'release/develop')
        jira_no: Jira number

    Returns: {
        'combined_existing_files': [(file_path, commit_sha, variant), ...],
        'combined_deleted_files': [(file_path, commit_sha, variant), ...],
        'total_commits': int,
        'variant_results': {
            'db': {...},
            'fe': {...}
        }
    }
    """
    combined_existing = []
    combined_deleted = []
    total_commits = 0
    variant_results = {}

    for variant, info in repo_variants.items():
        if not info['exists'] or not info['is_git_repo']:
            continue

        repo_path = info['path']

        # Get files for this variant
        files_info = get_files_for_jira(repo_path, branch_name, jira_no, variant)

        # Add variant information to each file tuple
        existing_with_variant = [
            (file_path, commit_sha, variant)
            for file_path, commit_sha in files_info['existing_files']
        ]

        deleted_with_variant = [
            (file_path, commit_sha, variant)
            for file_path, commit_sha in files_info['deleted_files']
        ]

        combined_existing.extend(existing_with_variant)
        combined_deleted.extend(deleted_with_variant)
        total_commits += files_info['commit_count']

        variant_results[variant] = {
            'repo_name': info['full_name'],
            'commit_count': files_info['commit_count'],
            'existing_count': len(files_info['existing_files']),
            'deleted_count': len(files_info['deleted_files'])
        }

    return {
        'combined_existing_files': combined_existing,
        'combined_deleted_files': combined_deleted,
        'total_commits': total_commits,
        'variant_results': variant_results
    }


def restore_original_branch(repo_path: str, original_branch: str, stash_name: Optional[str] = None) -> tuple:
    """
    Restore to original branch and pop stash if exists
    Returns: (success: bool, message: str)
    """
    try:
        repo = Repo(repo_path)

        # Checkout to original branch
        repo.git.checkout(original_branch)

        message = f"Restored to branch {original_branch}"

        # Pop stash if exists
        if stash_name:
            try:
                stash_list = repo.git.stash('list')
                if stash_name in stash_list:
                    repo.git.stash('pop')
                    message += f"\nRestored stashed changes"
            except Exception as e:
                message += f"\nWarning: Could not restore stash: {str(e)}"

        return True, message

    except Exception as e:
        return False, f"Error restoring state: {str(e)}"


def extract_file_from_commit(repo_path: str, commit_sha: str, file_path: str, output_path: str) -> tuple:
    """
    Extract deleted file from specific commit
    Returns: (success: bool, message: str)
    """
    try:
        # Ensure output directory exists
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        # Use git show to extract file content from commit
        git_show_cmd = ['git', 'show', f'{commit_sha}:{file_path}']

        result = subprocess.run(
            git_show_cmd,
            cwd=repo_path,
            capture_output=True,
            check=True
        )

        # Write to output file
        with open(output_path, 'wb') as f:
            f.write(result.stdout)

        return True, f"Extracted {file_path} from commit {commit_sha[:8]}"

    except subprocess.CalledProcessError as e:
        return False, f"Failed to extract {file_path}: {str(e)}"
    except Exception as e:
        return False, f"Error extracting file: {str(e)}"