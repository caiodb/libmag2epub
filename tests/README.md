# Testing Guide

## Quick Start

### 1. Install Test Dependencies

```bash
pip install pytest pytest-asyncio
```

### 2. Run All Unit Tests

```bash
python tests/run_tests.py
# or
pytest tests/unit/ -v
```

### 3. Run Specific Test Files

```bash
# Test configuration
pytest tests/unit/test_config.py -v

# Test session management
pytest tests/unit/test_session.py -v

# Test EPUB builder
pytest tests/unit/test_builder.py -v

# Test mailer
pytest tests/unit/test_mailer.py -v
```

## Test Structure

```
tests/
├── unit/                    # Unit tests (no network required)
│   ├── test_config.py       # Configuration tests
│   ├── test_session.py      # Session/auth tests
│   ├── test_builder.py      # EPUB builder tests
│   └── test_mailer.py       # Email tests
├── integration/             # Integration tests (requires network)
│   └── test_pipeline.py     # Full pipeline tests
├── fixtures/                # Test data
└── run_tests.py             # Test runner script
```

## Testing Levels

### Level 1: Unit Tests (Safe, Fast)

These don't require network access or credentials:

```bash
pytest tests/unit/ -v
```

Tests include:
- Config path validation
- Class instantiation
- Method logic without external calls
- Error handling paths

### Level 2: Component Tests (Requires Setup)

Test individual components with real data:

```python
# Test scraper with a real edition (requires credentials)
from src.scraper import scrape_issue
await scrape_issue("edicao-18")

# Test builder with existing raw data
from src.builder import build_epub
build_epub("edicao-18")

# Test mailer (requires email credentials)
from src.mailer import send_via_gmail
from pathlib import Path
send_via_gmail(Path("ebook/test.epub"))
```

### Level 3: Integration Tests (Full Pipeline)

Run the full pipeline end-to-end:

```bash
# Full pipeline (requires all credentials)
python main.py
```

Or with the orchestrator directly:

```python
import asyncio
from src.orchestrator import process_single
await process_single("edicao-18")
```

## Manual Testing Checklist

### Config Module

```python
from src.config import PROJECT_ROOT, RAW_DIR, EBOOK_DIR
print(f"Project root: {PROJECT_ROOT}")
print(f"Raw dir: {RAW_DIR}")
print(f"Ebook dir: {EBOOK_DIR}")
```

### Session Module

```python
import asyncio
from playwright.async_api import async_playwright
from src.session import SessionManager

async def test_session():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        manager = SessionManager()
        context = await manager.get_or_create_context(browser)
        print("Session created successfully!")
        await manager.cleanup()
        await browser.close()

asyncio.run(test_session())
```

### Scraper Module

```python
import asyncio
from src.scraper import IndexScraper, MagazineScraper

async def test_scrapers():
    # Test index scraper
    index = IndexScraper()
    editions = await index.get_available_editions()
    print(f"Found {len(editions)} editions")
    
    # Test magazine scraper (if editions found)
    if editions:
        scraper = MagazineScraper(editions[0])
        success = await scraper.scrape()
        print(f"Scrape success: {success}")

asyncio.run(test_scrapers())
```

### Builder Module

```python
from src.builder import build_epub
from pathlib import Path

# If you have raw data already
result = build_epub("edicao-18")
if result:
    print(f"EPUB created: {result}")
else:
    print("Build failed")
```

### Mailer Module

```python
from src.mailer import Mailer
from pathlib import Path

mailer = Mailer()
# Check configuration
print(f"Sender: {mailer.sender}")
print(f"Recipients: {mailer.recipients}")

# Test with real file (will actually send!)
# result = mailer.send_epub(Path("ebook/Test.epub"))
```

## Mock Testing

For testing without external dependencies:

```python
from unittest.mock import Mock, patch, MagicMock

# Mock SMTP
with patch('src.mailer.smtplib.SMTP_SSL') as mock_smtp:
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__ = Mock(return_value=mock_server)
    mock_smtp.return_value.__exit__ = Mock(return_value=False)
    
    from src.mailer import Mailer
    mailer = Mailer()
    result = mailer.send_epub(Path("fake.epub"))
    # Test logic without actual email sent
```

## Continuous Integration

For CI/CD environments, exclude integration tests:

```bash
# Only unit tests (no network)
pytest tests/ -m "not integration"

# All tests
pytest tests/
```

## Debugging Failed Tests

```bash
# Show full traceback
pytest tests/unit/ -v --tb=long

# Stop on first failure
pytest tests/unit/ -v -x

# Run specific test
pytest tests/unit/test_config.py::TestConfigPaths::test_project_root_exists -v

# Show print statements
pytest tests/unit/ -v -s
```

## Expected Test Results

### Unit Tests
- All config tests should pass
- Session tests should pass
- Builder tests should pass
- Mailer tests should pass

### Integration Tests
- May fail without valid credentials
- Require network access
- May be slow due to page loads

## Troubleshooting

### Import Errors

If you get `ModuleNotFoundError`:

```bash
# Make sure you're in the project root
cd /home/devuser/myapps/newshit

# Run with python -m
cd /home/devuser/myapps/newshit && python -m pytest tests/unit/ -v
```

### Playwright Not Installed

```bash
playwright install chromium
```

### Missing Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-asyncio
```
