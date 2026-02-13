# ui/repo_manager.py

import streamlit as st
import yaml
from pathlib import Path

from services.repo_sync_service import ensure_repo_cloned, refresh_repo


def load_clusters_config() -> dict:
    with open("config/clusters.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["clusters"]


def render_repo_manager() -> None:
    """
    Repo management UI:
    - Clone repos
    - Refresh repos
    """

    st.header("🧰 Repository Manager")

    clusters = load_clusters_config()
    cluster_names = list(clusters.keys())

    selected_cluster = st.selectbox(
        "Select cluster",
        cluster_names
    )

    cluster_cfg = clusters[selected_cluster]
    repo_url = cluster_cfg["repo_url"]
    local_path = Path(cluster_cfg["local_path"])
    branches = cluster_cfg["branches"]

    st.markdown("### 📍 Resolved Repository Details")
    st.code(f"""
Repository URL : {repo_url}
Local Path     : {local_path}
Branches       : {branches}
""")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("📥 Clone Repo"):
            try:
                ensure_repo_cloned(repo_url, local_path)
                st.success("Repository cloned / already present.")
            except Exception as e:
                st.error(str(e))

    with col2:
        base_branch = st.selectbox(
            "Select branch to refresh",
            list(branches.values())
        )

        if st.button("🔄 Refresh Repo"):
            try:
                refresh_repo(local_path, base_branch)
                st.success(f"Repository refreshed on branch '{base_branch}'.")
            except Exception as e:
                st.error(str(e))

    st.divider()

    if st.button("🔃 Refresh ALL repositories"):
        failures = []

        for name, cfg in clusters.items():
            try:
                ensure_repo_cloned(cfg["repo_url"], Path(cfg["local_path"]))
                refresh_repo(
                    Path(cfg["local_path"]),
                    list(cfg["branches"].values())[0]
                )
            except Exception as e:
                failures.append(f"{name}: {e}")

        if failures:
            st.error("Some repositories failed to refresh:")
            for f in failures:
                st.write(f"- {f}")
        else:
            st.success("All repositories refreshed successfully.")
