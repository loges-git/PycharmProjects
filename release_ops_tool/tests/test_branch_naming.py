from models.release_context import ReleaseContext, ReleaseType
from ui.release_flow import generate_release_branch_name

def test_generate_release_branch_name_full():
    context = ReleaseContext(
        release_type=ReleaseType.FULL,
        release_jira="JIRA-123"
    )
    branch_name = generate_release_branch_name(context)
    assert branch_name == "feature/JIRA-123"

def test_generate_release_branch_name_fix():
    context = ReleaseContext(
        release_type=ReleaseType.FIX,
        release_jira="JIRA-456"
    )
    branch_name = generate_release_branch_name(context)
    # This assertion reflects the DESIRED behavior (feature/), 
    # but initially it will fail (returning bugfix/)
    assert branch_name == "feature/JIRA-456"

def test_generate_release_branch_name_rollback():
    context = ReleaseContext(
        release_type=ReleaseType.ROLLBACK,
        release_jira="JIRA-789"
    )
    branch_name = generate_release_branch_name(context)
    assert branch_name == "feature/JIRA-789"
