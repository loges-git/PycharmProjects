"""
Main Streamlit Application - Luxury Edition
"""

import streamlit as st
from styles import get_custom_css
from components import render_header, render_input_section, render_results, handle_extraction

# Page configuration
st.set_page_config(
    page_title="Unit Extraction Tool",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize session state
if 'repo_scan_results' not in st.session_state:
    st.session_state.repo_scan_results = {}

if 'extraction_results' not in st.session_state:
    st.session_state.extraction_results = None

if 'original_states' not in st.session_state:
    st.session_state.original_states = {}

if 'stash_info' not in st.session_state:
    st.session_state.stash_info = {}

# Render header
render_header()

# Render input section
jira_number, base_path, repo_name, output_path, _, branches_to_extract = render_input_section()

st.markdown("<hr>", unsafe_allow_html=True)

# Action buttons
handle_extraction(jira_number, base_path, repo_name, output_path, branches_to_extract)

# Display results
if st.session_state.extraction_results:
    render_results(st.session_state.extraction_results, output_path, jira_number)

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
    <div style='text-align: center; padding: 2rem 0; color: #808080;'>
        <p style='font-size: 0.9rem; margin: 0;'>
            Unit Extraction Tool <span style='color: #667eea;'>v1.0</span>
        </p>
        <p style='font-size: 0.85rem; margin: 0.5rem 0 0 0;'>
            Crafted with 💎 for efficient Jira-based unit extraction
        </p>
    </div>
""", unsafe_allow_html=True)