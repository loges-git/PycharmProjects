# workspace/file_copier.py

import shutil
from pathlib import Path


def ensure_parent_dir(file_path: Path):
    """
    Ensure parent directory exists for the given file path
    """
    file_path.parent.mkdir(parents=True, exist_ok=True)


def copy_file(
    source: Path,
    destination: Path,
    overwrite: bool = False
):
    """
    Copy a single file from source to destination.

    :param source: Path to source file
    :param destination: Full destination file path
    :param overwrite: Allow to overwrite if file already exists
    """

    source = Path(source)
    destination = Path(destination)

    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source}")

    ensure_parent_dir(destination)

    if destination.exists() and not overwrite:
        raise FileExistsError(f"Destination already exists: {destination}")

    shutil.copy2(source, destination)


def copy_files_bulk(
    source_root: Path,
    destination_root: Path,
    files: list[Path],
    overwrite: bool = False
):
    """
    Copy multiple files while preserving relative folder structure.

    :param source_root: Base path of source repo/workspace
    :param destination_root: Base path of destination folder
    :param files: List of file paths (absolute or relative to source_root)
    :param overwrite: Allow to overwrite
    """

    source_root = Path(source_root)
    destination_root = Path(destination_root)

    for file_path in files:
        file_path = Path(file_path)

        # Normalize to absolute path
        if not file_path.is_absolute():
            file_path = source_root / file_path

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        relative_path = file_path.relative_to(source_root)
        destination_file = destination_root / relative_path

        copy_file(
            source=file_path,
            destination=destination_file,
            overwrite=overwrite
        )
