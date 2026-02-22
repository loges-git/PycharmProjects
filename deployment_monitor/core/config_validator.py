"""
Configuration Validator Module
Validates config.json for production readiness
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


class ConfigValidator:
    """Validates deployment monitor configuration"""
    
    REQUIRED_FIELDS = ["base_audit_path", "poll_interval_seconds", "clusters", "ignorable_errors"]
    EMAIL_REQUIRED_FIELDS = ["enabled", "recipients", "subject_templates", "body_template"]
    
    def __init__(self, config: Dict):
        """Initialize with config dict"""
        self.config = config
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """
        Run all validation checks.
        
        Returns:
            Tuple of (is_valid, errors, warnings)
        """
        self._validate_required_fields()
        self._validate_base_paths()
        self._validate_poll_interval()
        self._validate_clusters()
        self._validate_email_settings()
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _validate_required_fields(self):
        """Check for required top-level fields"""
        for field in self.REQUIRED_FIELDS:
            if field not in self.config:
                self.errors.append(f"Missing required field: {field}")
    
    def _validate_base_paths(self):
        """Validate base_audit_path exists and is accessible"""
        if "base_audit_path" not in self.config:
            return
        
        path = self.config["base_audit_path"]
        try:
            base_path = Path(path)
            if not base_path.exists():
                self.warnings.append(f"base_audit_path does not exist: {path}")
            elif not base_path.is_dir():
                self.errors.append(f"base_audit_path is not a directory: {path}")
        except Exception as e:
            self.errors.append(f"Invalid base_audit_path: {e}")
    
    def _validate_poll_interval(self):
        """Validate poll interval is valid"""
        if "poll_interval_seconds" not in self.config:
            return
        
        try:
            interval = int(self.config["poll_interval_seconds"])
            if interval <= 0:
                self.errors.append(f"poll_interval_seconds must be > 0, got {interval}")
            elif interval < 5:
                self.warnings.append("poll_interval_seconds < 5 may cause high CPU usage")
        except (ValueError, TypeError):
            self.errors.append(f"poll_interval_seconds must be integer, got {type(self.config['poll_interval_seconds'])}")
    
    def _validate_clusters(self):
        """Validate cluster configuration"""
        if "clusters" not in self.config:
            return
        
        clusters = self.config["clusters"]
        if not isinstance(clusters, dict):
            self.errors.append("clusters must be a dictionary")
            return
        
        for cluster_name, instances in clusters.items():
            if not isinstance(instances, list):
                self.errors.append(f"cluster '{cluster_name}' must have list of instances")
            elif len(instances) == 0:
                self.errors.append(f"cluster '{cluster_name}' has no instances")
    
    def _validate_email_settings(self):
        """Validate email configuration"""
        if "email_settings" not in self.config:
            self.warnings.append("No email_settings configured")
            return
        
        email = self.config["email_settings"]
        if not isinstance(email, dict):
            self.errors.append("email_settings must be a dictionary")
            return
        
        # Check required email fields
        for field in self.EMAIL_REQUIRED_FIELDS:
            if field not in email:
                self.errors.append(f"Missing email_settings.{field}")
        
        # Validate recipients
        if "recipients" in email:
            recipients = email["recipients"]
            if not isinstance(recipients, list):
                self.errors.append("email_settings.recipients must be a list")
            else:
                for recipient in recipients:
                    if not self._is_valid_email(recipient):
                        self.warnings.append(f"Invalid email format: {recipient}")
        
        # Validate templates
        if "subject_templates" in email:
            templates = email["subject_templates"]
            if not isinstance(templates, dict):
                self.errors.append("subject_templates must be a dictionary")
            else:
                for status, template in templates.items():
                    self._validate_template(f"subject_templates[{status}]", template, status)
        
        if "body_template" in email:
            self._validate_template("body_template", email["body_template"], "PASS")
    
    def _validate_template(self, field_name: str, template: str, status: str):
        """Validate email template has required placeholders"""
        required_placeholders = {"status", "cluster", "instance", "message"}
        
        if not isinstance(template, str):
            self.errors.append(f"{field_name} must be string")
            return
        
        found_placeholders = set(re.findall(r'\{(\w+)\}', template))
        missing = required_placeholders - found_placeholders
        
        if missing:
            self.errors.append(f"{field_name} missing placeholders: {', '.join(missing)}")
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Check if email format is valid"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
