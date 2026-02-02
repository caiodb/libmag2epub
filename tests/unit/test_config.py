"""
Unit tests for the config module.
Run with: python -m pytest tests/unit/test_config.py -v
"""

import pytest
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import (
    PROJECT_ROOT,
    RAW_DIR,
    EBOOK_DIR,
    SENT_DIR,
    BASE_URL,
    INDEX_URL,
    LOGIN_URL,
    HTTP_TIMEOUT,
    PLAYWRIGHT_TIMEOUT,
)


class TestConfigPaths:
    """Test path configurations."""
    
    def test_project_root_exists(self):
        """Verify PROJECT_ROOT points to existing directory."""
        assert PROJECT_ROOT.exists()
        assert PROJECT_ROOT.is_dir()
    
    def test_raw_dir_is_path_object(self):
        """Verify RAW_DIR is a Path object."""
        assert isinstance(RAW_DIR, Path)
        assert RAW_DIR.name == "raw"
    
    def test_ebook_dir_is_path_object(self):
        """Verify EBOOK_DIR is a Path object."""
        assert isinstance(EBOOK_DIR, Path)
        assert EBOOK_DIR.name == "ebook"
    
    def test_sent_dir_is_path_object(self):
        """Verify SENT_DIR is a Path object."""
        assert isinstance(SENT_DIR, Path)
        assert SENT_DIR.name == "sent"


class TestConfigUrls:
    """Test URL configurations."""
    
    def test_base_url_is_valid(self):
        """Verify BASE_URL is a valid HTTPS URL."""
        assert BASE_URL.startswith("https://")
        assert "revistaliberta.com.br" in BASE_URL
    
    def test_index_url_composed_correctly(self):
        """Verify INDEX_URL is correctly composed."""
        assert INDEX_URL.startswith(BASE_URL)
        assert "edicoes" in INDEX_URL
    
    def test_login_url_composed_correctly(self):
        """Verify LOGIN_URL is correctly composed."""
        assert LOGIN_URL.startswith(BASE_URL)
        assert "login" in LOGIN_URL


class TestConfigTimeouts:
    """Test timeout configurations."""
    
    def test_http_timeout_is_positive(self):
        """Verify HTTP timeout is a positive number."""
        assert isinstance(HTTP_TIMEOUT, int)
        assert HTTP_TIMEOUT > 0
        assert HTTP_TIMEOUT == 30  # Expected value
    
    def test_playwright_timeout_is_positive(self):
        """Verify Playwright timeout is a positive number."""
        assert isinstance(PLAYWRIGHT_TIMEOUT, int)
        assert PLAYWRIGHT_TIMEOUT > 0


class TestConfigSelectors:
    """Test CSS selector configurations."""
    
    def test_edition_links_selector_exists(self):
        """Verify edition links selector is defined."""
        from src.config import SELECTOR_EDITION_LINKS
        assert SELECTOR_EDITION_LINKS
        assert isinstance(SELECTOR_EDITION_LINKS, str)
    
    def test_cover_image_selector_exists(self):
        """Verify cover image selector is defined."""
        from src.config import SELECTOR_COVER_IMAGE
        assert SELECTOR_COVER_IMAGE
        assert isinstance(SELECTOR_COVER_IMAGE, str)
    
    def test_author_container_selector_exists(self):
        """Verify author container selector is defined."""
        from src.config import SELECTOR_AUTHOR_CONTAINER
        assert SELECTOR_AUTHOR_CONTAINER
        assert isinstance(SELECTOR_AUTHOR_CONTAINER, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
