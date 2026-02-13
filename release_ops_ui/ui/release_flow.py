# ui/release_flow.py

import streamlit as st
import yaml
from pathlib import Path

from models.release_context import ReleaseContext, ReleaseType
from services.release_service import execute_release
from validators.drift_validator import (
    validate_no_drift,
    DriftDetectedError,
    DriftReadError
)


def load_clusters_config() -> dict:
    with open("config/clusters.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["clusters"]


def render_cluster_selector(context):
    """Select cluster (SSA, LDN, WEU, etc.)"""
    st.subheader("📍 Select Cluster")

    if context.cluster:
        st.info(f"Cluster locked: {context.cluster}")
        return

    clusters = load_clusters_config()
    cluster_names = list(clusters.keys())

    selected = st.selectbox(
        "Choose cluster",
        cluster_names
    )

    if st.button("Confirm Cluster"):
        context.cluster = selected

        # Auto-resolve repo config
        cluster_cfg = clusters[selected]
        context.repo_path = Path(cluster_cfg["local_path"])
        context.repo_url = cluster_cfg["repo_url"]
        context.platform = cluster_cfg["platform"]

        # Auto-resolve base branch based on environment
        context.base_branch = cluster_cfg["branches"][context.environment.value]

        st.rerun()


def render_release_type_selector(context):
    """Select release type (FULL / FIX / ROLLBACK)"""
    st.subheader("🎯 Select Release Type")

    if context.release_type:
        st.info(f"Release Type locked: {context.release_type.value}")
        return

    release_type = st.radio(
        "Choose release type",
        options=[ReleaseType.FULL, ReleaseType.FIX, ReleaseType.ROLLBACK],
        format_func=lambda x: {
            ReleaseType.FULL: "📦 Full Project Release",
            ReleaseType.FIX: "🔧 Fix / Bug Release",
            ReleaseType.ROLLBACK: "⏪ Rollback Release"
        }[x]
    )

    if st.button("Confirm Release Type"):
        context.release_type = release_type
        st.rerun()


def generate_release_branch_name(context) -> str:
    """Generate branch name from release type + Jira"""
    prefix_map = {
        ReleaseType.FULL: "feature",
        ReleaseType.FIX: "feature",
        ReleaseType.ROLLBACK: "feature"
    }

    prefix = prefix_map[context.release_type]
    return f"{prefix}/{context.release_jira}"


def render_release_summary(context):
    st.header("📦 Release Summary")

    st.markdown("### 📋 Release Details")

    st.write(f"**Environment:** {context.environment.name}")
    st.write(f"**Release Type:** {context.release_type.name}")
    st.write(f"**Cluster:** {context.cluster}")
    st.write(f"**Base Branch:** `{context.base_branch}`")
    st.write(f"**Release Branch:** `{context.release_branch}`")
    st.write(f"**Release Jira:** `{context.release_jira}`")

    st.divider()

    st.markdown("### 📂 Approved Files")

    if not context.approved_files:
        st.warning("No approved files found.")
        return

    for file_path in context.approved_files.keys():
        st.write(f"📄 `{file_path}`")


def render_release_flow(context: ReleaseContext) -> None:
    """
    Final release execution UI with modern styling.
    """

    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
        <span style="font-size: 2rem; vertical-align: middle;">🚀</span>
        <span style="font-family: 'Poppins', sans-serif; font-size: 1.5rem; font-weight: 700;
                     background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
                     -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                     margin-left: 0.5rem; vertical-align: middle;">
            Release Execution
        </span>
    </div>
    """, unsafe_allow_html=True)

    # -------------------------
    # Guard: Prerequisites
    # -------------------------
    if not context.cluster or not context.release_type:
        st.warning("⚠️ Please define **Cluster** and **Release Type** in the **Setup** tab first.")
        return

    st.success(f"✅ Target: **{context.cluster}** | Type: **{context.release_type.value}**")
    st.divider()

    # -------------------------
    # Step 3: Auto-generate release branch name
    # -------------------------
    if context.release_jira and not context.release_branch:
        context.release_branch = generate_release_branch_name(context)

    # -------------------------
    # Step 4: Wait for approval before showing release execution
    # -------------------------
    if not context.approval_file:
        st.info(
            "📋 **Next Step**: Scroll down to the **Review & Approval** section below to:\n"
            "1. Enter the shared review path\n"
            "2. Enter the search tag\n"
            "3. Record approval\n\n"
            "Once approval is recorded, return here to execute the release."
        )
        return

    # -------------------------
    # Pre-flight checks
    # -------------------------
    missing = []

    if not context.environment:
        missing.append("Environment")
    if not context.release_type:
        missing.append("Release Type")
    if not context.repo_path:
        missing.append("Repository")
    if not context.base_branch:
        missing.append("Base Branch")
    if not context.release_branch:
        missing.append("Release Branch")
    if not context.release_jira:
        missing.append("Release Jira")
    if not context.approval_file:
        missing.append("Approval")

    if missing:
        st.warning(
            "Cannot proceed. Missing prerequisites:\n- "
            + "\n- ".join(missing)
        )
        return

    # -------------------------
    # Summary
    # -------------------------
    st.markdown("### 📋 Release Summary")

    st.code(f"""
Environment    : {context.environment.value}
Release Type   : {context.release_type.value}
Cluster        : {context.cluster}
Base Branch    : {context.base_branch}
Release Branch : {context.release_branch}
Release Jira   : {context.release_jira}
Approval ID    : {context.approval_id}
""")

    st.markdown("### 🛡 Approval Status")

    if not context.approval_file:
        st.warning("⏳ No approval recorded yet.")
        return

    try:
        validate_no_drift(
            repo_path=context.repo_path,
            base_branch=context.base_branch,
            approval_file=context.approval_file
        )

        st.success("✅ APPROVED — No drift detected since approval")

    except DriftDetectedError as e:
        st.error("⚠️ DRIFTED — Code has changed since approval")

        st.table(
            [{"File": f, "Status": "❌ Drifted"} for f in e.drifted_files]
        )

        st.stop()

    except DriftReadError as e:
        st.error("❌ Unable to validate drift due to repository read error")
        st.code(str(e))
        st.stop()

    # -------------------------
    # Final confirmation
    # -------------------------
    confirm = st.checkbox(
        "⚠️ I confirm that I want to execute this release"
    )

    if not confirm:
        st.info("Awaiting final confirmation.")
        return

    if st.button("🚀 Execute Release"):
        try:
            execute_release(context)
            st.success("🎉 Release executed successfully!")
            st.balloons()
        except RuntimeWarning as w:
            st.warning(str(w))
        except Exception as e:
            if st.session_state.get("debug"):
                st.exception(e)
            else:
                st.error(
                    f"❌ Release failed: {str(e)}\n\n"
                    "Enable Debug Mode for full details."
                )