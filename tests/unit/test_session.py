"""
Unit tests for the session module.
Run with: python -m pytest tests/unit/test_session.py -v
"""

import pytest
import pytest_asyncio
from pathlib import Path
import sys
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.session import SessionManager


class TestSessionManager:
    """Test SessionManager functionality."""
    
    def test_session_manager_creation(self):
        """Verify SessionManager can be instantiated."""
        manager = SessionManager()
        assert manager is not None
        assert manager._context is None
    
    @pytest.mark.asyncio
    async def test_cleanup_without_context(self):
        """Verify cleanup doesn't fail when no context exists."""
        manager = SessionManager()
        # Should not raise any exceptions
        await manager.cleanup()


class TestCredentials:
    """Test credential loading from environment."""
    
    def test_liber_user_loaded(self):
        """Verify LIBER_USER is loaded from environment."""
        from src.config import LIBER_USER
        # Should be a string (may be empty if .env not loaded)
        assert isinstance(LIBER_USER, str)
    
    def test_liber_pass_loaded(self):
        """Verify LIBER_PASS is loaded from environment."""
        from src.config import LIBER_PASS
        assert isinstance(LIBER_PASS, str)
    
    def test_mail_config_loaded(self):
        """Verify MAIL is loaded from environment."""
        from src.config import MAIL
        assert isinstance(MAIL, str)
    
    def test_kindle_emails_is_list(self):
        """Verify KINDLE_EMAILS is a list."""
        from src.config import KINDLE_EMAILS
        assert isinstance(KINDLE_EMAILS, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
