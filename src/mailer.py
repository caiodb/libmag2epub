"""
Modern mailer module with retry mechanism and proper EmailMessage usage.
"""

import os
import time
import smtplib
from pathlib import Path
from email.message import EmailMessage
from typing import List, Optional

from src.config import (
    MAIL,
    SEC,
    KINDLE_EMAILS,
    SMTP_HOST,
    SMTP_PORT,
    SMTP_MAX_RETRIES,
    SMTP_RETRY_DELAY,
)


class Mailer:
    """Handles sending EPUB files via email with retry mechanism."""
    
    def __init__(self):
        self.sender = MAIL
        self.password = SEC
        self.recipients = KINDLE_EMAILS
        self.max_retries = SMTP_MAX_RETRIES
        self.retry_delay = SMTP_RETRY_DELAY
    
    def send_epub(self, epub_path: Path) -> bool:
        """
        Send an EPUB file to all configured recipients.
        
        Args:
            epub_path: Path to the EPUB file
            
        Returns:
            bool: True if at least one email was sent successfully
        """
        if not self._validate_setup(epub_path):
            return False
        
        success_count = 0
        last_error = None
        
        # Try to connect with retries
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"Connecting to SMTP server (attempt {attempt}/{self.max_retries})...")
                
                with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                    server.login(self.sender, self.password)
                    print(f"Connected as {self.sender}")
                    
                    # Send to each recipient
                    for recipient in self.recipients:
                        try:
                            if self._send_single_email(server, epub_path, recipient):
                                success_count += 1
                        except Exception as e:
                            print(f"  ! Failed to send to {recipient}: {e}")
                
                # If we got here, connection and sending succeeded
                print(f"✓ Finished. Successfully delivered to {success_count}/{len(self.recipients)} recipients.")
                return success_count > 0
                
            except Exception as e:
                last_error = e
                print(f"  ! SMTP connection error (attempt {attempt}): {e}")
                
                if attempt < self.max_retries:
                    print(f"  Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print(f"  X All {self.max_retries} attempts failed.")
        
        print(f"X SMTP Error: {last_error}")
        return False
    
    def _validate_setup(self, epub_path: Path) -> bool:
        """
        Validate that all required configuration is present.
        
        Args:
            epub_path: Path to the EPUB file
            
        Returns:
            bool: True if setup is valid
        """
        if not epub_path.exists():
            print(f"Error: File '{epub_path}' not found.")
            return False
        
        if not self.sender or not self.password:
            print("Error: Email credentials not configured. Check MAIL and SEC in .env")
            return False
        
        if not self.recipients:
            print("Error: No recipient emails found in .env (KINDLE_EMAILS).")
            return False
        
        return True
    
    def _send_single_email(
        self, 
        server: smtplib.SMTP_SSL, 
        epub_path: Path, 
        recipient: str
    ) -> bool:
        """
        Send a single email with EPUB attachment.
        
        Args:
            server: Connected SMTP server
            epub_path: Path to the EPUB file
            recipient: Recipient email address
            
        Returns:
            bool: True if email was sent successfully
        """
        print(f"-> Sending to: {recipient}")
        
        # Create email message
        msg = EmailMessage()
        msg['Subject'] = "Liberta Magazine"
        msg['From'] = self.sender
        msg['To'] = recipient
        msg.set_content("Your requested magazine is attached.")
        
        # Read and attach the EPUB file
        with open(epub_path, 'rb') as f:
            file_data = f.read()
            msg.add_attachment(
                file_data,
                maintype='application',
                subtype='epub+zip',
                filename=epub_path.name
            )
        
        # Send the email
        server.send_message(msg)
        print(f"  ✓ Sent successfully to {recipient}")
        return True


# Convenience function
def send_via_gmail(epub_path: Path) -> bool:
    """
    Send an EPUB file via Gmail SMTP.
    
    Args:
        epub_path: Path to the EPUB file
        
    Returns:
        bool: True if at least one email was sent successfully
    """
    mailer = Mailer()
    return mailer.send_epub(Path(epub_path))
