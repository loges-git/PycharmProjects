# analysis/tag_extractor.py

from pathlib import Path
import re


def extract_tagged_changes(
    dev_file_path: Path,
    search_tag: str,
    uat_file_exists: bool
) -> dict:
    """
    Extract ONLY tagged changes from DEV file.

    Returns:
    {
        retrofit_type: NEW_UNIT | NORMAL | SKIPPED
        content: str                      # tagged content only OR full file for NEW_UNIT
        is_full_object_change: bool
    }
    """

    dev_content = dev_file_path.read_text(errors="ignore")

    # -----------------------------
    # NEW UNIT
    # -----------------------------
    if not uat_file_exists and search_tag in dev_content:
        return {
            "retrofit_type": "NEW_UNIT",
            "content": dev_content,
            "is_full_object_change": True
        }

    # -----------------------------
    # Explicit FULL OBJECT override
    # -----------------------------
    is_full_object_change = (
        f"{search_tag} FULL_OBJECT_CHANGE" in dev_content
    )

    # -----------------------------
    # Extract tagged blocks / lines
    # -----------------------------
    tag = re.escape(search_tag)
    extracted = []

    # Block style
    block_pattern = re.compile(
        rf"--\s*{tag}.*?STARTS.*?\n(.*?)\n--\s*{tag}.*?ENDS",
        re.IGNORECASE | re.DOTALL
    )

    extracted.extend(m.group(1).strip() for m in block_pattern.finditer(dev_content))

    # Inline style
    inline_pattern = re.compile(rf"^.*{tag}.*$", re.IGNORECASE | re.MULTILINE)
    extracted.extend(inline_pattern.findall(dev_content))

    if not extracted:
        return {
            "retrofit_type": "SKIPPED",
            "content": "",
            "is_full_object_change": False
        }

    # Deduplicate
    unique_content = "\n".join(dict.fromkeys(extracted))

    return {
        "retrofit_type": "NORMAL",
        "content": unique_content,
        "is_full_object_change": is_full_object_change
    }
