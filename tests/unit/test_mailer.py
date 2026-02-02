"""
Unit tests for the mailer module.
Run with: python -m pytest tests/unit/test_mailer.py -v
"""

import pytest
from pathlib import Path
import sys
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.mailer import Mailer, send_via_gmail
from src.config import SMTP_MAX_RETRIES, SMTP_RETRY_DELAY


class TestMailer:
    """Test Mailer functionality."""
    
    def test_mailer_creation(self):
        """Verify Mailer can be instantiated."""
        mailer = Mailer()
        assert mailer is not None
        assert mailer.max_retries == SMTP_MAX_RETRIES
    
    def test_validate_setup_with_missing_file(self):
        """Verify validate_setup returns False for non-existent file."""
        mailer = Mailer()
        result = mailer._validate_setup(Path("/nonexistent/path/file.epub"))
        assert result is False
    
    @patch('smtplib.SMTP_SSL')
    def test_send_single_email_success(self, mock_smtp_class):
        """Verify email can be sent successfully."""
        mailer = Mailer()
        mailer.sender = "test@example.com"
        
        mock_server = MagicMock()
        mock_smtp_class.return_value.__enter__ = Mock(return_value=mock_server)
        mock_smtp_class.return_value.__exit__ = Mock(return_value=False)
        
        # Create a temporary file for testing
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.epub', delete=False) as f:
            f.write(b"fake epub content")
            temp_path = Path(f.name)
        
        try:
            result = mailer._send_single_email(mock_server, temp_path, "recipient@example.com")
            assert result is True
            mock_server.send_message.assert_called_once()
        finally:
            temp_path.unlink()


class TestSendViaGmail:
    """Test send_via_gmail convenience function."""
    
    def test_send_via_gmail_with_nonexistent_file(self):
        """Verify function returns False for non-existent file."""
        result = send_via_gmail(Path("/nonexistent/file.epub"))
        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
