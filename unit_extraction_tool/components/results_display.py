"""
Results display component - shows extraction results
"""

import streamlit as st
from pathlib import Path


def render_results(results, output_path, jira_number):
    """Render the extraction results in a beautiful format"""

    st.markdown("<hr>", unsafe_allow_html=True)

    # Results header
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; font-size: 2.5rem; margin-bottom: 2rem;'>📊 Extraction Results</h2>",
                unsafe_allow_html=True)

    # Summary metrics
    _render_summary_metrics(results)

    st.markdown("</div>", unsafe_allow_html=True)

    # Branch results
    for branch_key, branch_data in results['branches'].items():
        _render_branch_results(branch_key, branch_data, results)

    # Global errors
    if results['errors']:
        _render_global_errors(results['errors'])


def _render_summary_metrics(results):
    """Render the summary metrics section"""
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)

    with col_m1:
        st.metric("Jira Number", results['jira_number'])

    with col_m2:
        st.metric("Repository", results['repo_name'].upper())

    with col_m3:
        total_files = sum(
            branch['extraction_summary']['existing_count'] + branch['extraction_summary']['deleted_count']
            for branch in results['branches'].values()
            if branch['extraction_summary']
        )
        st.metric("Total Files", total_files)

    with col_m4:
        st.metric("Completed", results['timestamp'].split()[1])


def _render_branch_results(branch_key, branch_data, results):
    """Render results for a single branch"""
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

    summary = branch_data.get('extraction_summary')

    if summary and summary['total_commits'] > 0:
        # Branch header with gradient
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
                border-radius: 15px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                border: 1px solid rgba(102, 126, 234, 0.3);
            '>
                <h3 style='margin: 0; font-size: 1.8rem;'>{branch_key}</h3>
                <p style='margin: 0.3rem 0 0 0; color: #a0a0a0;'>{branch_data['branch_name']}</p>
            </div>
        """, unsafe_allow_html=True)

        # Metrics
        _render_branch_metrics(summary)

        # Variant breakdown
        if summary['variant_breakdown']:
            _render_variant_breakdown(summary['variant_breakdown'])

        # File lists
        _render_file_lists(summary)

        # Errors
        if summary['errors']:
            st.error("**Errors encountered:**")
            for error in summary['errors']:
                st.markdown(f"<div style='color: #fca5a5; margin-left: 1rem;'>• {error}</div>", unsafe_allow_html=True)

    else:
        # No commits found
        st.markdown(f"""
            <div style='
                background: linear-gradient(135deg, rgba(156, 163, 175, 0.1) 0%, rgba(107, 114, 128, 0.1) 100%);
                border-radius: 15px;
                padding: 2rem;
                text-align: center;
                border: 1px solid rgba(156, 163, 175, 0.2);
            '>
                <h3 style='margin: 0; font-size: 1.5rem;'>{branch_key}</h3>
                <p style='margin: 0.5rem 0 0 0; color: #9ca3af;'>No commits found for {results['jira_number']}</p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_branch_metrics(summary):
    """Render metrics for a branch"""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Commits", summary['total_commits'])

    with col2:
        st.metric("Existing Files", summary['existing_count'])

    with col3:
        st.metric("Deleted Files", summary['deleted_count'])

    with col4:
        total = summary['existing_count'] + summary['deleted_count']
        st.metric("Total", total)


def _render_variant_breakdown(variant_breakdown):
    """Render the variant breakdown section"""
    st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
    st.markdown("<h4 style='font-size: 1.1rem; color: #b0b0b0; margin-bottom: 1rem;'>Variant Breakdown</h4>",
                unsafe_allow_html=True)

    for variant, v_data in variant_breakdown.items():
        st.markdown(f"""
            <div style='
                background: rgba(255, 255, 255, 0.03);
                border-radius: 8px;
                padding: 0.8rem 1rem;
                margin-bottom: 0.5rem;
                border-left: 3px solid #667eea;
            '>
                <span style='font-weight: 600; color: #667eea;'>{variant.upper()}</span>
                <span style='color: #808080; margin-left: 0.5rem;'>({v_data['repo_name']})</span>
                <br>
                <span style='color: #a0a0a0; font-size: 0.9rem;'>
                    {v_data['commit_count']} commits • {v_data['existing_count']} existing • {v_data['deleted_count']} deleted
                </span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_file_lists(summary):
    """Render file lists (existing and deleted)"""
    # Existing files
    if summary['existing_files']:
        with st.expander(f"📄 Existing Files ({len(summary['existing_files'])})", expanded=False):
            for idx, file_info in enumerate(summary['existing_files'], 1):
                st.markdown(f"""
                    <div style='
                        padding: 0.5rem;
                        margin: 0.3rem 0;
                        background: rgba(16, 185, 129, 0.05);
                        border-radius: 6px;
                        border-left: 2px solid #10b981;
                    '>
                        <code style='color: #6ee7b7;'>{file_info['file']}</code>
                        <span style='color: #808080; font-size: 0.85rem; margin-left: 0.5rem;'>from {file_info['repo']}</span>
                    </div>
                """, unsafe_allow_html=True)

    # Deleted files
    if summary['deleted_files']:
        with st.expander(f"🗑️ Deleted Files ({len(summary['deleted_files'])})", expanded=False):
            for idx, file_info in enumerate(summary['deleted_files'], 1):
                st.markdown(f"""
                    <div style='
                        padding: 0.5rem;
                        margin: 0.3rem 0;
                        background: rgba(239, 68, 68, 0.05);
                        border-radius: 6px;
                        border-left: 2px solid #ef4444;
                    '>
                        <code style='color: #fca5a5;'>{file_info['file']}</code>
                        <span style='color: #808080; font-size: 0.85rem; margin-left: 0.5rem;'>from {file_info['repo']}</span>
                    </div>
                """, unsafe_allow_html=True)


def _render_global_errors(errors):
    """Render global errors section"""
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.error("**⚠️ Global Errors**")
    for error in errors:
        st.markdown(f"<div style='color: #fca5a5; margin-left: 1.5rem;'>• {error}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

