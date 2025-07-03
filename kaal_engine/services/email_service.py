"""
Email Service for Brahmakaal Enterprise API
SMTP-based email delivery with templates and queue support
"""

import smtplib
import ssl
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Dict, Any
from jinja2 import Environment, FileSystemLoader
import asyncio
from concurrent.futures import ThreadPoolExecutor
import secrets
from pathlib import Path

from ..config import get_settings

settings = get_settings()

class EmailTemplate:
    """Email template definitions"""
    
    WELCOME = "welcome"
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"
    SUBSCRIPTION_WELCOME = "subscription_welcome"
    SUBSCRIPTION_UPDATED = "subscription_updated"
    SUBSCRIPTION_EXPIRED = "subscription_expired"
    USAGE_ALERT = "usage_alert"
    API_KEY_CREATED = "api_key_created"

class EmailService:
    """Email service for authentication and notifications"""
    
    def __init__(self):
        self.smtp_host = "smtp.zoho.in"
        self.smtp_port = 465
        self.smtp_user = "aham@brah.ma"
        self.smtp_pass = "6whrzKc*@brahma"
        self.smtp_secure = True
        self.from_email = "aham@brah.ma"
        self.from_name = "Brahmakaal Team"
        
        # Template environment
        template_dir = Path(__file__).parent / "templates"
        template_dir.mkdir(exist_ok=True)
        
        # Thread pool for async email sending
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        print(f"✅ Email service initialized with {self.smtp_host}")
    
    async def send_email_async(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send email asynchronously"""
        loop = asyncio.get_event_loop()
        
        try:
            result = await loop.run_in_executor(
                self.executor,
                self._send_email_sync,
                to_email,
                subject,
                html_body,
                text_body,
                attachments
            )
            return result
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            return False
    
    def _send_email_sync(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send email synchronously"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject
            msg['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S +0000')
            
            # Add text version if provided
            if text_body:
                text_part = MIMEText(text_body, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Add HTML version
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    self._add_attachment(msg, attachment)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context) as server:
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)
            
            print(f"✅ Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send email to {to_email}: {e}")
            return False
    
    def _add_attachment(self, msg: MIMEMultipart, attachment: Dict[str, Any]):
        """Add attachment to email message"""
        try:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment['data'])
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment["filename"]}'
            )
            msg.attach(part)
        except Exception as e:
            print(f"⚠️ Failed to add attachment {attachment.get('filename', 'unknown')}: {e}")

# Global email service instance
email_service = EmailService()
