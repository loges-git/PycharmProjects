from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional


class Intent(Enum):
    RELEASE = "RELEASE"
    REPO_MANAGER = "REPO_MANAGER"


class Environment(Enum):
    CIT = "CIT"
    BFX = "BFX"


class ReleaseType(Enum):
    FULL = "FULL"
    FIX = "FIX"
    ROLLBACK = "ROLLBACK"


class Platform(Enum):
    GITHUB = "github"
    BITBUCKET = "bitbucket"


@dataclass
class ReleaseContext:
    # -------------------------
    # UI / Session
    # -------------------------
    intent: Optional[Intent] = None
    environment: Optional[Environment] = None
    release_type: Optional[ReleaseType] = None

    # -------------------------
    # Cluster / Repo
    # -------------------------
    cluster: Optional[str] = None
    platform: Optional[Platform] = None
    repo_path: Optional[Path] = None
    repo_url: Optional[str] = None
    base_branch: Optional[str] = None
    release_branch: Optional[str] = None

    # -------------------------
    # Jira
    # -------------------------
    epic_jira: Optional[str] = None
    release_jira: Optional[str] = None
    bug_jiras: List[str] = field(default_factory=list)

    # Jira (extended)
    jira_description: Optional[str] = None
    jira_labels: List[str] = field(default_factory=list)

    # -------------------------
    # Review / Shared workspace
    # -------------------------
    shared_root_path: Optional[Path] = None
    shared_retro_path: Optional[Path] = None
    search_tag: Optional[str] = None

    # -------------------------
    # Approval
    # -------------------------
    approval_id: Optional[str] = None
    approval_file: Optional[Path] = None
    approved_files: Dict[str, str] = field(default_factory=dict)
    base_commit: Optional[str] = None
