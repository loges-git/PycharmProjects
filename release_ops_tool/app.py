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
from ui.chat_interface import render_chat_interface
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

    # Global controls (always visible)
    render_debug_toggle(context)
    render_global_reset()

    # =========================================================
    # MODE SELECTION
    # =========================================================
    if "ui_mode" not in st.session_state:
        st.session_state.ui_mode = None  # Not yet selected

    # Show mode selection if not yet chosen
    if st.session_state.ui_mode is None:
        st.markdown("---")
        st.markdown("## 🎯 How would you like to proceed?")
        st.markdown("""
        <p style="color: var(--text-secondary); font-size: 1.05rem; margin-bottom: 2rem;">
            Select your preferred way to interact with the release platform:
        </p>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="ui-card" style="min-height: 280px; text-align: center;">
                <div style="margin-bottom: 1.5rem;">
                    <span style="font-size: 4rem; display: block;">🤖</span>
                </div>
                <div style="font-family: 'Poppins', sans-serif; font-size: 1.4rem; font-weight: 700; 
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                            margin-bottom: 0.75rem;">
                    ChatBot Mode
                </div>
                <p style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.7; margin-bottom: 1rem;">
                    Use <strong>natural language</strong> to execute releases instantly.
                </p>
                <p style="color: var(--text-muted); font-size: 0.85rem; font-style: italic;">
                    "Release BANKING-123 to CIT on SSA"
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🚀 Start with ChatBot", use_container_width=True, type="primary", key="mode_chat"):
                st.session_state.ui_mode = "CHATBOT"
                st.rerun()
        
        with col2:
            st.markdown("""
            <div class="ui-card" style="min-height: 280px; text-align: center;">
                <div style="margin-bottom: 1.5rem;">
                    <span style="font-size: 4rem; display: block;">🖱️</span>
                </div>
                <div style="font-family: 'Poppins', sans-serif; font-size: 1.4rem; font-weight: 700; 
                            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                            margin-bottom: 0.75rem;">
                    Manual UI Mode
                </div>
                <p style="color: var(--text-secondary); font-size: 0.95rem; line-height: 1.7; margin-bottom: 1rem;">
                    Use <strong>guided forms</strong> and dropdowns for precision.
                </p>
                <p style="color: var(--text-muted); font-size: 0.85rem; font-style: italic;">
                    Step-by-step workflow with validation
                </p>
            </div>
            """, unsafe_allow_html=True)
            if st.button("📋 Start with Manual UI", use_container_width=True, type="secondary", key="mode_manual"):
                st.session_state.ui_mode = "MANUAL"
                st.rerun()
        
        st.stop()  # Don't render anything else until mode is selected

    # =========================================================
    # CHATBOT MODE
    # =========================================================
    if st.session_state.ui_mode == "CHATBOT":
        st.markdown("---")
        
        # Switch mode button
        if st.button("🔄 Switch to Manual UI", key="switch_to_manual"):
            st.session_state.ui_mode = "MANUAL"
            st.rerun()
        
        render_chat_interface(context)
        st.stop()  # Don't show manual UI

    # =========================================================
    # MANUAL UI MODE
    # =========================================================
    if st.session_state.ui_mode == "MANUAL":
        st.markdown("---")
        
        # Switch mode button
        if st.button("🔄 Switch to ChatBot", key="switch_to_chatbot"):
            st.session_state.ui_mode = "CHATBOT"
            st.rerun()

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