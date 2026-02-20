
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.release_service import execute_release
from services.git_service import GitCommandError
from models.release_context import ReleaseContext, Environment, ReleaseType
from pathlib import Path

class TestNoChangeHandling(unittest.TestCase):
    @patch('services.release_service.ensure_clean_working_tree')
    @patch('services.release_service.validate_no_drift')
    @patch('services.release_service.checkout_branch')
    @patch('services.release_service.create_or_checkout_branch')
    @patch('services.release_service.stage_all')
    @patch('services.release_service.commit_changes')
    @patch('services.release_service.push_branch')
    @patch('services.release_service.load_file_routing')
    @patch('pathlib.Path.mkdir')
    @patch('pathlib.Path.write_text')
    @patch('pathlib.Path.read_text')
    def test_no_change_warning(self, mock_read, mock_write, mock_mkdir, mock_routing, 
                              mock_push, mock_commit, mock_stage, mock_create, mock_checkout, 
                              mock_validate, mock_clean):
        
        # Setup context
        context = ReleaseContext()
        context.repo_path = Path("/mock/repo")
        context.base_branch = "main"
        context.release_branch = "release/integration"
        context.release_jira = "TEST-123"
        context.approval_file = Path("approval.json")
        context.approved_files = {"test.sql": "hash"}
        context.shared_retro_path = Path("/mock/retro")

        # Mock routing
        mock_routing.return_value = {}

        # Mock commit failure with "nothing to commit"
        error = GitCommandError(
            message="Git command failed",
            command=["git", "commit"],
            stdout="On branch main\nnothing to commit, working tree clean",
            stderr=""
        )
        mock_commit.side_effect = error

        # Assert that RuntimeWarning is raised
        with self.assertRaises(RuntimeWarning) as cm:
            execute_release(context)
        
        self.assertIn("Release skipped: No changes to commit", str(cm.exception))

if __name__ == "__main__":
    unittest.main()
