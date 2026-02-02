"""
Integration tests for the full pipeline.
Run with: python -m pytest tests/integration/test_pipeline.py -v

Note: These tests may require network access and valid credentials.
Use --dry-run flag or mock external dependencies for CI/CD.
"""

import pytest
import pytest_asyncio
from pathlib import Path
import sys
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.orchestrator import PipelineOrchestrator
from src.scraper import IndexScraper
from src.builder import EpubBuilder
from src.mailer import Mailer


@pytest.mark.integration
class TestPipelineIntegration:
    """Integration tests requiring network/credentials."""
    
    @pytest.mark.asyncio
    async def test_orchestrator_creation(self):
        """Verify orchestrator can be created."""
        orchestrator = PipelineOrchestrator()
        assert orchestrator is not None
        assert orchestrator.index_scraper is not None
    
    @pytest.mark.asyncio
    async def test_index_scraper_creation(self):
        """Verify IndexScraper can be created."""
        scraper = IndexScraper()
        assert scraper is not None
    
    def test_epub_builder_with_mock_raw_data(self):
        """Test builder with mock raw data directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create mock raw directory structure
            raw_dir = Path(temp_dir) / "test-edition"
            raw_dir.mkdir()
            
            # Create a mock cover image
            from PIL import Image
            cover = Image.new('RGB', (100, 150), color='red')
            cover.save(raw_dir / "cover.jpg")
            
            # Create a mock article
            article = raw_dir / "artigo_00.md"
            article.write_text("# Test Article\n\nThis is test content.")
            
            # Temporarily override RAW_DIR
            import src.builder
            original_raw_dir = src.builder.RAW_DIR
            src.builder.RAW_DIR = Path(temp_dir)
            
            try:
                builder = EpubBuilder("test-edition")
                # Build should fail because pandoc isn't available in test environment
                # But we can verify the setup worked
                assert builder.raw_dir.exists()
            finally:
                src.builder.RAW_DIR = original_raw_dir


class TestDryRunPipeline:
    """Tests that don't require network or credentials."""
    
    def test_directory_structure(self):
        """Verify required directories exist."""
        from src.config import PROJECT_ROOT, RAW_DIR, EBOOK_DIR, SENT_DIR
        
        assert PROJECT_ROOT.exists()
        assert (PROJECT_ROOT / "src").exists()
        assert (PROJECT_ROOT / "main.py").exists()
    
    def test_config_imports(self):
        """Verify all config values can be imported."""
        from src.config import (
            PROJECT_ROOT, RAW_DIR, EBOOK_DIR, SENT_DIR, SRC_DIR, DOCS_DIR,
            BASE_URL, INDEX_URL, LOGIN_URL,
            LIBER_USER, LIBER_PASS, MAIL, SEC, KINDLE_EMAILS,
            SELECTOR_EDITION_LINKS, SELECTOR_COVER_IMAGE, SELECTOR_AUTHOR_CONTAINER,
            HTTP_TIMEOUT, PLAYWRIGHT_TIMEOUT,
            AUTHOR_NAME, LANGUAGE,
            SMTP_HOST, SMTP_PORT, SMTP_MAX_RETRIES,
        )
        
        # Verify types
        assert isinstance(PROJECT_ROOT, Path)
        assert isinstance(BASE_URL, str)
        assert isinstance(HTTP_TIMEOUT, int)
        assert isinstance(KINDLE_EMAILS, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not integration"])
