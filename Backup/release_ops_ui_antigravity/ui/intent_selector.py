# ui/intent_selector.py

import streamlit as st

from models.release_context import Intent, ReleaseContext


def render_intent_selector(context: ReleaseContext) -> None:
    """
    Step 1 UI: User intent selection.
    """

    st.header("What would you like to do?")

    if context.intent is not None:
        st.info(f"Selected intent: {context.intent.value}")
        if st.button("Reset / Start Over"):
            st.session_state.clear()
            st.rerun()
        return

    st.markdown("""
    <div style="margin-bottom: 2rem;">
        Choose an action to proceed:
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="ui-card">
            <div class="ui-card-header">🚀 Release Operations</div>
            <p style="color:var(--text-secondary); margin-bottom:1.5rem;">
                Execute releases to CIT (UAT) or BFX (Pre-Prod). 
                Upload changed files, validate drift, and deploy.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Start Release Flow", use_container_width=True):
            context.intent = Intent.RELEASE
            st.rerun()

    with col2:
        st.markdown("""
        <div class="ui-card">
            <div class="ui-card-header">🧰 Repo Manager</div>
            <p style="color:var(--text-secondary); margin-bottom:1.5rem;">
                Clone new repositories or refresh existing ones.
                Manage local git configurations.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Open Repo Manager", use_container_width=True):
            context.intent = Intent.REPO_MANAGER
            st.rerun()
