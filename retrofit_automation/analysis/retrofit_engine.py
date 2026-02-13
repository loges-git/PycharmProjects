# analysis/retrofit_engine.py

def build_retro_content(file_analysis: dict) -> dict:
    """
    Build final retrofit payload.

    REQUIRED input keys:
    {
        "retrofit_type": "NEW_UNIT" | "NORMAL",
        "content": str,
        "unit_name": str,
        "is_full_object_change": bool   # OPTIONAL, defaults to False
    }

    RETURNS:
    {
        "retrofit_type": str,
        "content_to_apply": str,
        "unit_name": str,
        "merge_required": bool
    }
    """

    # -----------------------------
    # Mandatory fields
    # -----------------------------
    retrofit_type = file_analysis.get("retrofit_type")
    content = file_analysis.get("content")
    unit_name = file_analysis.get("unit_name")

    if retrofit_type is None:
        raise KeyError("retrofit_type missing in file_analysis")

    if content is None:
        raise KeyError("content missing in file_analysis")

    if unit_name is None:
        raise KeyError("unit_name missing in file_analysis")

    # -----------------------------
    # NEW UNIT → full overwrite
    # -----------------------------
    if retrofit_type == "NEW_UNIT":
        return {
            "retrofit_type": "NEW_UNIT",
            "content_to_apply": content,
            "unit_name": unit_name,
            "merge_required": False
        }

    # -----------------------------
    # NORMAL RETROFIT
    # -----------------------------
    if retrofit_type == "NORMAL":
        is_full_object_change = file_analysis.get(
            "is_full_object_change",
            False
        )

        return {
            "retrofit_type": "NORMAL",
            "content_to_apply": content,
            "unit_name": unit_name,
            # 🔑 CRITICAL FIX:
            # Merge unless explicitly marked FULL_OBJECT_CHANGE
            "merge_required": not is_full_object_change
        }

    # -----------------------------
    # Unsupported state
    # -----------------------------
    raise ValueError(f"Unsupported retrofit_type: {retrofit_type}")
