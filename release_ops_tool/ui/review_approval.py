# ui/review_approval.py

import streamlit as st
import os
from pathlib import Path
from datetime import datetime, UTC
from typing import Optional, Tuple

from models.release_context import ReleaseContext
from services.approval_service import create_approval_record
from utils.hashing import calculate_file_hash
from services.git_service import get_remote_branch_head, is_repo


def render_review_approval(context: ReleaseContext) -> None:
    """
    Review & Approval UI with shareable review link support.
    """

    # -------------------------------------------------
    # Load context from URL (review link)
    # -------------------------------------------------
    query_params = st.query_params

    link_shared_path = query_params.get("shared_path", "")
    link_search_tag = query_params.get("tag", "")
    requested_by = query_params.get("requested_by", "")
    link_environment = query_params.get("environment", "")
    link_cluster = query_params.get("cluster", "")
    link_release_type = query_params.get("release_type", "")

    opened_via_link = bool(link_shared_path and link_search_tag)

    # If opened via link, restore context from URL
    if opened_via_link:
        from models.release_context import Environment, ReleaseType
        import yaml

        # Set environment from link
        if link_environment and not context.environment:
            context.environment = Environment(link_environment)

        # Set cluster from link
        if link_cluster and not context.cluster:
            context.cluster = link_cluster

            # Auto-resolve repo config from cluster
            with open("config/clusters.yaml", "r", encoding="utf-8") as f:
                clusters = yaml.safe_load(f)["clusters"]

            cluster_cfg = clusters[link_cluster]
            context.repo_path = Path(cluster_cfg["local_path"])
            context.repo_url = cluster_cfg["repo_url"]
            context.platform = cluster_cfg["platform"]
            context.base_branch = cluster_cfg["branches"][context.environment.value]

        # Set release type from link
        if link_release_type and not context.release_type:
            context.release_type = ReleaseType(link_release_type)

    # -------------------------------------------------
    # MANAGER VIEW (opened via link)
    # -------------------------------------------------
    if opened_via_link:
        st.header("🧾 Review & Approval")

        st.info(
            f"📋 **Review Request from:** `{requested_by or 'Release Engineer'}`\n\n"
            f"**Environment:** {context.environment.value}\n"
            f"**Cluster:** {context.cluster}\n"
            f"**Release Type:** {context.release_type.value}\n\n"
            "Please review the files below and approve if everything is correct."
        )

        st.warning(
            "⚠️ **IMPORTANT:** After approving, please communicate the **Approval ID** "
            "back to the release engineer who sent you this link. They will need it to load your approval."
        )

        st.divider()

        # Show shared path (read-only)
        st.text_input(
            "Shared review path",
            value=link_shared_path,
            disabled=True
        )

        # Add button to open in explorer
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_input(
                "Search tag",
                value=link_search_tag,
                disabled=True
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📂 Open in Explorer"):
                import subprocess
                import platform

                path = Path(link_shared_path)
                if path.exists():
                    if platform.system() == "Windows":
                        subprocess.run(["explorer", str(path)])
                    elif platform.system() == "Darwin":
                        subprocess.run(["open", str(path)])
                    else:
                        subprocess.run(["xdg-open", str(path)])
                else:
                    st.error("Path does not exist!")

        st.divider()

        shared_root_path = Path(link_shared_path)
        retro_path = shared_root_path / "retro"

        if not retro_path.exists():
            st.error("❌ Retro folder not found in shared path.")
            return

        # -------------------------------------------------
        # List files for review with comparison tools
        # -------------------------------------------------
        st.markdown("### 📂 Files for Review")

        # Show folder paths for reference
        with st.expander("📁 Folder Structure (for manual comparison)"):
            st.code(f"""
Shared Path: {shared_root_path}

Folders for comparison:
- dev/    → Developer version
- cit/    → Current CIT/UAT version
- bfx/    → Current BFX version (if applicable)
- prod/   → Production version
- retro/  → Final code to be released (what you're approving)
""")

        st.markdown("#### Files in RETRO folder (to be released):")

        approved_files = {}
        files = list(retro_path.rglob("*"))

        if not files:
            st.warning("No files found in retro folder.")
            return

        for file in files:
            if file.is_file():
                rel_path = file.relative_to(retro_path)
                file_hash = calculate_file_hash(file)
                approved_files[str(rel_path)] = file_hash

                # Show file with comparison option
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"📄 {rel_path}")
                with col2:
                    if st.button("👁️ View", key=f"view_{rel_path}"):
                        try:
                            content = file.read_text(encoding="utf-8")
                            st.code(content, language="sql" if file.suffix == ".sql" else None)
                        except Exception as e:
                            st.error(f"Cannot read file: {e}")
                with col3:
                    if st.button("🔍 Compare", key=f"compare_{rel_path}"):
                        st.info(
                            f"**To compare:**\n\n"
                            f"Use your comparison tool (WinMerge, Beyond Compare, etc.) to compare:\n\n"
                            f"**Retro (new):** `{retro_path / rel_path}`\n\n"
                            f"**vs CIT (current):** `{shared_root_path / 'cit' / rel_path}`\n\n"
                            f"Or open the shared folder in Explorer using the button above."
                        )

        st.divider()

        # -------------------------------------------------
        # MANAGER APPROVAL SECTION
        # -------------------------------------------------
        approve_checked = st.checkbox(
            "✅ I have reviewed and approve these changes"
        )

        if approve_checked:
            manager_name = st.text_input(
                "Your Name / Manager ID",
                placeholder="e.g., John Smith or MGRID123",
                help="This will be used to generate the approval ID"
            )

            if st.button("🔒 Record Approval"):
                if not manager_name:
                    st.error("Please enter your name or manager ID.")
                    return

                # Auto-generate unique approval ID
                timestamp = datetime.now(UTC).strftime('%Y%m%d_%H%M%S')
                safe_name = manager_name.strip().replace(" ", "_")[:20]
                approval_id = f"APPROVED_{safe_name}_{timestamp}"

                # Lock context
                context.shared_root_path = shared_root_path
                context.shared_retro_path = retro_path
                context.search_tag = link_search_tag
                context.approval_id = approval_id
                context.approved_files = approved_files

                # Pre-check: Validate Repository
                if not context.repo_path.exists():
                    st.error(
                        f"❌ Local repository not found at: `{context.repo_path}`\n\n"
                        "👉 **Action Required:** Go to the **Repo Manager** (main menu) and clone the repository for this cluster."
                    )
                    return

                if not is_repo(context.repo_path):
                    st.error(
                        f"❌ Invalid git repository at: `{context.repo_path}`\n\n"
                        "👉 **Action Required:** The folder exists but is not a git repo. Use **Repo Manager** to fix this."
                    )
                    return

                try:
                    # Capture base commit for drift detection
                    base_commit = get_remote_branch_head(
                        context.repo_path,
                        context.base_branch
                    )
                    context.base_commit = base_commit
                except Exception as e:
                    st.error(
                        f"❌ Failed to verify remote branch status.\n\n"
                        f"**Error Details:** `{str(e)}`\n\n"
                        "👉 **Likely Fix:** The local repository might be stale.\n"
                        "1. Go to **Repo Manager** tab.\n"
                        "2. Click **Refresh / Fetch** for this cluster.\n"
                        "3. Try again."
                    )
                    return

                approval_file = create_approval_record(
                    approval_dir=Path("data/approvals"),
                    approval_id=approval_id,
                    environment=context.environment,
                    release_type=context.release_type,
                    base_branch=context.base_branch,
                    base_commit=base_commit,
                    approved_files=approved_files,
                    release_jira=requested_by,
                    cluster=context.cluster,
                    shared_path=link_shared_path,
                    search_tag=link_search_tag
                )

                context.approval_file = approval_file

                st.success("✅ Approval recorded successfully!")
                st.balloons()

                # Show approval ID prominently
                st.markdown("---")
                st.markdown("### 📢 IMPORTANT: Communicate This Approval ID")
                st.markdown(f"# 🔑 `{approval_id}`")
                st.markdown("---")

                st.info(
                    f"📄 **Approval File Created:** `{approval_file}`\n\n"
                    f"**Approved At:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
                    f"**Approved By:** {manager_name}\n\n"
                    "⚠️ **Please send the Approval ID above to the release engineer** "
                    "via email/Teams so they can load this specific approval."
                )

                st.session_state["approval_just_created"] = True

        # Show approved status only if just created
        if st.session_state.get("approval_just_created"):
            st.success(f"🔒 Approved (Approval ID: {context.approval_id})")

        return

    # -------------------------------------------------
    # RELEASE ENGINEER VIEW (normal flow)
    # -------------------------------------------------
    st.header("🧾 Review & Approval")

    shared_root = st.text_input(
        "Shared review path (contains dev / cit / retro folders)",
        placeholder="\\\\shared\\release_reviews\\BANKING-123456"
    )

    search_tag = st.text_input(
        "Search tag for review context",
        placeholder="--BANKING-123456 changes"
    )

    # Generate review link
    if shared_root and search_tag:
        base_url = os.getenv("APP_BASE_URL", "http://localhost:8501")

        cluster_param = f"&cluster={context.cluster}" if context.cluster else ""
        release_type_param = f"&release_type={context.release_type.value}" if context.release_type else ""

        review_link = (
            f"{base_url}/"
            f"?shared_path={shared_root}"
            f"&tag={search_tag}"
            f"&requested_by={context.release_jira or 'Release Engineer'}"
            f"&environment={context.environment.value}"
            f"{cluster_param}"
            f"{release_type_param}"
        )

        st.markdown("### 🔗 Review Link for Manager")
        st.code(review_link, language="text")

        st.info(
            f"📋 **This approval is for:**\n\n"
            f"- **Release Jira:** {context.release_jira}\n"
            f"- **Cluster:** {context.cluster}\n"
            f"- **Environment:** {context.environment.value}\n"
            f"- **Release Type:** {context.release_type.value}\n\n"
            "**Instructions:**\n"
            "1. Copy the link above\n"
            "2. Send it to your manager via email/Teams\n"
            "3. Manager will open the link and approve\n"
            "4. You'll see approval status appear below once manager approves"
        )

    st.divider()

    # Show approval status
    if not context.approval_file:
        st.markdown("### 📥 Load Manager Approval")

        st.info(
            "After your manager approves, they will send you an **Approval ID**.\n\n"
            "Enter that Approval ID below to load the approval."
        )

        # -------------------------
        # GUARD: Prerequisites
        # -------------------------
        if not context.cluster or not context.release_type:
            st.warning("⚠️ Please select **Cluster** and **Release Type** above to see matching approvals.")
            return

        approval_dir = Path("data/approvals")
        all_matching_approvals = []

        if approval_dir.exists():
            from services.approval_service import load_approval_record

            for approval_file in approval_dir.glob("*.json"):
                try:
                    approval_data = load_approval_record(approval_file)

                    # Only show UNCONSUMED approvals
                    if approval_data.get("consumed", False):
                        continue

                    # Only show NON-REVOKED approvals
                    if approval_data.get("revoked", False):
                        continue

                    # Check if this approval matches current release context
                    if (approval_data.get("release_jira") == context.release_jira and
                            approval_data.get("cluster") == context.cluster and
                            approval_data.get("environment") == context.environment.value and
                            approval_data.get("release_type") == context.release_type.value and
                            approval_data.get("shared_path") == shared_root and
                            approval_data.get("search_tag") == search_tag):

                        # CRITICAL SECURITY CHECK: Verify files haven't changed
                        approval_files = approval_data.get("approved_files", {})

                        current_retro_path = Path(shared_root) / "retro"
                        if not current_retro_path.exists():
                            continue

                        current_files = {}
                        for file in current_retro_path.rglob("*"):
                            if file.is_file():
                                rel_path = str(file.relative_to(current_retro_path))
                                current_hash = calculate_file_hash(file)
                                current_files[rel_path] = current_hash

                        # Check if file lists match
                        if set(approval_files.keys()) != set(current_files.keys()):
                            continue

                        # Check if file contents match
                        files_changed = False
                        for file_path, approved_hash in approval_files.items():
                            current_hash = current_files.get(file_path)
                            if current_hash != approved_hash:
                                files_changed = True
                                break

                        if files_changed:
                            continue

                        all_matching_approvals.append((approval_file, approval_data))

                except (FileNotFoundError, KeyError, ValueError):
                    continue

            if all_matching_approvals:
                all_matching_approvals.sort(key=lambda x: x[1].get("approved_at", ""), reverse=True)

                st.success(
                    f"✅ Found {len(all_matching_approvals)} unconsumed approval(s) matching your review request!")

                st.info(
                    "✅ **Approval validation passed:**\n\n"
                    f"- Shared Path: `{shared_root}`\n"
                    f"- Search Tag: `{search_tag}`\n\n"
                    "This ensures the approval is for the EXACT files you're releasing."
                )

                with st.expander("📋 Available Approvals (Click to see details)"):
                    for file, data in all_matching_approvals:
                        approved_at = data.get("approved_at", "Unknown")[:19]
                        file_count = len(data.get("approved_files", {}))
                        st.write(f"🔑 **{data['approval_id']}** - Approved: {approved_at} - Files: {file_count}")

                # Automatic loading if only one match
                if len(all_matching_approvals) == 1:
                    file, data = all_matching_approvals[0]

                    st.success(f"✅ Found exact match: **{data['approval_id']}**")

                    if st.button("📥 Load This Approval", key="load_single"):
                        context.approval_id = data["approval_id"]
                        context.approval_file = file
                        context.approved_files = data["approved_files"]
                        context.base_commit = data["base_commit"]

                        # CRITICAL: Load shared paths from approval
                        context.shared_root_path = Path(data["shared_path"])
                        context.shared_retro_path = Path(data["shared_path"]) / "retro"
                        context.search_tag = data["search_tag"]

                        st.success(f"✅ Loaded approval: {context.approval_id}")
                        st.info("⚠️ This approval will be marked as 'consumed' after successful release execution.")
                        st.rerun()
                else:
                    # Multiple matches
                    approval_id_input = st.text_input(
                        "Enter Approval ID from Manager",
                        placeholder="e.g., APPROVED_John_Smith_20260127_143052",
                        help="Multiple approvals match. Enter the specific one your manager sent you."
                    )

                    if st.button("📥 Load This Approval", key="load_multiple"):
                        if not approval_id_input:
                            st.error("Please enter an Approval ID")
                        else:
                            found_approval: Optional[Tuple[Path, dict]] = None

                            for file, data in all_matching_approvals:
                                if data["approval_id"] == approval_id_input.strip():
                                    found_approval = (file, data)
                                    break

                            if found_approval:
                                file, data = found_approval
                                context.approval_id = data["approval_id"]
                                context.approval_file = file
                                context.approved_files = data["approved_files"]
                                context.base_commit = data["base_commit"]

                                # CRITICAL: Load shared paths from approval
                                context.shared_root_path = Path(data["shared_path"])
                                context.shared_retro_path = Path(data["shared_path"]) / "retro"
                                context.search_tag = data["search_tag"]

                                st.success(f"✅ Loaded approval: {context.approval_id}")
                                st.info(
                                    "⚠️ This approval will be marked as 'consumed' after successful release execution.")
                                st.rerun()
                            else:
                                st.error(f"❌ Approval ID '{approval_id_input}' not found in matching approvals.")
            else:
                st.info(
                    f"⏳ Waiting for manager approval for:\n\n**{context.release_jira}** | **{context.cluster}** | **{context.environment.value}**")
                st.caption("💡 This page will auto-refresh every 10 seconds to check for new approvals.")

                import time
                time.sleep(10)
                st.rerun()
        else:
            st.info(
                f"⏳ Waiting for manager approval for:\n\n**{context.release_jira}** | **{context.cluster}** | **{context.environment.value}**")
            st.caption("💡 This page will auto-refresh every 10 seconds to check for new approvals.")

            import time
            time.sleep(10)
            st.rerun()

    if context.approval_file:
        st.success(f"✅ Approval Received (Approval ID: {context.approval_id})")
        st.info("You can now proceed to Release Execution section above.")