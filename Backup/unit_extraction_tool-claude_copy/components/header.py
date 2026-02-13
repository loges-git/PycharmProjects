"""
Header component for the application
"""

import streamlit as st


def render_header():
    """Render the application header"""
    col_title, col_icon = st.columns([4, 1])

    with col_title:
        st.markdown("<h1>💎 Unit Extraction Tool</h1>", unsafe_allow_html=True)
        st.markdown(
            "<p style='font-size: 1.1rem; color: #b0b0b0; margin-top: -1rem;'>"
            "Extract units committed under a Jira number with elegance and precision"
            "</p>",
            unsafe_allow_html=True
        )

    with col_icon:
        st.markdown("""
            <div style='text-align: right; padding-top: 1rem;'>
                <div style='font-size: 4rem; opacity: 0.3;'>🚀</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)