# analysis/sql_merge_engine.py

"""
Context-aware merge engine for SQL / PLSQL files.

Strategy for each tagged block from source:
  1. If the tag already exists in target → replace in-place.
  2. Context match → find the same surrounding lines in target, insert there.
  3. Fuzzy match → retry with whitespace-normalised lines.
  4. Fallback → append at end with a WARNING comment.
"""

from __future__ import annotations
import re
import logging
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

# Minimum similarity ratio for fuzzy line matching
FUZZY_THRESHOLD = 0.80


# ─────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────

def smart_merge(
    source_content: str,
    target_content: str,
    tagged_blocks: list[dict],
    search_tags: list[str],
) -> str:
    """
    Merge tagged blocks from source into target at the correct positions.

    Args:
        source_content: Full text of the source file.
        target_content: Full text of the target file.
        tagged_blocks:  List of TaggedBlock dicts from tag_extractor.
        search_tags:    The search tag strings (for in-place replacement detection).

    Returns:
        The merged content (target + all tagged blocks inserted correctly).
    """

    if not tagged_blocks:
        return target_content

    result_lines = target_content.splitlines()

    # Process blocks in REVERSE order so that earlier line indices stay valid
    # after we insert content further down the file.
    for block in reversed(tagged_blocks):
        result_lines = _merge_single_block(result_lines, block, search_tags)

    return "\n".join(result_lines)


# ─────────────────────────────────────────────
# Single-block merge
# ─────────────────────────────────────────────

def _merge_single_block(
    target_lines: list[str],
    block: dict,
    search_tags: list[str],
) -> list[str]:
    """Insert or replace a single tagged block in *target_lines*."""

    block_type = block["block_type"]
    content = block["content"]
    tag = block["tag"]
    ctx_above = block["context_above"]
    ctx_below = block["context_below"]

    content_lines = content.splitlines()

    # ── Strategy 1: tag already exists in target → replace ──
    existing_range = _find_existing_tag_range(target_lines, tag, block_type)
    if existing_range is not None:
        start, end = existing_range
        logger.info("Tag '%s' found in target at lines %d–%d → replacing", tag, start, end)
        return target_lines[:start] + content_lines + target_lines[end + 1:]

    # ── Strategy 2: exact context match ──
    pos = _find_by_context(target_lines, ctx_above, ctx_below, exact=True)
    if pos is not None:
        logger.info("Exact context match at line %d → inserting", pos)
        return target_lines[:pos] + content_lines + target_lines[pos:]

    # ── Strategy 3: fuzzy context match ──
    pos = _find_by_context(target_lines, ctx_above, ctx_below, exact=False)
    if pos is not None:
        logger.info("Fuzzy context match at line %d → inserting", pos)
        return target_lines[:pos] + content_lines + target_lines[pos:]

    # ── Strategy 4: try matching just the closest context line ──
    pos = _find_by_nearest_context(target_lines, ctx_above, ctx_below)
    if pos is not None:
        logger.info("Nearest-context match at line %d → inserting", pos)
        return target_lines[:pos] + content_lines + target_lines[pos:]

    # ── Strategy 5: fallback — append with warning ──
    logger.warning("No context match found for tag '%s' → appending at end", tag)
    warning = f"-- WARNING: Auto-placed by Retrofit Automation (no context match for {tag})"
    return target_lines + ["", warning] + content_lines


# ─────────────────────────────────────────────
# Strategy 1: find existing tag block in target
# ─────────────────────────────────────────────

def _find_existing_tag_range(
    lines: list[str],
    tag: str,
    block_type: str,
) -> tuple[int, int] | None:
    """
    If the target already contains the tag, return (start, end) line indices.
    For BLOCK type → find STARTS…ENDS.
    For INLINE type → find the single line containing the tag.
    """
    tag_esc = re.escape(tag)

    if block_type == "BLOCK":
        start_re = re.compile(rf"^--\s*{tag_esc}.*(?:starts?|begins?)", re.IGNORECASE)
        end_re = re.compile(rf"^--\s*{tag_esc}.*(?:ends?)", re.IGNORECASE)

        for i, line in enumerate(lines):
            if start_re.match(line.strip()):
                for j in range(i + 1, len(lines)):
                    if end_re.match(lines[j].strip()):
                        return (i, j)
        return None

    # INLINE
    tag_re = re.compile(rf".*{tag_esc}.*", re.IGNORECASE)
    for i, line in enumerate(lines):
        if tag_re.match(line):
            return (i, i)
    return None


# ─────────────────────────────────────────────
# Strategy 2 & 3: context matching
# ─────────────────────────────────────────────

def _normalize(line: str) -> str:
    """Collapse whitespace and lowercase for fuzzy comparison."""
    return " ".join(line.split()).strip().lower()


def _lines_match(a: str, b: str, exact: bool) -> bool:
    if exact:
        return a.strip() == b.strip()
    na, nb = _normalize(a), _normalize(b)
    if na == nb:
        return True
    if not na or not nb:
        return False
    return SequenceMatcher(None, na, nb).ratio() >= FUZZY_THRESHOLD


def _find_by_context(
    target_lines: list[str],
    ctx_above: list[str],
    ctx_below: list[str],
    exact: bool,
) -> int | None:
    """
    Find an insertion point in target by matching the context lines.

    We search for consecutive context-above lines in target,
    then verify that context-below lines follow shortly after.
    The insertion point is right after the last matched above-context line.
    """
    if not ctx_above and not ctx_below:
        return None

    # Try matching using the LAST N lines of context_above (closest to block)
    # Start with the most context and shrink on failure
    for window in range(len(ctx_above), 0, -1):
        anchor_lines = ctx_above[-window:]
        pos = _find_sequence_in_target(target_lines, anchor_lines, exact)
        if pos is not None:
            insert_at = pos + len(anchor_lines)
            # Optionally verify below-context exists nearby
            if ctx_below and _verify_below_context(target_lines, insert_at, ctx_below, exact):
                return insert_at
            elif ctx_below:
                continue  # try smaller window
            else:
                return insert_at

    # If above-context fails, try below-context only
    if ctx_below:
        for window in range(len(ctx_below), 0, -1):
            anchor_lines = ctx_below[:window]
            pos = _find_sequence_in_target(target_lines, anchor_lines, exact)
            if pos is not None:
                return pos  # insert BEFORE the below-context

    return None


def _find_sequence_in_target(
    target_lines: list[str],
    sequence: list[str],
    exact: bool,
) -> int | None:
    """Find where *sequence* occurs in *target_lines*. Returns start index or None."""
    if not sequence:
        return None

    seq_len = len(sequence)
    for i in range(len(target_lines) - seq_len + 1):
        if all(
            _lines_match(target_lines[i + j], sequence[j], exact)
            for j in range(seq_len)
        ):
            return i
    return None


def _verify_below_context(
    target_lines: list[str],
    start: int,
    ctx_below: list[str],
    exact: bool,
) -> bool:
    """Check that at least the first below-context line appears near *start*."""
    search_window = min(start + 15, len(target_lines))
    for i in range(start, search_window):
        if _lines_match(target_lines[i], ctx_below[0], exact):
            return True
    return False


# ─────────────────────────────────────────────
# Strategy 4: nearest single-context-line match
# ─────────────────────────────────────────────

def _find_by_nearest_context(
    target_lines: list[str],
    ctx_above: list[str],
    ctx_below: list[str],
) -> int | None:
    """
    Last-resort context: match just the single nearest line above or below.
    """
    # Try last line of above-context
    if ctx_above:
        nearest = ctx_above[-1]
        for i, tl in enumerate(target_lines):
            if _lines_match(tl, nearest, exact=False):
                return i + 1

    # Try first line of below-context
    if ctx_below:
        nearest = ctx_below[0]
        for i, tl in enumerate(target_lines):
            if _lines_match(tl, nearest, exact=False):
                return i

    return None
