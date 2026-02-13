# ui/intent_selector.py

import streamlit as st

from models.release_context import Intent, ReleaseContext


def render_intent_selector(context: ReleaseContext) -> None:
    """
    Step 1 UI: User intent selection with modern card design.
    """

    st.header("What would you like to do?")

    if context.intent is not None:
        st.info(f"✨ Selected intent: **{context.intent.value}**")
        if st.button("🔄 Reset / Start Over", key="reset_intent"):
            st.session_state.clear()
            st.rerun()
        return

    st.markdown("""
    <p style="color: var(--text-secondary); font-size: 1.1rem; margin-bottom: 2rem;">
        Choose an action to get started:
    </p>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="ui-card" style="min-height: 220px;">
            <div style="text-align: center; margin-bottom: 1rem;">
                <span style="font-size: 3rem; display: block; margin-bottom: 0.5rem;">🚀</span>
            </div>
            <div class="ui-card-header" style="justify-content: center;">
                Release Operations
            </div>
            <p style="color: var(--text-secondary); text-align: center; font-size: 0.95rem; line-height: 1.6;">
                Execute releases to <strong>CIT</strong> (UAT) or <strong>BFX</strong> (Pre-Prod). 
                Upload changed files, validate drift, and deploy.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Start Release Flow", use_container_width=True, type="primary"):
            context.intent = Intent.RELEASE
            st.rerun()

    with col2:
        st.markdown("""
        <div class="ui-card" style="min-height: 220px;">
            <div style="text-align: center; margin-bottom: 1rem;">
                <span style="font-size: 3rem; display: block; margin-bottom: 0.5rem;">🧰</span>
            </div>
            <div class="ui-card-header" style="justify-content: center;">
                Repo Manager
            </div>
            <p style="color: var(--text-secondary); text-align: center; font-size: 0.95rem; line-height: 1.6;">
                Clone new repositories or refresh existing ones.
                Manage local git configurations.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🧰 Open Repo Manager", use_container_width=True, type="secondary"):
            context.intent = Intent.REPO_MANAGER
            st.rerun()
