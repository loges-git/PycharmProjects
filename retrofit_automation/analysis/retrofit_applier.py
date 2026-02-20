# analysis/retrofit_applier.py

"""
Writes retrofitted content to the Retro review folder.
Never writes to source or target directories.
"""

from __future__ import annotations
from pathlib import Path
import logging

from analysis.tag_extractor import extract_tagged_blocks, content_has_any_tag
from analysis.sql_merge_engine import smart_merge

logger = logging.getLogger(__name__)


def retrofit_file(
    source_content: str,
    target_content: str | None,
    search_tags: list[str],
    retro_file_path: Path,
) -> dict:
    """
    Perform a single-file retrofit.

    Args:
        source_content:  Full text of the source file (contains tagged changes).
        target_content:  Full text of the target file, or None if it's a new unit.
        search_tags:     Tags to search for.
        retro_file_path: Where to write the retrofitted result.

    Returns:
        {
            "retrofit_type": "NEW_UNIT" | "MERGED",
            "blocks_found": int,
            "retro_path": Path,
        }
    """

    retro_file_path.parent.mkdir(parents=True, exist_ok=True)

    # ── New unit (file doesn't exist in target) ──
    if target_content is None:
        retro_file_path.write_text(source_content, errors="ignore")
        return {
            "retrofit_type": "NEW_UNIT",
            "blocks_found": 0,
            "retro_path": retro_file_path,
        }

    # ── Extract tagged blocks from source ──
    tagged_blocks = extract_tagged_blocks(source_content, search_tags)

    if not tagged_blocks:
        logger.info("No tagged blocks found in source — skipping")
        return {
            "retrofit_type": "SKIPPED",
            "blocks_found": 0,
            "retro_path": retro_file_path,
        }

    # ── Smart merge ──
    merged = smart_merge(
        source_content=source_content,
        target_content=target_content,
        tagged_blocks=tagged_blocks,
        search_tags=search_tags,
    )

    retro_file_path.write_text(merged, errors="ignore")

    return {
        "retrofit_type": "MERGED",
        "blocks_found": len(tagged_blocks),
        "retro_path": retro_file_path,
    }
