# analysis/file_copier.py

from pathlib import Path
import shutil
import re


def merge_tagged_blocks(
    original_content: str,
    tagged_content: str,
    search_tag: str
) -> str:
    """
    Replace existing tagged section in UAT with DEV tagged content.
    If no tagged section exists, append safely at the end.

    This preserves all unrelated UAT logic.
    """

    tag = re.escape(search_tag)

    # Match:
    # 1) Block style:
    #    -- BANKING-xxxx changes starts
    #    ...
    #    -- BANKING-xxxx changes ends
    #
    # 2) Single-line style:
    #    anything containing the search tag

    tag_pattern = re.compile(
        rf"""
        (
            --\s*{tag}.*?(?:starts?|begins?).*?
            --\s*{tag}.*?(?:ends?)
        |
            ^.*{tag}.*$
        )
        """,
        re.IGNORECASE | re.DOTALL | re.MULTILINE | re.VERBOSE
    )

    # Replace in place if tag already exists in UAT
    if tag_pattern.search(original_content):
        return tag_pattern.sub(tagged_content, original_content, count=1)

    # Fallback: append safely at end
    return original_content.rstrip() + "\n\n" + tagged_content + "\n"


def apply_retrofit(
    uat_file_path: Path | None,
    retrofit_result: dict,
    retro_review_dir: Path,
    search_tag: str
):
    """
    Apply retrofit result to UAT file (APPLY mode)
    Always write a copy into Retro review folder
    """

    retrofit_type = retrofit_result["retrofit_type"]
    content_to_apply = retrofit_result["content_to_apply"]
    unit_name = retrofit_result["unit_name"]

    # -----------------------------
    # Always write Retro review copy
    # -----------------------------
    retro_review_dir.mkdir(parents=True, exist_ok=True)
    retro_file = retro_review_dir / unit_name
    retro_file.write_text(content_to_apply, errors="ignore")

    # -----------------------------
    # VALIDATE mode → stop here
    # -----------------------------
    if uat_file_path is None:
        return

    uat_file_path.parent.mkdir(parents=True, exist_ok=True)

    # -----------------------------
    # NEW UNIT → full overwrite
    # -----------------------------
    if retrofit_type == "NEW_UNIT":
        uat_file_path.write_text(content_to_apply, errors="ignore")
        shutil.copy2(uat_file_path, retro_file)
        return

    # -----------------------------
    # NORMAL → merge or overwrite
    # -----------------------------
    if retrofit_type == "NORMAL":

        if not uat_file_path.exists():
            raise RuntimeError(
                f"UAT file missing for NORMAL retrofit: {uat_file_path}"
            )

        original_content = uat_file_path.read_text(errors="ignore")

        if retrofit_result.get("merge_required", True):
            # ✅ SAFE PATH: replace tagged section in-place
            final_content = merge_tagged_blocks(
                original_content=original_content,
                tagged_content=content_to_apply,
                search_tag=search_tag
            )
        else:
            # ⚠ Explicit FULL_OBJECT_CHANGE
            final_content = content_to_apply

        uat_file_path.write_text(final_content, errors="ignore")
        shutil.copy2(uat_file_path, retro_file)
        return

    # -----------------------------
    # Safety net
    # -----------------------------
    raise ValueError(f"Unsupported retrofit_type: {retrofit_type}")
