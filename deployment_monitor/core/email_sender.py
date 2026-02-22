"""
Email Sender Module
Sends deployment validation summary emails via Outlook COM
"""

import win32com.client
from pathlib import Path
from typing import Dict, List, Optional


class EmailSender:
    """
    Sends deployment summary emails using Outlook COM.
    Safe, requires no server authentication, uses logged-in user session.
    """

    def __init__(self, config: dict):
        """
        Initialize EmailSender with configuration.
        
        Args:
            config: Full config dict containing email_settings
        """
        self.config = config
        self.email_config = config.get("email_settings", {})
        self.enabled = self.email_config.get("enabled", False)
        self.recipients = self.email_config.get("recipients", [])
        self.subject_templates = self.email_config.get("subject_templates", {})
        self.body_template = self.email_config.get("body_template", "")

    def build_subject(self, status: str, cluster: str, instance: str) -> str:
        """
        Build email subject from template using placeholders.
        
        Args:
            status: "PASS" or "FAIL"
            cluster: Cluster name (e.g., "MENA")
            instance: Instance name (e.g., "FSMHO1U")
            
        Returns:
            Formatted subject line
        """
        template = self.subject_templates.get(status, "Deployment Validation - {status}")
        
        return template.format(
            status=status,
            cluster=cluster,
            instance=instance
        )

    def build_body(self, status: str, cluster: str, instance: str, message: str) -> str:
        """
        Build email body from template using placeholders.
        
        Args:
            status: "PASS" or "FAIL"
            cluster: Cluster name
            instance: Instance name
            message: Validation message/details
            
        Returns:
            Formatted body text
        """
        return self.body_template.format(
            status=status,
            cluster=cluster,
            instance=instance,
            message=message
        )

    def send_mail(self, subject: str, body: str) -> tuple[bool, str]:
        """
        Send email via Outlook COM.
        
        Args:
            subject: Email subject
            body: Email body
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.enabled:
            return False, "Email notification disabled in config"

        if not self.recipients:
            return False, "No recipients configured"

        try:
            # Create Outlook COM object
            outlook = win32com.client.Dispatch("Outlook.Application")
            
            # Create new mail item
            mail = outlook.CreateItem(0)  # 0 = OlMailItem
            
            # Set recipients
            mail.To = ";".join(self.recipients)
            
            # Set subject and body
            mail.Subject = subject
            mail.Body = body
            
            # Send (no Outlook dialog required for same-session)
            mail.Send()
            
            recipient_list = ", ".join(self.recipients)
            return True, f"Email sent to: {recipient_list}"

        except Exception as e:
            error_msg = f"Failed to send email: {str(e)}"
            return False, error_msg

    def send_deployment_summary(self, status: str, cluster: str, instance: str, message: str) -> tuple[bool, str]:
        """
        Send deployment validation summary email.
        
        Args:
            status: "PASS" or "FAIL"
            cluster: Cluster name
            instance: Instance name
            message: Validation message
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        subject = self.build_subject(status, cluster, instance)
        body = self.build_body(status, cluster, instance, message)
        
        return self.send_mail(subject, body)
