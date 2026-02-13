"""
Extraction handler component - handles the extraction process UI
"""

import streamlit as st
import os
from pathlib import Path
from datetime import datetime
import time

from config import BRANCH_MAPPING
from utils import (
    validate_jira_number,
    validate_path,
    validate_repo_variants,
    create_output_structure,
    create_no_commits_file
)
from git_operations import (
    get_current_branch,
    check_uncommitted_changes,
    stash_changes,
    checkout_branch,
    pull_latest,
    restore_original_branch,
    process_multi_variant_extraction
)
from file_extractor import process_branch_extraction_multi_variant


def handle_extraction(jira_number, base_path, repo_name, output_path, branches_to_extract):
    """Handle the extraction process with UI"""

    # Action buttons
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    col_btn1, col_btn2, col_btn3, col_spacer = st.columns([2, 2, 2, 4])

    with col_btn1:
        extract_btn = st.button("🚀 Extract Units", type="primary", use_container_width=True, key="extract_btn")

    with col_btn2:
        clear_btn = st.button("🗑️ Clear Results", use_container_width=True, key="clear_btn")

    with col_btn3:
        if st.session_state.extraction_results:
            output_folder = Path(output_path) / jira_number
            if output_folder.exists():
                if st.button("📂 Open Folder", use_container_width=True, key="open_folder_btn"):
                    os.system(f'xdg-open "{output_folder}" 2>/dev/null || open "{output_folder}" 2>/dev/null')

    st.markdown("</div>", unsafe_allow_html=True)

    # Clear results handler
    if clear_btn:
        st.session_state.extraction_results = None
        st.rerun()

    # Extraction handler
    # Extraction handler
    if extract_btn:
        output_folder = Path(output_path) / jira_number
        if output_folder.exists():
            st.session_state.confirm_overwrite = True
        else:
            _perform_extraction(jira_number, base_path, repo_name, output_path, branches_to_extract)

    # Confirmation Dialog
    if st.session_state.get('confirm_overwrite', False):
        st.markdown("<div class='glass-card' style='border-left: 4px solid #fbbf24;'>", unsafe_allow_html=True)
        st.warning(f"⚠️ **Folder '{jira_number}' already exists!**")
        st.write("Do you want to overwrite existing files? Operations unrelated to this extraction will be preserved.")
        
        col_yes, col_no = st.columns([1, 4])
        with col_yes:
            if st.button("✅ Yes, Overwrite", type="primary", use_container_width=True):
                st.session_state.confirm_overwrite = False
                _perform_extraction(jira_number, base_path, repo_name, output_path, branches_to_extract)
                st.rerun()
        
        with col_no:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.confirm_overwrite = False
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)


def _perform_extraction(jira_number, base_path, repo_name, output_path, branches_to_extract):
    """Perform the actual extraction process"""

    # Validation
    errors = _validate_inputs(jira_number, base_path, repo_name, output_path)

    if errors:
        _display_validation_errors(errors)
        return

    # Start extraction
    repo_variants = st.session_state.repo_scan_results[repo_name]
    output_folders = create_output_structure(output_path, jira_number, branches_to_extract)

    # Progress container
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.markdown("<h2>🔄 Extraction in Progress</h2>", unsafe_allow_html=True)

    progress_bar = st.progress(0)
    status_container = st.container()

    extraction_results = {
        'jira_number': jira_number,
        'repo_name': repo_name,
        'branches': {},
        'errors': [],
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    total_steps = len(branches_to_extract) * len(repo_variants) * 4
    current_step = 0

    try:
        # Save original states
        _save_original_states(repo_variants)

        # Process each branch
        for branch_idx, branch_key in enumerate(branches_to_extract):
            branch_name = BRANCH_MAPPING[branch_key]

            with status_container:
                st.markdown(f"<h3 style='color: #667eea;'>Processing {branch_key} ({branch_name})...</h3>",
                            unsafe_allow_html=True)

            branch_results = {
                'branch_name': branch_name,
                'variants_processed': {},
                'extraction_summary': None,
                'errors': []
            }

            # Check uncommitted changes (first branch only)
            if branch_idx == 0:
                if not _handle_uncommitted_changes(repo_variants, status_container):
                    st.error("❌ Extraction aborted")
                    st.stop()

            # Process each variant for this branch
            for variant, info in repo_variants.items():
                if not info['is_git_repo']:
                    continue

                repo_path = info['path']
                variant_name = info['full_name']

                # Checkout branch
                with status_container:
                    st.info(f"🔄 {branch_key}/{variant.upper()}: Checking out {branch_name}...")
                current_step += 1
                progress_bar.progress(current_step / total_steps)

                success, msg = checkout_branch(repo_path, branch_name)
                if not success:
                    _handle_critical_error(f"{variant_name}: Checkout failed - {msg}", branch_results,
                                           extraction_results)
                    return

                # Pull latest
                with status_container:
                    st.info(f"⬇️ {branch_key}/{variant.upper()}: Pulling latest changes...")
                current_step += 1
                progress_bar.progress(current_step / total_steps)

                success, msg = pull_latest(repo_path)
                if not success:
                    _handle_critical_error(f"{variant_name}: Pull failed - {msg}", branch_results, extraction_results)
                    return

                branch_results['variants_processed'][variant] = {
                    'checkout': 'Success',
                    'pull': 'Success'
                }

            # Extract files from all variants
            with status_container:
                st.info(f"📦 {branch_key}: Finding files for {jira_number}...")
            current_step += 1
            progress_bar.progress(current_step / total_steps)

            multi_variant_files = process_multi_variant_extraction(
                base_path, repo_variants, branch_name, jira_number
            )

            with status_container:
                st.info(f"💾 {branch_key}: Extracting files...")
            current_step += 1
            progress_bar.progress(current_step / total_steps)

            if multi_variant_files['total_commits'] == 0:
                create_no_commits_file(output_folders[branch_key], branch_name, jira_number)
                branch_results['extraction_summary'] = {
                    'branch_key': branch_key,
                    'total_commits': 0,
                    'existing_count': 0,
                    'deleted_count': 0,
                    'existing_files': [],
                    'deleted_files': [],
                    'variant_breakdown': {},
                    'errors': []
                }
            else:
                extraction_summary = process_branch_extraction_multi_variant(
                    repo_variants,
                    multi_variant_files,
                    jira_number,
                    output_folders,
                    branch_key
                )
                branch_results['extraction_summary'] = extraction_summary

            extraction_results['branches'][branch_key] = branch_results

        # Restore original state
        with status_container:
            st.info("🔙 Restoring original state...")
        _restore_all_states()

        # Complete
        progress_bar.progress(1.0)
        with status_container:
            st.success("✨ Extraction completed successfully!")

        st.session_state.extraction_results = extraction_results

        time.sleep(1.5)
        st.rerun()

    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        _restore_all_states()

    st.markdown("</div>", unsafe_allow_html=True)


def _validate_inputs(jira_number, base_path, repo_name, output_path):
    """Validate all inputs"""
    errors = []

    is_valid, msg = validate_jira_number(jira_number)
    if not is_valid:
        errors.append(f"Jira Number: {msg}")

    is_valid, msg = validate_path(base_path, should_exist=True)
    if not is_valid:
        errors.append(f"Base Path: {msg}")

    is_valid, msg = validate_path(output_path, should_exist=False)
    if not is_valid:
        errors.append(f"Output Path: {msg}")

    if not st.session_state.repo_scan_results:
        errors.append("Please scan repositories first")
    elif repo_name not in st.session_state.repo_scan_results:
        errors.append(f"Repository '{repo_name}' not found")
    else:
        repo_variants = st.session_state.repo_scan_results[repo_name]
        is_valid, msg = validate_repo_variants(repo_variants)
        if not is_valid:
            errors.append(msg)

    return errors


def _display_validation_errors(errors):
    """Display validation errors in a styled container"""
    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
    st.error("**⚠️ Validation Errors**")
    for error in errors:
        st.markdown(f"<div style='color: #fca5a5; margin-left: 1.5rem;'>• {error}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _save_original_states(repo_variants):
    """Save original branch states for all variants"""
    for variant, info in repo_variants.items():
        if info['is_git_repo']:
            repo_path = info['path']
            original_branch = get_current_branch(repo_path)
            st.session_state.original_states[variant] = {
                'repo_path': repo_path,
                'branch': original_branch
            }


def _handle_uncommitted_changes(repo_variants, status_container):
    """Handle uncommitted changes in repositories"""
    for variant, info in repo_variants.items():
        if not info['is_git_repo']:
            continue

        repo_path = info['path']
        has_changes, changes_msg = check_uncommitted_changes(repo_path)

        if has_changes:
            with status_container:
                st.warning(f"⚠️ **Uncommitted changes in {info['full_name']}**")
                st.code(changes_msg, language="text")

                user_choice = st.radio(
                    f"Action required for {info['full_name']}:",
                    ["Stash changes and continue", "Abort extraction"],
                    key=f"uncommitted_{variant}"
                )

                if user_choice == "Abort extraction":
                    return False
                else:
                    with st.spinner(f"Stashing changes in {info['full_name']}..."):
                        success, stash_name = stash_changes(repo_path)
                        if success:
                            st.session_state.stash_info[variant] = stash_name
                            st.success(f"✓ Stashed: {stash_name}")
                        else:
                            st.error(f"❌ Stash failed: {stash_name}")
                            return False

    return True


def _handle_critical_error(error_msg, branch_results, extraction_results):
    """Handle critical errors during extraction"""
    branch_results['errors'].append(error_msg)
    extraction_results['errors'].append(error_msg)
    st.error(f"❌ {error_msg}")

    # Restore state before stopping
    _restore_all_states()
    st.stop()


def _restore_all_states():
    """Restore all repositories to original state"""
    for variant, state in st.session_state.original_states.items():
        success, msg = restore_original_branch(
            state['repo_path'],
            state['branch'],
            st.session_state.stash_info.get(variant)
        )
        if not success:
            st.warning(f"⚠ Failed to restore {variant}: {msg}")

    # Clear temporary states
    st.session_state.original_states = {}
    st.session_state.stash_info = {}