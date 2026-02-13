"""
File extraction and copying operations
"""

import shutil
from pathlib import Path
from git_operations import extract_file_from_commit


def copy_existing_files_multi_variant(repo_variants: dict, file_list: list, destination: str) -> tuple:
    """
    Copy files from multiple repo variants to destination
    file_list: [(file_path, commit_sha, variant), ...]
    repo_variants: Dict with variant info (from scan_repositories)

    Returns: (success_count: int, failed_files: list, copied_files: list)
    """
    success_count = 0
    failed_files = []
    copied_files = []

    for file_path, commit_sha, variant in file_list:
        try:
            # Get repo path for this variant
            if variant not in repo_variants:
                failed_files.append((file_path, f"Variant {variant} not found"))
                continue

            repo_path = repo_variants[variant]['path']
            source = Path(repo_path) / file_path

            if not source.exists():
                failed_files.append((file_path, f"File not found in {variant}"))
                continue

            # Preserve directory structure
            dest = Path(destination) / file_path
            dest.parent.mkdir(parents=True, exist_ok=True)

            # Copy file
            shutil.copy2(source, dest)
            success_count += 1
            copied_files.append({
                'file': file_path,
                'variant': variant,
                'repo': repo_variants[variant]['full_name']
            })

        except Exception as e:
            failed_files.append((file_path, f"{variant}: {str(e)}"))

    return success_count, failed_files, copied_files


def extract_deleted_files_multi_variant(repo_variants: dict, deleted_files_info: list,
                                        destination: str) -> tuple:
    """
    Extract deleted files from git history across multiple variants
    deleted_files_info: [(file_path, commit_sha, variant), ...]

    Returns: (success_count: int, failed_files: list, extracted_files: list)
    """
    success_count = 0
    failed_files = []
    extracted_files = []

    for file_path, commit_sha, variant in deleted_files_info:
        try:
            # Get repo path for this variant
            if variant not in repo_variants:
                failed_files.append((file_path, f"Variant {variant} not found"))
                continue

            repo_path = repo_variants[variant]['path']

            # Preserve directory structure
            output_path = Path(destination) / file_path
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Extract file from commit
            success, message = extract_file_from_commit(
                repo_path, commit_sha, file_path, str(output_path)
            )

            if success:
                success_count += 1
                extracted_files.append({
                    'file': file_path,
                    'variant': variant,
                    'repo': repo_variants[variant]['full_name']
                })
            else:
                failed_files.append((file_path, f"{variant}: {message}"))

        except Exception as e:
            failed_files.append((file_path, f"{variant}: {str(e)}"))

    return success_count, failed_files, extracted_files


def process_branch_extraction_multi_variant(repo_variants: dict, branch_info: dict,
                                            jira_no: str, output_folders: dict,
                                            branch_key: str) -> dict:
    """
    Complete extraction for one branch across multiple variants

    Args:
        repo_variants: Dict from scan_repositories()
        branch_info: output from process_multi_variant_extraction()
        output_folders: folder structure dict
        branch_key: 'CIT', 'BFX', or 'PROD'

    Returns: {
        'branch_key': str,
        'total_commits': int,
        'existing_count': int,
        'deleted_count': int,
        'existing_files': list,
        'deleted_files': list,
        'variant_breakdown': dict,
        'errors': list
    }
    """
    errors = []

    # Extract existing files from all variants
    existing_count = 0
    existing_files = []
    if branch_info['combined_existing_files']:
        existing_count, failed, existing_files = copy_existing_files_multi_variant(
            repo_variants,
            branch_info['combined_existing_files'],
            output_folders[branch_key]
        )
        if failed:
            errors.extend([f"Failed to copy {f[0]}: {f[1]}" for f in failed])

    # Extract deleted files from all variants
    deleted_count = 0
    deleted_files = []
    if branch_info['combined_deleted_files']:
        deleted_count, failed, deleted_files = extract_deleted_files_multi_variant(
            repo_variants,
            branch_info['combined_deleted_files'],
            output_folders[f'{branch_key}_DELETED']
        )
        if failed:
            errors.extend([f"Failed to extract {f[0]}: {f[1]}" for f in failed])

    return {
        'branch_key': branch_key,
        'total_commits': branch_info['total_commits'],
        'existing_count': existing_count,
        'deleted_count': deleted_count,
        'existing_files': existing_files,
        'deleted_files': deleted_files,
        'variant_breakdown': branch_info['variant_results'],
        'errors': errors
    }