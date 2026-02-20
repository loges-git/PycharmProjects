# analysis/tag_extractor.py

from __future__ import annotations
import re
import logging

logger = logging.getLogger(__name__)

# Number of context lines to capture above/below each tagged block
CONTEXT_LINES = 10


def _normalize(line: str) -> str:
    """Normalize a line for fuzzy comparison (strip + collapse whitespace)."""
    return " ".join(line.split()).strip()


def extract_tagged_blocks(
    content: str,
    search_tags: list[str],
) -> list[dict]:
    """
    Extract all tagged blocks and inline tags from *content*.

    Each search tag may appear as:
      • Block style:  -- <tag> ... STARTS  …  -- <tag> ... ENDS
      • Inline style: any line containing <tag> that is NOT a block marker

    Returns a list of dicts:
    {
        "block_type":    "BLOCK" | "INLINE",
        "content":       str,           # the tagged content (with markers for BLOCK, full line for INLINE)
        "context_above": list[str],     # N source lines above the block
        "context_below": list[str],     # N source lines below the block
        "tag":           str,           # which tag matched
        "start_line":    int,           # 0-indexed line number in source
        "end_line":      int,           # 0-indexed line number in source (inclusive)
    }
    """

    lines = content.splitlines()
    blocks: list[dict] = []
    consumed_lines: set[int] = set()  # line indices already part of a block

    for tag in search_tags:
        tag_escaped = re.escape(tag)

        # --- 1. Block tags (STARTS … ENDS) ---
        block_start_re = re.compile(
            rf"^--\s*{tag_escaped}.*(?:starts?|begins?)",
            re.IGNORECASE,
        )
        block_end_re = re.compile(
            rf"^--\s*{tag_escaped}.*(?:ends?)",
            re.IGNORECASE,
        )

        i = 0
        while i < len(lines):
            if i in consumed_lines:
                i += 1
                continue

            if block_start_re.match(lines[i].strip()):
                start_idx = i
                j = i + 1
                while j < len(lines):
                    if block_end_re.match(lines[j].strip()):
                        end_idx = j
                        block_content = "\n".join(lines[start_idx : end_idx + 1])

                        ctx_above = _context_lines(lines, 0, start_idx, consumed_lines)
                        ctx_below = _context_lines_below(lines, end_idx, consumed_lines)

                        blocks.append({
                            "block_type": "BLOCK",
                            "content": block_content,
                            "context_above": ctx_above,
                            "context_below": ctx_below,
                            "tag": tag,
                            "start_line": start_idx,
                            "end_line": end_idx,
                        })

                        for k in range(start_idx, end_idx + 1):
                            consumed_lines.add(k)
                        i = end_idx + 1
                        break
                    j += 1
                else:
                    # No matching END found — treat start line as inline
                    i += 1
                continue
            i += 1

        # --- 2. Inline tags (single lines containing the tag, not already consumed) ---
        inline_re = re.compile(rf".*{tag_escaped}.*", re.IGNORECASE)

        for i, line in enumerate(lines):
            if i in consumed_lines:
                continue
            if inline_re.match(line):
                ctx_above = _context_lines(lines, 0, i, consumed_lines)
                ctx_below = _context_lines_below(lines, i, consumed_lines)

                blocks.append({
                    "block_type": "INLINE",
                    "content": line,
                    "context_above": ctx_above,
                    "context_below": ctx_below,
                    "tag": tag,
                    "start_line": i,
                    "end_line": i,
                })
                consumed_lines.add(i)

    # Sort blocks by their position in the file (important for sequential insertion)
    blocks.sort(key=lambda b: b["start_line"])
    return blocks


def _context_lines(
    lines: list[str],
    range_start: int,
    block_start: int,
    consumed: set[int],
) -> list[str]:
    """Return up to CONTEXT_LINES non-consumed, non-empty lines above *block_start*."""
    result = []
    idx = block_start - 1
    while idx >= range_start and len(result) < CONTEXT_LINES:
        if idx not in consumed and lines[idx].strip():
            result.append(lines[idx])
        idx -= 1
    result.reverse()
    return result


def _context_lines_below(
    lines: list[str],
    block_end: int,
    consumed: set[int],
) -> list[str]:
    """Return up to CONTEXT_LINES non-consumed, non-empty lines below *block_end*."""
    result = []
    idx = block_end + 1
    while idx < len(lines) and len(result) < CONTEXT_LINES:
        if idx not in consumed and lines[idx].strip():
            result.append(lines[idx])
        idx += 1
    return result


def content_has_any_tag(content: str, search_tags: list[str]) -> bool:
    """Quick check: does content contain at least one of the search tags?"""
    content_upper = content.upper()
    return any(tag.upper() in content_upper for tag in search_tags)
