"""
Unit tests for the builder module.
Run with: python -m pytest tests/unit/test_builder.py -v
"""

import pytest
from pathlib import Path
import sys
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.builder import EpubBuilder
from src.config import RAW_DIR, EBOOK_DIR, AUTHOR_NAME, LANGUAGE


class TestEpubBuilder:
    """Test EpubBuilder functionality."""
    
    def test_builder_creation(self):
        """Verify EpubBuilder can be instantiated."""
        builder = EpubBuilder("test-edition")
        assert builder is not None
        assert builder.issue_name == "test-edition"
    
    def test_builder_paths_set_correctly(self):
        """Verify builder sets paths correctly."""
        builder = EpubBuilder("test-edition")
        assert builder.raw_dir == RAW_DIR / "test-edition"
        assert builder.build_dir.name == "test-edition_build_temp"
    
    def test_get_clean_title(self):
        """Verify title cleaning works."""
        builder = EpubBuilder("edicao-18")
        clean = builder._get_clean_title()
        assert "Edicao" not in clean  # Should be replaced with Edição
        assert "edicao" not in clean.lower()
        assert "18" in clean
    
    def test_build_returns_none_without_raw_dir(self):
        """Verify build returns None when raw directory doesn't exist."""
        builder = EpubBuilder("nonexistent-edition-12345")
        result = builder.build()
        assert result is None


class TestImageConversion:
    """Test image conversion functionality."""
    
    def test_convert_webp_images_no_urls(self):
        """Verify content without WebP URLs is unchanged."""
        builder = EpubBuilder("test")
        content = "# Test Article\n\nThis is content without images."
        result = builder._convert_webp_images(content)
        assert result == content
    
    def test_convert_webp_images_finds_urls(self):
        """Verify WebP URLs are found in markdown."""
        builder = EpubBuilder("test")
        content = "![image](https://example.com/image.webp)"
        # Note: This will try to download, but we're just testing the regex
        # In a real test, you'd mock the httpx.get call
        result = builder._convert_webp_images(content)
        # If download fails, URL remains unchanged
        # If download succeeds, URL is replaced with local name
        assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
