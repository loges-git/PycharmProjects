# ui/jira_ops.py

import streamlit as st
import yaml
import urllib.parse

from models.release_context import ReleaseContext
from validators.input_validator import (
    validate_epic_jira,
    validate_release_jira
)


# --------------------------------------------------
# Load Jira settings
# --------------------------------------------------

def load_jira_settings() -> dict:
    with open("config/settings.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)["jira"]


# --------------------------------------------------
# Build Jira Create-Issue URL (UI redirect)
# --------------------------------------------------

def build_jira_create_url(epic_jira: str) -> str:
    jira_cfg = load_jira_settings()

    base_url = jira_cfg["base_url"]
    project_id = jira_cfg["project_key"]      # can be numeric pid or key (as configured)
    issue_type = jira_cfg["issue_type"]        # usually "Task"
    epic_field = jira_cfg["epic_field_id"]     # e.g. customfield_10008

    params = {
        "pid": project_id,
        "issuetype": issue_type,
        epic_field: epic_jira
    }

    query = urllib.parse.urlencode(params)
    return f"{base_url}/secure/CreateIssueDetails!init.jspa?{query}"


# --------------------------------------------------
# Jira UI
# --------------------------------------------------

def render_jira_ops(context: ReleaseContext) -> None:
    """
    Jira creation via UI redirect.
    No API integration by design.
    """

    st.header("📌 Jira Operations")

    # -------------------------
    # Epic Jira input
    # -------------------------

    epic = st.text_input(
        "Epic Jira",
        placeholder="EPIC-1234 or full Jira URL",
        value=context.epic_jira or ""
    )

    if epic:
        try:
            validate_epic_jira(epic)
            context.epic_jira = epic.strip()
        except Exception as e:
            st.error(str(e))
            return

        jira_url = build_jira_create_url(context.epic_jira)

        st.link_button(
            "🔗 Create Release Jira in Jira",
            jira_url
        )

        st.info(
            "This will open Jira in a new tab.\n\n"
            "➡️ Select required fields\n"
            "➡️ Add description & labels\n"
            "➡️ Create the issue\n"
            "➡️ Copy the created BANKING Jira and paste it below"
        )

    st.divider()

    # -------------------------
    # Release Jira input
    # -------------------------

    release_jira = st.text_input(
        "Release Jira (BANKING number)",
        placeholder="BANKING-120901",
        value=context.release_jira or ""
    )

    if release_jira:
        try:
            validate_release_jira(release_jira)
            context.release_jira = release_jira.strip()
            st.success(f"Release Jira set: {context.release_jira}")
        except Exception as e:
            st.error(str(e))
