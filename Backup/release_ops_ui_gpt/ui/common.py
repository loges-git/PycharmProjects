# ui/common.py

import streamlit as st

from models.release_context import Environment, ReleaseContext


def render_environment_banner(context: ReleaseContext) -> None:
    """
    Visual banner indicating selected environment.
    """

    if context.environment is None:
        return

    if context.environment == Environment.CIT:
        st.markdown(
            """
            <div style="padding:10px;
                        background-color:#E3F2FD;
                        border-left:6px solid #1976D2;">
                🟦 <b>CIT – UAT Release Environment</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    elif context.environment == Environment.BFX:
        st.markdown(
            """
            <div style="padding:10px;
                        background-color:#FFF3E0;
                        border-left:6px solid #FB8C00;">
                🟧 <b>BFX – Pre-Prod Release Environment</b>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_environment_selector(context: ReleaseContext) -> None:
    """
    Environment selection with lock once chosen.
    """

    st.subheader("Select Environment")

    if context.environment is not None:
        st.info(f"Environment locked: {context.environment.value}")
        return

    env = st.radio(
        "Choose target environment",
        options=[Environment.CIT, Environment.BFX],
        format_func=lambda x: {
            Environment.CIT: "🟦 CIT (UAT)",
            Environment.BFX: "🟧 BFX (Pre-Prod)"
        }[x]
    )

    if st.button("Confirm Environment"):
        context.environment = env
        st.rerun()


def render_debug_toggle(context: ReleaseContext) -> None:
    """
    Debug mode toggle.
    """

    debug = st.checkbox("🛠 Debug Mode", value=False)

    st.session_state["debug"] = debug

    if debug:
        st.caption("Debug mode enabled – verbose errors will be shown.")


def render_global_reset() -> None:
    """
    Full application reset.
    """

    st.divider()
    if st.button("🔄 Reset Application"):
        st.session_state.clear()
        st.rerun()
