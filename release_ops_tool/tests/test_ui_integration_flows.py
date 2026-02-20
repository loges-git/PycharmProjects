import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from models.release_context import Environment, ReleaseType
from services.approval_service import create_approval_record, load_approval_record

# Simulate the "Record Approval" button flow
@pytest.mark.parametrize("env", [Environment.CIT, Environment.BFX])
@pytest.mark.parametrize("release_type", [ReleaseType.FULL, ReleaseType.FIX])
@patch("services.git_service.get_remote_branch_head")
def test_record_approval_button_flow(mock_get_head, env, release_type, tmp_path):
    # 1. Setup UI context (simulated)
    approval_dir = tmp_path / "approvals"
    repo_path = tmp_path / "repo"
    
    mock_get_head.return_value = "commit_hash_123"
    
    # 2. Simulate User clicking "Record Approval"
    # This triggers create_approval_record with gathered context
    approval_file = create_approval_record(
        approval_dir=approval_dir,
        approval_id=f"APPROVED_Manager_Test_{env.value}",
        environment=env,
        release_type=release_type,
        base_branch="develop",
        base_commit=mock_get_head(repo_path, "develop"),  # UI calls this
        approved_files={"script.sql": "hash_abc"},
        release_jira="JIRA-100",
        cluster="test-cluster-01",
        shared_path=str(tmp_path / "shared"),
        search_tag="tag-100"
    )
    
    # 3. Validation
    assert approval_file.exists()
    
    data = load_approval_record(approval_file)
    assert data["environment"] == env.value
    assert data["release_type"] == release_type.value
    assert data["base_commit"] == "commit_hash_123"


# Simulate the "Load Approval" button flow
@pytest.mark.parametrize("env", [Environment.CIT, Environment.BFX])
@pytest.mark.parametrize("release_type", [ReleaseType.FULL, ReleaseType.FIX])
def test_load_approval_button_flow(env, release_type, tmp_path):
    # 1. Setup existing external approval
    approval_dir = tmp_path / "approvals"
    create_approval_record(
        approval_dir=approval_dir,
        approval_id=f"APPROVED_External_{env.value}",
        environment=env,
        release_type=release_type,
        base_branch="develop",
        base_commit="hash_xyz",
        approved_files={"file.sql": "hash_1"},
        release_jira="JIRA-200",
        cluster="cluster-A"
    )
    
    # 2. Simulate User clicking "Load Approval" (Searching/Filtering logic)
    # The UI iterates over files and filters. We verify the service reads it correctly.
    
    found_approvals = []
    for f in approval_dir.glob("*.json"):
        data = load_approval_record(f)
        # Simulate filter:
        if (data["release_jira"] == "JIRA-200" and 
            data["cluster"] == "cluster-A" and
            data["environment"] == env.value and
            data["release_type"] == release_type.value):
             found_approvals.append(data)
             
    # 3. Validation
    assert len(found_approvals) == 1
    assert found_approvals[0]["approval_id"] == f"APPROVED_External_{env.value}"
    assert found_approvals[0]["environment"] == env.value
    assert found_approvals[0]["release_type"] == release_type.value
