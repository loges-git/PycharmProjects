# ui/common.py

import streamlit as st

from models.release_context import Environment, ReleaseContext


def render_environment_banner(context: ReleaseContext) -> None:
    """
    Visual banner indicating selected environment with gradient badges.
    """

    if context.environment is None:
        return

    if context.environment == Environment.CIT:
        st.markdown(
            """
            <div style="margin: 1rem 0;">
                <span class="badge-cit">
                    ❄️ CIT – UAT Environment
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    elif context.environment == Environment.BFX:
        st.markdown(
            """
            <div style="margin: 1rem 0;">
                <span class="badge-bfx">
                    🔥 BFX – Pre-Prod Environment
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_environment_selector(context: ReleaseContext) -> None:
    """
    Environment selection with modern styling.
    """

    st.subheader("🌐 Select Environment")

    if context.environment is not None:
        st.success(f"✅ Environment locked: **{context.environment.value}**")
        return

    env = st.radio(
        "Choose target environment",
        options=[Environment.CIT, Environment.BFX],
        format_func=lambda x: {
            Environment.CIT: "❄️ CIT (UAT) – Staging Environment",
            Environment.BFX: "🔥 BFX (Pre-Prod) – Production Mirror"
        }[x],
        horizontal=True
    )

    if st.button("✅ Confirm Environment", type="primary"):
        context.environment = env
        st.rerun()


def render_debug_toggle(context: ReleaseContext) -> None:
    """
    Debug mode toggle with subtle styling.
    """
    col1, col2 = st.columns([6, 1])
    
    with col2:
        debug = st.checkbox("🛠 Debug", value=False, help="Enable verbose error messages")
        st.session_state["debug"] = debug


def render_global_reset() -> None:
    """
    Full application reset button.
    """

    st.divider()
    col1, col2, col3 = st.columns([4, 2, 4])
    with col2:
        if st.button("🔄 Reset All", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.rerun()
