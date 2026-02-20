import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def create_retro_workspace(reference_name: str) -> dict:
    """
    Creates review workspace on Desktop:

    Retro_auto/
        <reference_name>/
            Source/
            Target/
            Retro/
    """

    reference_name = reference_name.strip()
    if not reference_name:
        raise ValueError("Reference name cannot be empty")

    # Windows-safe folder name (replace chars not allowed in folder names)
    folder_name = reference_name.replace("/", "-").replace("\\", "-")

    base_path = Path.home() / "Desktop" / "Retro_auto" / folder_name
    base_path.mkdir(parents=True, exist_ok=True)

    source_dir = base_path / "Source"
    target_dir = base_path / "Target"
    retro_dir = base_path / "Retro"

    source_dir.mkdir(exist_ok=True)
    target_dir.mkdir(exist_ok=True)
    retro_dir.mkdir(exist_ok=True)

    logger.info("Review workspace created at: %s", base_path)

    return {
        "base": base_path,
        "source": source_dir,
        "target": target_dir,
        "retro": retro_dir,
    }
