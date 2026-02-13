"""
Input section component
"""

import streamlit as st
import time
import os
from config import REPOS, BRANCH_MAPPING
from utils import get_all_repo_variants, format_repo_display


def render_input_section():
    """Render the input configuration section"""

    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h2 style='margin-bottom: 1.5rem;'>⚙️ Configuration</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("<h3 style='font-size: 1.3rem;'>📋 Input Parameters</h3>", unsafe_allow_html=True)

        jira_number = st.text_input(
            "Jira Number",
            placeholder="BANKING-123456",
            help="Enter the Jira ticket number",
            key="jira_input"
        )

        base_path = st.text_input(
            "Base Path",
            placeholder="/home/user/repos",
            help="Root directory containing all repositories",
            key="base_path_input"
        )

        # Scan section
        st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
        col_scan, col_refresh = st.columns([3, 1])

        with col_scan:
            scan_btn = st.button("🔍 Scan Repositories", use_container_width=True, key="scan_btn")

        with col_refresh:
            if st.button("🔄", help="Refresh scan results", use_container_width=True):
                st.session_state.repo_scan_results = {}
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        if scan_btn and base_path:
            with st.spinner("🔎 Scanning repositories..."):
                time.sleep(0.5)
                st.session_state.repo_scan_results = get_all_repo_variants(base_path)

            if st.session_state.repo_scan_results:
                st.success(f"✨ Successfully found {len(st.session_state.repo_scan_results)} repositories")
            else:
                st.warning("⚠️ No repositories detected")

        # Repository selection
        st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
        repo_name = st.selectbox(
            "Select Repository",
            REPOS,
            help="Choose the logical repository",
            key="repo_select"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        # Display found variants
        _display_repo_variants(repo_name, base_path)

    with col2:
        st.markdown("<h3 style='font-size: 1.3rem;'>🎯 Extraction Options</h3>", unsafe_allow_html=True)

        # Lock output path to Desktop
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        output_path = st.text_input(
            "Output Directory",
            value=desktop_path,
            help="Destination folder (Locked to Desktop)",
            key="output_path_input",
            disabled=True
        )

        st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
        extraction_mode = st.radio(
            "Extraction Mode",
            ["Single Branch", "Multiple Branches"],
            help="Choose extraction mode",
            key="mode_select"
        )
        st.markdown("</div>", unsafe_allow_html=True)

        branches_to_extract = _get_branches_to_extract(extraction_mode)

    st.markdown("</div>", unsafe_allow_html=True)

    return jira_number, base_path, repo_name, output_path, extraction_mode, branches_to_extract


def _display_repo_variants(repo_name, base_path):
    """Display repository variant information"""
    if st.session_state.repo_scan_results and repo_name in st.session_state.repo_scan_results:
        variants = st.session_state.repo_scan_results[repo_name]
        repo_display = format_repo_display(variants)

        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.1) 100%);
                border-left: 4px solid #10b981;
                border-radius: 10px;
                padding: 1rem;
                margin-top: 1rem;
            '>
                <div style='font-size: 0.85rem; color: #6ee7b7; margin-bottom: 0.3rem; text-transform: uppercase; letter-spacing: 1px;'>
                    Found Repositories
                </div>
                <div style='font-size: 1rem; color: #ffffff; font-weight: 500;'>{repo_display}</div>
            </div>
        """, unsafe_allow_html=True)

        # Detailed info in expander
        with st.expander("📊 Detailed Repository Information", expanded=False):
            for variant, info in variants.items():
                status_icon = "✅" if info['is_git_repo'] else "❌"
                st.markdown(f"""
                    <div style='
                        background: rgba(255, 255, 255, 0.03);
                        border-radius: 8px;
                        padding: 0.8rem;
                        margin-bottom: 0.8rem;
                        border: 1px solid rgba(255, 255, 255, 0.1);
                    '>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <div>
                                <span style='font-size: 1.1rem; font-weight: 600; color: #667eea;'>{variant.upper()}</span>
                                <span style='margin-left: 1rem;'>{status_icon}</span>
                            </div>
                        </div>
                        <div style='margin-top: 0.5rem; color: #a0a0a0; font-size: 0.9rem;'>
                            <code>{info['full_name']}</code>
                        </div>
                        <div style='margin-top: 0.3rem; color: #808080; font-size: 0.85rem;'>
                            {info['path']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

    elif base_path and st.session_state.repo_scan_results:
        st.info(f"💡 Repository '{repo_name}' not detected. Please scan again.")
    else:
        st.info("💡 Enter base path and click 'Scan Repositories'")


def _get_branches_to_extract(extraction_mode):
    """Determine which branches to extract from"""
    if extraction_mode == "Single Branch":
        st.markdown("<div style='margin-top: 1rem;'>", unsafe_allow_html=True)
        selected_branch = st.selectbox(
            "Select Branch",
            list(BRANCH_MAPPING.keys()),
            format_func=lambda x: f"{x} ({BRANCH_MAPPING[x]})",
            key="branch_select"
        )
        st.markdown("</div>", unsafe_allow_html=True)
        return [selected_branch]
    else:
        branches = list(BRANCH_MAPPING.keys())
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%);
                border-left: 4px solid #3b82f6;
                border-radius: 10px;
                padding: 1rem;
                margin-top: 1rem;
            '>
                <div style='font-size: 0.85rem; color: #93c5fd; margin-bottom: 0.3rem; text-transform: uppercase; letter-spacing: 1px;'>
                    Branches to Extract
                </div>
                <div style='font-size: 1rem; color: #ffffff; font-weight: 500;'>{', '.join(branches)}</div>
            </div>
        """, unsafe_allow_html=True)
        return branches