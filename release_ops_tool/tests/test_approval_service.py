import json
import pytest
from pathlib import Path
from datetime import datetime, UTC
from unittest.mock import patch, MagicMock

from services.approval_service import (
    create_approval_record,
    load_approval_record,
    mark_approval_consumed,
    revoke_approval,
    ApprovalServiceError
)
from models.release_context import Environment, ReleaseType


@pytest.fixture
def temp_approval_dir(tmp_path):
    return tmp_path / "approvals"


@pytest.fixture
def sample_approval_data(request):
    # Default values, can be overridden by indirect parameterization if needed
    env = getattr(request, "param", {}).get("env", Environment.CIT)
    rtype = getattr(request, "param", {}).get("rtype", ReleaseType.FULL)
    
    return {
        "approval_id": f"APPROVED_Test_User_20260101_{env.value}_{rtype.value}",
        "environment": env,
        "release_type": rtype,
        "base_branch": "develop",
        "base_commit": "abc1234",
        "approved_files": {"file1.txt": "hash1"},
        "release_jira": "JIRA-123",
        "cluster": "test-cluster",
        "shared_path": "/tmp/shared",
        "search_tag": "test-tag"
    }


@pytest.mark.parametrize("env", [Environment.CIT, Environment.BFX])
@pytest.mark.parametrize("release_type", [ReleaseType.FULL, ReleaseType.FIX, ReleaseType.ROLLBACK])
def test_create_approval_record(temp_approval_dir, env, release_type):
    approval_id = f"APPROVED_{env.value}_{release_type.value}_123"
    
    approval_file = create_approval_record(
        approval_dir=temp_approval_dir,
        approval_id=approval_id,
        environment=env,
        release_type=release_type,
        base_branch="develop",
        base_commit="abc1234",
        approved_files={"file.txt": "hash"},
        release_jira="JIRA-123",
        cluster="test-cluster"
    )

    assert approval_file.exists()
    
    with open(approval_file, "r") as f:
        data = json.load(f)

    assert data["environment"] == env.value
    assert data["release_type"] == release_type.value


def test_load_approval_record(temp_approval_dir):
    # Basic load test
    approval_file = create_approval_record(
        approval_dir=temp_approval_dir,
        approval_id="TEST_LOAD_1",
        environment=Environment.CIT,
        release_type=ReleaseType.FULL,
        base_branch="main",
        base_commit="123",
        approved_files={}
    )

    loaded_data = load_approval_record(approval_file)
    assert loaded_data["approval_id"] == "TEST_LOAD_1"


def test_load_approval_record_not_found(temp_approval_dir):
    missing_file = temp_approval_dir / "nonexistent.json"
    with pytest.raises(ApprovalServiceError):
        load_approval_record(missing_file)


def test_mark_approval_consumed(temp_approval_dir):
    approval_file = create_approval_record(
        approval_dir=temp_approval_dir,
        approval_id="TEST_CONSUME_1",
        environment=Environment.CIT,
        release_type=ReleaseType.FULL,
        base_branch="main",
        base_commit="123",
        approved_files={}
    )

    mark_approval_consumed(approval_file)

    loaded_data = load_approval_record(approval_file)
    assert loaded_data["consumed"] is True


def test_revoke_approval(temp_approval_dir):
    approval_file = create_approval_record(
        approval_dir=temp_approval_dir,
        approval_id="TEST_REVOKE_1",
        environment=Environment.CIT,
        release_type=ReleaseType.FULL,
        base_branch="main",
        base_commit="123",
        approved_files={}
    )

    revoke_approval(approval_file, "Mgr", "Reason")

    loaded_data = load_approval_record(approval_file)
    assert loaded_data["revoked"] is True


def test_cannot_revoke_consumed_approval(temp_approval_dir):
    approval_file = create_approval_record(
        approval_dir=temp_approval_dir,
        approval_id="TEST_REVOKE_CONSUMED",
        environment=Environment.CIT,
        release_type=ReleaseType.FULL,
        base_branch="main",
        base_commit="123",
        approved_files={}
    )

    mark_approval_consumed(approval_file)

    with pytest.raises(ApprovalServiceError):
        revoke_approval(approval_file, "Mgr", "Reason")
