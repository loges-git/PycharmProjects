# app.py

import streamlit as st

from models.release_context import ReleaseContext, Intent
from ui.intent_selector import render_intent_selector
from ui.common import (
    render_environment_banner,
    render_environment_selector,
    render_debug_toggle,
    render_global_reset,
)
from ui.repo_manager import render_repo_manager
from ui.review_approval import render_review_approval
from ui.jira_ops import render_jira_ops
from ui.release_flow import (
    render_release_flow,
    render_cluster_selector,
    render_release_type_selector
)
from ui.styles import load_css


def get_context() -> ReleaseContext:
    """
    Retrieve or initialize ReleaseContext from session.
    """
    if "context" not in st.session_state:
        st.session_state["context"] = ReleaseContext()
    return st.session_state["context"]


def is_manager_review_link() -> bool:
    """
    Check if this is a manager review link.
    Manager links have shared_path and tag parameters.
    """
    query_params = st.query_params
    return bool(query_params.get("shared_path") and query_params.get("tag"))


def main():
    st.set_page_config(
        page_title="Release Operations UI",
        layout="wide"
    )

    # 🎨 Load Custom Design System
    load_css()

    context = get_context()

    # =========================================================
    # MANAGER REVIEW MODE (special handling for review links)
    # =========================================================
    if is_manager_review_link():
        st.title("🏦 Release Approval - Manager Review")

        # Clear any old context - manager should start fresh
        if "manager_mode_initialized" not in st.session_state:
            st.session_state.clear()
            st.session_state["context"] = ReleaseContext()
            st.session_state["manager_mode_initialized"] = True
            context = st.session_state["context"]

        # Only render the approval section
        render_review_approval(context)

        # Stop here - don't render anything else
        return

    # =========================================================
    # NORMAL RELEASE ENGINEER MODE
    # =========================================================
    st.title("🏦 Release Operations Platform")

    # Global controls
    render_debug_toggle(context)
    render_global_reset()

    st.divider()

    # Step 1: Intent selection
    render_intent_selector(context)

    # Intent not yet selected
    if context.intent is None:
        return

    # -------------------------
    # Repo Manager flow
    # -------------------------
    if context.intent == Intent.REPO_MANAGER:
        render_repo_manager()
        return

    # -------------------------
    # Release flow
    # -------------------------
    # -------------------------
    # Release Flow with Tabs
    # -------------------------
    st.markdown("### 🛠 Release Workflow")

    tab_setup, tab_approval, tab_execution = st.tabs([
        "📍 1. Setup", 
        "✅ 2. Approval", 
        "🚀 3. Execution"
    ])

    # ==========================
    # TAB 1: SETUP
    # ==========================
    with tab_setup:
        st.caption("Configure the environment, cluster, and release details.")
        
        render_environment_selector(context)
        render_environment_banner(context)

        st.divider()

        render_cluster_selector(context)
        render_release_type_selector(context)
        
        st.divider()
        
        render_jira_ops(context)

    # ==========================
    # TAB 2: APPROVAL
    # ==========================
    with tab_approval:
        st.caption("Verify and load manager approval.")
        render_review_approval(context)

    # ==========================
    # TAB 3: EXECUTION
    # ==========================
    with tab_execution:
        st.caption("Finalize and execute the release.")
        
        # Only show execution if context is ready (simple check)
        if not context.approval_file:
            st.info("ℹ️ Please complete **Setup** and **Approval** tabs first.")
            
        render_release_flow(context)


if __name__ == "__main__":
    main()