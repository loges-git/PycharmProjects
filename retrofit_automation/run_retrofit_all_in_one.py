import streamlit as st
from pathlib import Path
import subprocess
import yaml
import re
from git_ops.safety_checks import check_working_tree_clean
from git_ops.branch_ops import create_or_reuse_feature_branch
from workspace.workspace_manager import create_retro_workspace
from analysis.tag_extractor import extract_tagged_changes
from analysis.retrofit_engine import build_retro_content
from analysis.file_copier import apply_retrofit


# -----------------------------
# Helper: run git safely
# -----------------------------
def run_git(cmd, cwd):
    result = subprocess.run(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0:
        st.error(result.stderr)
        st.stop()
    return result.stdout.strip()


# -----------------------------
# Load repo config
# -----------------------------
def load_repo_config():
    with open("config/repos.yaml", "r") as f:
        return yaml.safe_load(f)


# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Retrofit Automation", layout="wide")
st.title("🔁 Code Retrofit Automation")

mode = st.selectbox("Select Mode", ["VALIDATE", "APPLY"])

banking_no = st.text_input(
    "Enter BANKING number (for branch name)",
    placeholder="BANKING-123456"
)

search_tag = st.text_input(
    "Enter Search Tag shared by DEV team",
    placeholder="BANKING-123456 project changes"
)

config = load_repo_config()

repo_names = [k for k in config.keys() if k != "sit"]
selected_repo = st.selectbox("Select UAT Repo", repo_names)

sit_branch = st.text_input(
    "SIT Feature Branch",
    placeholder="feature/dev-team-branch"
)

start_btn = st.button("🚀 Start Retrofit")


# -----------------------------
# Main flow
# -----------------------------
if start_btn:

    if not banking_no or not search_tag or not sit_branch:
        st.error("All inputs are mandatory")
        st.stop()

    # -----------------------------
    # Validate BANKING number format
    # -----------------------------
    if not re.fullmatch(r"BANKING-\d{6}", banking_no):
        st.error("Invalid BANKING number format. Expected: BANKING-123456")
        st.stop()

    # Global SIT repo
    SIT_PATH = Path(config["sit"]["path"])

    # Selected UAT repo
    repo_cfg = config[selected_repo]
    UAT_PATH = Path(repo_cfg["path"])
    BASE_BRANCH = repo_cfg["base_branch"]
    PLATFORM = repo_cfg["platform"]

    st.markdown("### 🔍 Resolved Repository Details")
    st.info(f"""
    **SIT Path:** `{SIT_PATH}`  
    **UAT Path:** `{UAT_PATH}`  
    **Base Branch:** `{BASE_BRANCH}`  
    **Platform:** `{PLATFORM}`
    """)

    # -----------------------------
    # Safety check
    # -----------------------------
    check_working_tree_clean(UAT_PATH)

    # -----------------------------
    # Checkout SIT branch
    # -----------------------------
    run_git(["git", "checkout", sit_branch], cwd=SIT_PATH)

    # -----------------------------
    # Create / reuse UAT feature branch
    # -----------------------------
    feature_branch = create_or_reuse_feature_branch(
        repo_path=UAT_PATH,
        base_branch=BASE_BRANCH,
        banking_number=banking_no
    )

    st.success(f"Using branch: {feature_branch}")

    # -----------------------------
    # Validate branch name format
    # -----------------------------
    BRANCH_PATTERN = re.compile(
        r"^(feature|bugfix|hotfix)/BANKING-\d+([._-][a-zA-Z0-9]+)*$|^release/hotfix$"
    )

    if not BRANCH_PATTERN.fullmatch(feature_branch):
        st.error(
            "Invalid branch name format.\n\n"
            "Allowed examples:\n"
            "• feature/BANKING-123456\n"
            "• bugfix/BANKING-123456_fix\n"
            "• hotfix/BANKING-123456-ui\n"
            "• release/hotfix"
        )
        st.stop()

    # -----------------------------
    # Workspace setup
    # -----------------------------
    workspace = create_retro_workspace(banking_no)
    DEV_DIR = workspace["dev"]
    CIT_DIR = workspace["cit"]
    RETRO_DIR = workspace["retro"]

    # -----------------------------
    # Scan SIT repo
    # -----------------------------
    sit_files = [
        p for p in SIT_PATH.rglob("*")
        if p.is_file() and p.suffix.lower() == ".sql"
    ]

    retrofit_count = 0

    for dev_file in sit_files:

        relative_path = dev_file.relative_to(SIT_PATH)
        uat_file = UAT_PATH / relative_path

        dev_content = dev_file.read_text(errors="ignore")

        # 🔍 Explicit search-tag filter
        if search_tag not in dev_content:
            continue

        # -----------------------------
        # Copy DEV and CIT for review
        # -----------------------------
        dev_target = DEV_DIR / relative_path
        dev_target.parent.mkdir(parents=True, exist_ok=True)
        dev_target.write_text(dev_content, errors="ignore")

        if uat_file.exists():
            cit_target = CIT_DIR / relative_path
            cit_target.parent.mkdir(parents=True, exist_ok=True)
            cit_target.write_text(
                uat_file.read_text(errors="ignore"),
                errors="ignore"
            )

        # -----------------------------
        # Extract + build retrofit
        # -----------------------------
        extract_result = extract_tagged_changes(
            dev_file_path=dev_file,
            search_tag=search_tag,
            uat_file_exists=uat_file.exists()
        )

        if extract_result["retrofit_type"] == "SKIPPED":
            continue

        # 🔑 REQUIRED by retrofit_engine
        extract_result["file_path"] = dev_file  # absolute Path
        extract_result["unit_name"] = relative_path.name

        extract_result["is_new_unit_retro"] = (
                extract_result["retrofit_type"] == "NEW_UNIT"
        )

        extract_result["has_change_block"] = (
                extract_result["retrofit_type"] == "NORMAL"
        )

        retrofit_result = build_retro_content(extract_result)
        retrofit_count += 1

        st.write(
            f"RETROFIT → {relative_path} | type={extract_result['retrofit_type']}"
        )

        # -----------------------------
        # Apply / Preview retrofit
        # -----------------------------
        apply_retrofit(
            uat_file_path=uat_file if mode == "APPLY" else None,
            retrofit_result=retrofit_result,
            retro_review_dir=RETRO_DIR / relative_path.parent,
            search_tag=search_tag
        )

    st.success(f"Units identified for retrofit: {retrofit_count}")

    # -----------------------------
    # Commit & push
    # -----------------------------
    if mode == "APPLY" and retrofit_count > 0:
        run_git(["git", "add", "."], cwd=UAT_PATH)
        run_git(
            ["git", "commit", "-m", banking_no],
            cwd=UAT_PATH
        )
        run_git(["git", "push", "-u", "origin", feature_branch], cwd=UAT_PATH)
        st.success("✅ Changes committed and pushed successfully")

    elif mode == "VALIDATE":
        st.info("VALIDATE mode: No changes applied to UAT repo")

    st.info(f"📁 Review workspace created at:\n{workspace['base']}")
