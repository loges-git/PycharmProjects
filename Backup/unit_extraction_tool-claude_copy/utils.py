"""
Utility functions for validation and file operations
"""

import re
import os
from pathlib import Path
from config import REPOS, REPO_VARIANTS, JIRA_REGEX_PATTERN, FE_FILE_EXTENSION


def validate_jira_number(jira_no: str) -> tuple:
    """
    Validate Jira number format (e.g., BANKING-123456)
    Returns: (is_valid: bool, message: str)
    """
    if not jira_no or jira_no.strip() == '':
        return False, "Jira number cannot be empty"

    pattern = f'^{JIRA_REGEX_PATTERN}$'
    if re.match(pattern, jira_no.strip()):
        return True, "Valid"
    else:
        return False, "Invalid format. Expected format: PROJECT-12345 (e.g., BANKING-123456)"


def validate_path(path: str, should_exist: bool = True) -> tuple:
    """
    Validate if path exists and is accessible
    Returns: (is_valid: bool, message: str)
    """
    if not path or path.strip() == '':
        return False, "Path cannot be empty"

    path_obj = Path(path)

    if should_exist:
        if not path_obj.exists():
            return False, f"Path does not exist: {path}"
        if not os.access(path, os.R_OK):
            return False, f"Path is not readable: {path}"
    else:
        # For output path, check if parent exists and is writable
        parent = path_obj.parent
        if not parent.exists():
            return False, f"Parent directory does not exist: {parent}"
        if not os.access(parent, os.W_OK):
            return False, f"Parent directory is not writable: {parent}"

    return True, "Valid"


def scan_repositories(base_path: str, logical_repo: str) -> dict:
    """
    Scan base path to find all variants of a logical repository

    Flexible naming pattern:
    - Must contain the logical_repo name (e.g., 'ssa')
    - Must end with .db or .fe

    Examples:
    - 40006.ssa.db
    - 41234.git.ssa.db
    - ssa.fe
    - project_ssa_db (if ends with _db)

    Args:
        base_path: Base directory where repos are stored
        logical_repo: Logical repo name (e.g., 'ssa', 'mena')

    Returns: {
        'db': {
            'full_name': '40006.ssa.db',
            'path': '/path/to/40006.ssa.db',
            'exists': True,
            'is_git_repo': True
        },
        'fe': {
            'full_name': '41234.git.ssa.fe',
            'path': '/path/to/41234.git.ssa.fe',
            'exists': True,
            'is_git_repo': True
        }
    }
    """
    base_path_obj = Path(base_path)
    found_repos = {}

    if not base_path_obj.exists():
        return found_repos

    # Scan directory
    for item in base_path_obj.iterdir():
        if not item.is_dir():
            continue

        dir_name = item.name.lower()

        # Check if directory name contains the logical repo
        if logical_repo.lower() not in dir_name:
            continue

        # Determine variant based on suffix
        variant = None
        if dir_name.endswith('.db') or dir_name.endswith('_db'):
            variant = 'db'
        elif dir_name.endswith('.fe') or dir_name.endswith('_fe'):
            variant = 'fe'

        if variant:
            # Check if it's a valid git repo
            is_git_repo = (item / '.git').exists()

            found_repos[variant] = {
                'full_name': item.name,
                'path': str(item),
                'exists': True,
                'is_git_repo': is_git_repo
            }

    return found_repos


def get_all_repo_variants(base_path: str) -> dict:
    """
    Get all repository variants for all logical repos

    Returns: {
        'ssa': {
            'db': {...},
            'fe': {...}
        },
        'mena': {
            'db': {...}
        },
        ...
    }
    """
    all_repos = {}

    for logical_repo in REPOS:
        variants = scan_repositories(base_path, logical_repo)
        if variants:
            all_repos[logical_repo] = variants

    return all_repos


def format_repo_display(repo_variants: dict) -> str:
    """
    Format repository variants for display

    Args:
        repo_variants: Dict from scan_repositories()

    Returns:
        "40006.ssa.db, 40006.ssa.fe" or "40006.ssa.db only" etc.
    """
    if not repo_variants:
        return "Not found"

    names = [v['full_name'] for v in repo_variants.values() if v['exists']]
    return ', '.join(names) if names else "Not found"


def validate_repo_variants(repo_variants: dict) -> tuple:
    """
    Validate that repo variants are valid git repositories

    Returns: (is_valid: bool, message: str)
    """
    if not repo_variants:
        return False, "No repository variants found"

    invalid_repos = []
    for variant, info in repo_variants.items():
        if not info['is_git_repo']:
            invalid_repos.append(info['full_name'])

    if invalid_repos:
        return False, f"Not valid git repositories: {', '.join(invalid_repos)}"

    return True, "All variants are valid"


def should_skip_fe_file(file_path: str, variant: str) -> bool:
    """
    Check if a file from FE repo should be skipped

    In FE repo, only .fmb files are valid. Skip all other extensions.
    In DB repo, all files are valid.

    Args:
        file_path: Path to the file
        variant: 'db' or 'fe'

    Returns: True if file should be skipped, False otherwise
    """
    if variant != 'fe':
        return False

    # For FE repo, only accept .fmb files
    return not file_path.lower().endswith(FE_FILE_EXTENSION)


def create_output_structure(output_path: str, jira_no: str, branches: list) -> dict:
    """
    Create folder structure for extraction
    Returns: {
        'base': '/path/to/BANKING-123456',
        'CIT': '/path/to/BANKING-123456/CIT',
        'CIT_DELETED': '/path/to/BANKING-123456/CIT/deleted_files',
        ...
    }
    """
    base_path = Path(output_path) / jira_no
    base_path.mkdir(parents=True, exist_ok=True)

    folder_structure = {'base': str(base_path)}

    for branch_key in branches:
        branch_path = base_path / branch_key
        branch_path.mkdir(exist_ok=True)
        folder_structure[branch_key] = str(branch_path)

        # Create deleted_files subfolder
        deleted_path = branch_path / 'deleted_files'
        deleted_path.mkdir(exist_ok=True)
        folder_structure[f'{branch_key}_DELETED'] = str(deleted_path)

    return folder_structure


def escape_jira_for_grep(jira_no: str) -> str:
    """
    Convert BANKING-123456 to pattern for git grep
    Matches both (BANKING-123456) and BANKING-123456
    """
    # Escape special characters for grep
    escaped = re.escape(jira_no)
    return escaped


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def create_no_commits_file(folder_path: str, branch_name: str, jira_no: str):
    """Create a README file when no commits are found"""
    readme_path = Path(folder_path) / 'NO_COMMITS_FOUND.txt'
    with open(readme_path, 'w') as f:
        f.write(f"No commits found for {jira_no} in branch {branch_name}\n")
        f.write(f"\nThis means:\n")
        f.write(f"- No files were committed with {jira_no} in the commit message on this branch\n")
        f.write(f"- Files may exist in this branch but were committed under a different Jira\n")
        f.write(f"- Or this Jira's changes haven't been merged to this branch yet\n")