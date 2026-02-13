# services/release_service.py

import yaml
from pathlib import Path
from models.release_context import ReleaseContext
from validators.drift_validator import validate_no_drift, DriftDetectedError
from validators.repo_validator import ensure_clean_working_tree

from services.git_service import (
    checkout_branch,
    create_or_checkout_branch,
    stage_all,
    commit_changes,
    push_branch,
    GitCommandError
)

# Optional: Import logger if you added utils/logger.py
try:
    from utils.logger import logger

    LOGGING_ENABLED = True
except (ImportError, ModuleNotFoundError):
    LOGGING_ENABLED = False
    logger = None  # Define logger as None when import fails


def load_file_routing() -> dict:
    """Load extension-to-folder mappings."""
    try:
        with open("config/file_routing.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f).get("mappings", {})
    except (FileNotFoundError, yaml.YAMLError):
        return {}


def execute_release(context: ReleaseContext) -> None:
    """
    Execute CIT / BFX release.
    HARD BLOCK if drift is detected.
    """

    if LOGGING_ENABLED and logger:
        logger.info(f"Starting release execution for {context.release_jira}")

    # ======================================================
    # 🔒 SAFETY GATE 1: Working tree must be clean
    # ======================================================
    ensure_clean_working_tree(context.repo_path)

    if LOGGING_ENABLED and logger:
        logger.info("Working tree is clean")

    # ======================================================
    # 🔒 SAFETY GATE 2: Drift validation (CRITICAL)
    # ======================================================
    try:
        validate_no_drift(
            repo_path=context.repo_path,
            base_branch=context.base_branch,
            approval_file=context.approval_file
        )

        if LOGGING_ENABLED and logger:
            logger.info("No drift detected")

    except DriftDetectedError as e:
        if LOGGING_ENABLED and logger:
            logger.error(f"Drift detected: {e.drifted_files}")

        raise RuntimeError(
            "❌ RELEASE BLOCKED: Approved files have drifted from base branch.\n\n"
            f"{e}"
        )

    # ======================================================
    # 🧭 Git flow
    # ======================================================
    # Checkout base branch
    checkout_branch(context.repo_path, context.base_branch)

    if LOGGING_ENABLED and logger:
        logger.info(f"Checked out base branch: {context.base_branch}")

    # Create or checkout release branch
    create_or_checkout_branch(
        repo_path=context.repo_path,
        branch_name=context.release_branch,
        base_branch=context.base_branch
    )

    if LOGGING_ENABLED and logger:
        logger.info(f"Created/checked out release branch: {context.release_branch}")

    # ======================================================
    # 📂 Apply approved files
    # ======================================================
    # ======================================================
    # 📂 Apply approved files (with intelligent routing)
    # ======================================================
    routing_map = load_file_routing()

    for rel_string in context.approved_files.keys():
        rel_path = Path(rel_string)
        src = context.shared_retro_path / rel_path
        
        # Determine destination
        # If file is in root of retro folder (no parent parts), apply routing
        if len(rel_path.parts) == 1 and rel_path.suffix in routing_map:
            target_folder = routing_map[rel_path.suffix]
            dst = context.repo_path / target_folder / rel_path.name
        else:
            # Respect existing structure
            dst = context.repo_path / rel_path

        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")

        if LOGGING_ENABLED and logger:
            logger.info(f"Applied file: {rel_path}")

    # -----------------------------
    # Commit message enforcement
    # -----------------------------
    if not context.release_jira:
        raise RuntimeError(
            "❌ Release Jira is missing. Cannot commit without BANKING Jira."
        )

    # ======================================================
    # 📦 Commit & push
    # ======================================================
    stage_all(context.repo_path)

    try:
        commit_changes(
            context.repo_path,
            message=context.release_jira
        )
        
        if LOGGING_ENABLED and logger:
            logger.info(f"Committed changes with message: {context.release_jira}")

    except GitCommandError as e:
        if "nothing to commit" in e.stdout.lower():
            if LOGGING_ENABLED and logger:
                logger.warning("Nothing to commit - release skipped.")
            
            # Raise a specific message that the UI can catch or display as a warning
            raise RuntimeWarning("⚠️ Release skipped: No changes to commit. The files match the current repository state.")
        else:
            raise e

    push_branch(
        context.repo_path,
        context.release_branch
    )

    if LOGGING_ENABLED and logger:
        logger.info(f"Pushed branch: {context.release_branch}")
        logger.info(f"Release {context.release_jira} completed successfully")

    # Mark approval as consumed after successful release
    from services.approval_service import mark_approval_consumed
    mark_approval_consumed(context.approval_file)