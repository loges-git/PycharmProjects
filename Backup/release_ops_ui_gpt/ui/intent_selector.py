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

    intent = st.radio(
        "Choose an action",
        options=[
            Intent.RELEASE,
            Intent.REPO_MANAGER
        ],
        format_func=lambda x: {
            Intent.RELEASE: "🚀 Release (CIT / BFX)",
            Intent.REPO_MANAGER: "🧰 Repo Manager (Clone / Refresh)"
        }[x]
    )

    if st.button("Continue"):
        context.intent = intent
        st.rerun()
