"""
COMPREHENSIVE QA TEST SUITE
Senior Level Testing - Production Readiness Validation

Test Categories:
1. Module Unit Tests (Positive & Negative)
2. Integration Tests (End-to-End Flows)
3. Error Handling & Edge Cases
4. Configuration Validation
5. Email Functionality (Disabled by default)
"""

import unittest
import json
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add core modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.email_sender import EmailSender
from core.validator import DeploymentValidator
from core.cycle_manager import CycleManager


class TestEmailSender(unittest.TestCase):
    """POSITIVE & NEGATIVE TESTS: Email Sender Module"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.config_enabled = {
            "email_settings": {
                "enabled": True,
                "recipients": ["test@company.com", "qa@company.com"],
                "subject_templates": {
                    "PASS": "[PASS] {cluster} - {instance}",
                    "FAIL": "[FAIL] {cluster} - {instance}"
                },
                "body_template": "Status: {status}\nMessage: {message}"
            }
        }
        
        self.config_disabled = {
            "email_settings": {
                "enabled": False,
                "recipients": ["test@company.com"]
            }
        }
        
        self.config_empty = {}
    
    # ============ POSITIVE TESTS ============
    
    def test_email_sender_init_with_valid_config(self):
        """✅ TEST: EmailSender initializes with valid config"""
        sender = EmailSender(self.config_enabled)
        self.assertTrue(sender.enabled)
        self.assertEqual(len(sender.recipients), 2)
        self.assertIn("test@company.com", sender.recipients)
    
    def test_email_sender_init_with_empty_config(self):
        """✅ TEST: EmailSender handles missing email_settings gracefully"""
        sender = EmailSender(self.config_empty)
        self.assertFalse(sender.enabled)
        self.assertEqual(len(sender.recipients), 0)
    
    def test_build_subject_pass_status(self):
        """✅ TEST: Build PASS subject correctly"""
        sender = EmailSender(self.config_enabled)
        subject = sender.build_subject("PASS", "MENA", "FSMHO1U")
        self.assertEqual(subject, "[PASS] MENA - FSMHO1U")
    
    def test_build_subject_fail_status(self):
        """✅ TEST: Build FAIL subject correctly"""
        sender = EmailSender(self.config_enabled)
        subject = sender.build_subject("FAIL", "SSA", "FCCNIG")
        self.assertEqual(subject, "[FAIL] SSA - FCCNIG")
    
    def test_build_body_with_all_placeholders(self):
        """✅ TEST: Build body with all placeholders replaced"""
        sender = EmailSender(self.config_enabled)
        body = sender.build_body("PASS", "CEE", "FMSLO1P", "All checks passed")
        self.assertIn("PASS", body)
        self.assertIn("All checks passed", body)
    
    def test_send_mail_disabled(self):
        """✅ TEST: send_mail returns graceful error when disabled"""
        sender = EmailSender(self.config_disabled)
        success, msg = sender.send_mail("Test", "Test Body")
        self.assertFalse(success)
        self.assertIn("disabled", msg.lower())
    
    def test_send_mail_no_recipients(self):
        """✅ TEST: send_mail returns error with no recipients"""
        config = {
            "email_settings": {
                "enabled": True,
                "recipients": []
            }
        }
        sender = EmailSender(config)
        success, msg = sender.send_mail("Test", "Test Body")
        self.assertFalse(success)
        self.assertIn("recipient", msg.lower())
    
    # ============ NEGATIVE TESTS ============
    
    def test_build_subject_with_missing_template(self):
        """❌ TEST: Handle missing PASS/FAIL template gracefully"""
        config = {
            "email_settings": {
                "enabled": True,
                "recipients": ["test@company.com"],
                "subject_templates": {}  # Empty templates
            }
        }
        sender = EmailSender(config)
        subject = sender.build_subject("UNKNOWN_STATUS", "MENA", "FSMHO1U")
        # Should use default or handle gracefully
        self.assertIsNotNone(subject)
    
    def test_build_subject_with_special_characters(self):
        """❌ TEST: Handle special characters in cluster/instance names"""
        sender = EmailSender(self.config_enabled)
        subject = sender.build_subject("PASS", "MENA@#$", "FSMHO1U-TEST")
        self.assertIsNotNone(subject)
    
    def test_send_deployment_summary_pass(self):
        """✅ TEST: send_deployment_summary called with PASS status"""
        sender = EmailSender(self.config_disabled)
        success, msg = sender.send_deployment_summary("PASS", "MENA", "FSMHO1U", "Validation successful")
        self.assertFalse(success)  # Disabled, so should fail gracefully
    
    @patch('core.email_sender.win32com.client.Dispatch')
    def test_send_mail_outlook_exception_handled(self, mock_dispatch):
        """❌ TEST: Handle Outlook COM exceptions gracefully"""
        mock_outlook = MagicMock()
        mock_outlook.CreateItem.side_effect = Exception("Outlook not available")
        mock_dispatch.return_value = mock_outlook
        
        sender = EmailSender(self.config_enabled)
        success, msg = sender.send_mail("Test", "Test Body")
        self.assertFalse(success)
        self.assertIn("failed", msg.lower())


class TestDeploymentValidator(unittest.TestCase):
    """POSITIVE & NEGATIVE TESTS: Validator Module"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.config = {
            "ignorable_errors": ["ORA-00001", "ORA-00955"]
        }
        
        # Create temporary log files
        self.temp_dir = tempfile.mkdtemp()
        self.main_log = Path(self.temp_dir) / "main.log"
        self.invalid_log = Path(self.temp_dir) / "invalids.log"
        self.error_log = Path(self.temp_dir) / "error.log"
        
        self.metadata = {
            "main_log_path": self.main_log,
            "invalid_log_path": self.invalid_log,
            "error_log_path": self.error_log
        }
    
    def tearDown(self):
        """Cleanup temp files"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    # ============ POSITIVE TESTS ============
    
    def test_validator_init_with_valid_metadata(self):
        """✅ TEST: Validator initializes correctly with valid metadata"""
        validator = DeploymentValidator(self.metadata, self.config)
        self.assertFalse(validator.invalid_mismatch)
        self.assertFalse(validator.execution_mismatch)
        self.assertEqual(len(validator.detected_errors), 0)
    
    def test_validate_errors_no_errors(self):
        """✅ TEST: Validation passes when no errors detected"""
        # Create clean log
        self.main_log.write_text("Compilation successful\nNo errors found")
        self.invalid_log.write_text("Number of invalids at start: 0\nNumber of invalids at end: 0")
        self.error_log.write_text("")
        
        validator = DeploymentValidator(self.metadata, self.config)
        result = validator.validate_all()
        
        self.assertEqual(result["status"], "PASS")
    
    def test_validate_errors_ignorable_error(self):
        """✅ TEST: Ignorable errors do not fail validation"""
        # Log with ignorable error
        self.main_log.write_text("ORA-00001: unique constraint violated\nBut this is ignorable")
        self.invalid_log.write_text("Number of invalids at start: 0\nNumber of invalids at end: 0")
        
        validator = DeploymentValidator(self.metadata, self.config)
        result = validator.validate_all()
        
        self.assertEqual(result["status"], "PASS")
        self.assertIn("ORA-00001", validator.detected_errors)
        self.assertNotIn("ORA-00001", validator.filtered_errors)
    
    def test_validate_errors_non_ignorable(self):
        """✅ TEST: Non-ignorable errors fail validation"""
        # Log with non-ignorable error
        self.main_log.write_text("ORA-12514: listener connection refused")
        self.invalid_log.write_text("Number of invalids at start: 0\nNumber of invalids at end: 0")
        
        validator = DeploymentValidator(self.metadata, self.config)
        result = validator.validate_all()
        
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("ORA-12514", validator.filtered_errors)
    
    def test_error_details_captured(self):
        """✅ TEST: Error details (unit, code, message) are captured"""
        log_content = "SCHEMA.PACKAGE_NAME - execution\nORA-00955: name is already used"
        self.main_log.write_text(log_content)
        self.invalid_log.write_text("Number of invalids at start: 0\nNumber of invalids at end: 0")
        
        validator = DeploymentValidator(self.metadata, self.config)
        result = validator.validate_all()
        
        # Error should be detected
        self.assertTrue(len(validator.error_details) > 0)
        # Unit should be extracted
        self.assertEqual(validator.error_details[0]["unit"], "PACKAGE_NAME")
    
    def test_invalid_delta_validation_match(self):
        """✅ TEST: Valid invalid delta passes validation"""
        self.main_log.write_text("Compilation successful")
        self.invalid_log.write_text("Number of invalids at start: 5\nNumber of invalids at end: 5")
        
        validator = DeploymentValidator(self.metadata, self.config)
        result = validator.validate_invalid_delta()
        
        self.assertTrue(result)
        self.assertFalse(validator.invalid_mismatch)
    
    def test_invalid_delta_mismatch(self):
        """✅ TEST: Invalid delta mismatch is detected"""
        self.main_log.write_text("Compilation successful")
        self.invalid_log.write_text("Number of invalids at start: 5\nNumber of invalids at end: 8")
        
        validator = DeploymentValidator(self.metadata, self.config)
        result = validator.validate_invalid_delta()
        
        self.assertFalse(result)
        self.assertTrue(validator.invalid_mismatch)
    
    def test_execution_integrity_valid(self):
        """✅ TEST: Valid execution start/end is detected"""
        log_content = """
SCHEMA.PKG1 - execution start
SCHEMA.PKG1 - execution end
SCHEMA.PKG2 - execution start
SCHEMA.PKG2 - execution end
        """
        self.main_log.write_text(log_content)
        self.invalid_log.write_text("Number of invalids at start: 0\nNumber of invalids at end: 0")
        
        validator = DeploymentValidator(self.metadata, self.config)
        result = validator.validate_execution_integrity()
        
        self.assertTrue(result)
    
    def test_execution_integrity_mismatch(self):
        """✅ TEST: Execution start/end mismatch is detected"""
        log_content = """
SCHEMA.PKG1 - execution start
SCHEMA.PKG1 - execution start
SCHEMA.PKG1 - execution end
        """
        self.main_log.write_text(log_content)
        self.invalid_log.write_text("Number of invalids at start: 0\nNumber of invalids at end: 0")
        
        validator = DeploymentValidator(self.metadata, self.config)
        result = validator.validate_execution_integrity()
        
        self.assertFalse(result)
    
    # ============ NEGATIVE TESTS ============
    
    def test_missing_main_log_file(self):
        """❌ TEST: Handle missing main log file"""
        self.invalid_log.write_text("Number of invalids at start: 0\nNumber of invalids at end: 0")
        
        validator = DeploymentValidator(self.metadata, self.config)
        with self.assertRaises(FileNotFoundError):
            validator.validate_errors()
    
    def test_missing_invalid_log_file(self):
        """❌ TEST: Handle missing invalid log file"""
        self.main_log.write_text("OK")
        
        validator = DeploymentValidator(self.metadata, self.config)
        with self.assertRaises(FileNotFoundError):
            validator.validate_invalid_delta()
    
    def test_malformed_invalid_counts(self):
        """❌ TEST: Handle malformed invalid count lines"""
        self.main_log.write_text("OK")
        self.invalid_log.write_text("Invalid log without proper format")
        
        validator = DeploymentValidator(self.metadata, self.config)
        result = validator.validate_invalid_delta()
        
        self.assertFalse(result)  # Should fail if counts not found
    
    def test_empty_log_files(self):
        """❌ TEST: Handle completely empty log files"""
        self.main_log.write_text("")
        self.invalid_log.write_text("")
        
        validator = DeploymentValidator(self.metadata, self.config)
        result = validator.validate_all()
        
        # Should handle gracefully (might be PASS or FAIL depending on requirements)
        self.assertIsNotNone(result)
    
    def test_multiple_error_codes_in_one_line(self):
        """❌ TEST: Handle multiple error codes in single line"""
        self.main_log.write_text("Found errors: ORA-00001 and ORA-12514 in same line")
        self.invalid_log.write_text("Number of invalids at start: 0\nNumber of invalids at end: 0")
        
        validator = DeploymentValidator(self.metadata, self.config)
        result = validator.validate_errors()
        
        # Should capture ORA-00001
        self.assertIn("ORA-00001", validator.detected_errors)


class TestCycleManager(unittest.TestCase):
    """POSITIVE & NEGATIVE TESTS: Cycle Manager Module"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.base_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Cleanup"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cycle_manager_generates_cycle_name(self):
        """✅ TEST: Generate cycle name with timestamp"""
        manager = CycleManager(self.base_path)
        cycle_name = manager.generate_cycle_name()
        
        self.assertIsNotNone(cycle_name)
        self.assertIn("_20", cycle_name)  # Date portion
        self.assertIn("_", cycle_name)
    
    def test_cycle_manager_creates_folder(self):
        """✅ TEST: Create cycle folder"""
        manager = CycleManager(self.base_path)
        cycle_name = manager.generate_cycle_name()
        cycle_folder = manager.ensure_cycle_folder(cycle_name)
        
        self.assertTrue(cycle_folder.exists())
        self.assertTrue(cycle_folder.is_dir())
    
    def test_cycle_manager_idempotent(self):
        """✅ TEST: Creating same cycle folder twice doesn't fail"""
        manager = CycleManager(self.base_path)
        cycle_name = manager.generate_cycle_name()
        
        folder1 = manager.ensure_cycle_folder(cycle_name)
        folder2 = manager.ensure_cycle_folder(cycle_name)
        
        self.assertEqual(folder1, folder2)
        self.assertTrue(folder1.exists())
    
    def test_cycle_manager_invalid_base_path(self):
        """❌ TEST: Handle invalid base path"""
        invalid_path = Path("/nonexistent/path/that/does/not/exist")
        manager = CycleManager(invalid_path)
        
        # Should handle gracefully or raise appropriate error
        with self.assertRaises((FileNotFoundError, OSError)):
            manager.ensure_cycle_folder("test_cycle")


class TestConfiguration(unittest.TestCase):
    """POSITIVE & NEGATIVE TESTS: Configuration Validation"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.config_path = Path(__file__).parent.parent / "config.json"
    
    def test_config_file_exists(self):
        """✅ TEST: Config file exists"""
        self.assertTrue(self.config_path.exists())
    
    def test_config_valid_json(self):
        """✅ TEST: Config file is valid JSON"""
        try:
            with open(self.config_path) as f:
                config = json.load(f)
            self.assertIsInstance(config, dict)
        except json.JSONDecodeError:
            self.fail("Config file is not valid JSON")
    
    def test_config_has_required_fields(self):
        """✅ TEST: Config has all required fields"""
        with open(self.config_path) as f:
            config = json.load(f)
        
        required_fields = ["base_audit_path", "poll_interval_seconds", "clusters", "ignorable_errors", "email_settings"]
        for field in required_fields:
            self.assertIn(field, config)
    
    def test_config_email_settings_structure(self):
        """✅ TEST: Email settings have correct structure"""
        with open(self.config_path) as f:
            config = json.load(f)
        
        email = config["email_settings"]
        self.assertIn("enabled", email)
        self.assertIn("recipients", email)
        self.assertIn("subject_templates", email)
        self.assertIn("body_template", email)
        self.assertIsInstance(email["recipients"], list)
    
    def test_config_clusters_valid(self):
        """✅ TEST: Clusters configuration is valid"""
        with open(self.config_path) as f:
            config = json.load(f)
        
        clusters = config["clusters"]
        self.assertIsInstance(clusters, dict)
        
        # Each cluster should have a list of instances
        for cluster_name, instances in clusters.items():
            self.assertIsInstance(instances, list)
            self.assertTrue(len(instances) > 0)


class TestIntegration(unittest.TestCase):
    """INTEGRATION TESTS: End-to-End Flows"""
    
    def setUp(self):
        """Setup test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "ignorable_errors": ["ORA-00001"],
            "email_settings": {
                "enabled": False,
                "recipients": [],
                "subject_templates": {},
                "body_template": ""
            }
        }
    
    def tearDown(self):
        """Cleanup"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_full_validation_flow_pass(self):
        """✅ TEST: Full validation flow - PASS case"""
        # Create log files
        main_log = Path(self.temp_dir) / "main.log"
        invalid_log = Path(self.temp_dir) / "invalids.log"
        error_log = Path(self.temp_dir) / "error.log"
        
        main_log.write_text("SCHEMA.PKG - execution\nCompilation successful")
        invalid_log.write_text("Number of invalids at start: 0\nNumber of invalids at end: 0")
        error_log.write_text("")
        
        metadata = {
            "main_log_path": main_log,
            "invalid_log_path": invalid_log,
            "error_log_path": error_log
        }
        
        validator = DeploymentValidator(metadata, self.config)
        result = validator.validate_all()
        
        self.assertEqual(result["status"], "PASS")
        self.assertIn("successfully", result["message"].lower())
    
    def test_full_validation_flow_fail(self):
        """✅ TEST: Full validation flow - FAIL case"""
        main_log = Path(self.temp_dir) / "main.log"
        invalid_log = Path(self.temp_dir) / "invalids.log"
        
        main_log.write_text("ORA-12514: listener not available")
        invalid_log.write_text("Number of invalids at start: 0\nNumber of invalids at end: 0")
        
        metadata = {
            "main_log_path": main_log,
            "invalid_log_path": invalid_log,
            "error_log_path": None
        }
        
        validator = DeploymentValidator(metadata, self.config)
        result = validator.validate_all()
        
        self.assertEqual(result["status"], "FAIL")
        self.assertIn("error", result["message"].lower())


# ============ TEST RUNNER ============

if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
