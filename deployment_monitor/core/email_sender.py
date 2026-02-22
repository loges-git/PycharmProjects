"""
Email Sender Module
Sends deployment validation summary emails via Outlook COM
"""

import win32com.client
import logging
import time
from functools import wraps
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger("deployment_monitor.email_sender")


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """
    Decorator for retry logic with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (exponential growth: 1, 2, 4, 8...)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (OSError, AttributeError) as e:
                    if attempt < max_retries:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                            f"Retrying in {delay}s..."
                        )
                        time.sleep(delay)
                    else:
                        logger.error(f"All {max_retries + 1} retry attempts failed. Giving up.")
                        raise
        return wrapper
    return decorator


class EmailSender:
    """
    Sends deployment summary emails using Outlook COM.
    Safe, requires no server authentication, uses logged-in user session.
    """

    def __init__(self, config: dict):
        """
        Initialize EmailSender with configuration and validate templates.
        
        Args:
            config: Full config dict containing email_settings
            
        Raises:
            ValueError: If templates missing required placeholders
        """
        try:
            self.config = config
            self.email_config = config.get("email_settings", {})
            self.enabled = self.email_config.get("enabled", False)
            self.recipients = self.email_config.get("recipients", [])
            self.subject_templates = self.email_config.get("subject_templates", {})
            self.body_template = self.email_config.get("body_template", "")
            
            logger.info(f"EmailSender initialized - enabled={self.enabled}, recipients={len(self.recipients)}")
            
            # Validate templates if enabled
            if self.enabled:
                self._validate_templates()
                logger.info("Email templates validated successfully")
        
        except ValueError as e:
            logger.error(f"Template validation failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during EmailSender initialization: {e}")
            raise
    
    def _validate_templates(self) -> None:
        """Validate that templates contain essential placeholders.
        
        Subject: Must have at least cluster and instance
        Body: Must have status (can have message for details)
        """
        import string
        
        # Check subject templates
        if not self.subject_templates:
            raise ValueError("No subject_templates configured in email_settings")
        
        for status, template in self.subject_templates.items():
            if not isinstance(template, str):
                raise ValueError(f"Subject template for {status} is not a string")
            
            # Subject should have cluster and instance at minimum
            placeholders = set(field_name for _, field_name, _, _ in string.Formatter().parse(template) if field_name)
            required = {"cluster", "instance"}
            missing = required - placeholders
            
            if missing:
                logger.warning(f"Subject template for {status} missing placeholders: {missing}")
        
        # Check body template
        if not self.body_template:
            raise ValueError("body_template is empty in email_settings")
        
        placeholders = set(field_name for _, field_name, _, _ in string.Formatter().parse(self.body_template) if field_name)
        # Body should have at least status and message
        if not ("status" in placeholders or "message" in placeholders):
            raise ValueError("body_template must have at least {status} or {message} placeholder")

    def build_subject(self, status: str, cluster: str, instance: str) -> str:
        """
        Build email subject from template using placeholders.
        
        Args:
            status: "PASS" or "FAIL"
            cluster: Cluster name (e.g., "MENA")
            instance: Instance name (e.g., "FSMHO1U")
            
        Returns:
            Formatted subject line
            
        Raises:
            KeyError: If required placeholder missing from template
        """
        try:
            template = self.subject_templates.get(status, "Deployment Validation - {status}")
            
            subject = template.format(
                status=status,
                cluster=cluster,
                instance=instance
            )
            
            logger.debug(f"Subject built for {status}: {subject}")
            return subject
        
        except KeyError as e:
            logger.error(f"Missing placeholder in subject template for {status}: {e}")
            raise ValueError(f"Subject template for {status} has invalid placeholder: {e}")
        except Exception as e:
            logger.error(f"Error building subject for {status}: {e}")
            raise

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
            
        Raises:
            KeyError: If required placeholder missing from template
        """
        try:
            body = self.body_template.format(
                status=status,
                cluster=cluster,
                instance=instance,
                message=message
            )
            
            logger.debug(f"Body built for {status} - {cluster}/{instance}")
            return body
        
        except KeyError as e:
            logger.error(f"Missing placeholder in body template: {e}")
            raise ValueError(f"Body template has invalid placeholder: {e}")
        except Exception as e:
            logger.error(f"Error building body: {e}")
            raise

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def send_mail(self, subject: str, body: str) -> tuple[bool, str]:
        """
        Send email via Outlook COM with automatic retry on transient failures.
        
        Args:
            subject: Email subject
            body: Email body
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.enabled:
            logger.info("Email notification disabled in config")
            return False, "Email notification disabled in config"

        if not self.recipients:
            logger.error("No recipients configured for email")
            return False, "No recipients configured"

        try:
            logger.info(f"Preparing to send email to {len(self.recipients)} recipients")
            
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
            success_msg = f"Email sent to: {recipient_list}"
            logger.info(success_msg)
            return True, success_msg

        except OSError as e:
            error_msg = f"Outlook COM error (ensure Outlook is running): {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except AttributeError as e:
            error_msg = f"Invalid email object structure: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error sending email: {str(e)}"
            logger.error(error_msg, exc_info=True)
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
        try:
            logger.info(f"Building deployment summary email for {cluster}/{instance} - {status}")
            
            subject = self.build_subject(status, cluster, instance)
            body = self.build_body(status, cluster, instance, message)
            
            success, msg = self.send_mail(subject, body)
            return success, msg
        
        except ValueError as e:
            error_msg = f"Template validation error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error building deployment summary: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg
