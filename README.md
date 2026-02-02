# libmag2epub

libmag2epub is a Python automation pipeline that scrapes the Revista Liberta website, converts magazine editions into Kindle-compatible EPUB format, and emails them to configured Kindle addresses. The project has been refactored into a modular architecture with comprehensive testing.

> **Note:** You need to be a Revista Liberta subscriber for this script to work.

## What the project does

- **Scrapes** the Revista Liberta site for the latest and past editions using Playwright
- **Extracts** article content and cover images into the `raw/` directory
- **Converts** scraped editions into EPUB files optimized for Kindle
- **Emails** generated EPUBs to configured Kindle addresses via Gmail SMTP
- **Archives** sent EPUBs to the `sent/` directory with history tracking
- **Modular Design** - No subprocess chaining, all components are importable Python modules

## Architecture Overview

The project uses a modular architecture with all logic organized under `src/`:

```
src/
├── __init__.py          # Package exports
├── config.py            # Centralized configuration (paths, URLs, selectors, timeouts)
├── session.py           # Authentication & session management with proper resource cleanup
├── scraper.py           # Magazine content scraping (IndexScraper, MagazineScraper classes)
├── builder.py           # EPUB generation from scraped content (EpubBuilder class)
├── mailer.py            # Email delivery with retry mechanism (Mailer class)
├── orchestrator.py      # Pipeline coordination (PipelineOrchestrator class)
└── sent_manager.py      # Workflow management after EPUB creation (SentManager class)
```

## Key Features

- **No Subprocess Chaining**: Direct module imports instead of `subprocess.run()` calls
- **Portable Paths**: Uses `pathlib.Path(__file__).parent` - works on any machine
- **Resource Safety**: All Playwright contexts/browsers properly closed on error paths
- **Retry Logic**: SMTP connections retry 3 times with exponential backoff
- **Explicit Timeouts**: All HTTP and Playwright operations have configurable timeouts
- **Comprehensive Testing**: 30+ tests (configuration, session, builder, mailer, pipeline)

## Tech Stack

- **Python 3.11+** (recommended)
- **Playwright** - Browser automation for scraping
- **httpx** - Async HTTP requests
- **trafilatura** - HTML to Markdown extraction
- **Pillow** - Image optimization
- **pandoc** - Document conversion (external dependency)
- **pytest** - Testing framework

## Project Structure

```
├── src/                    # All Python modules (modular architecture)
│   ├── __init__.py        # Package exports
│   ├── config.py          # Centralized configuration
│   ├── session.py         # Authentication & session management
│   ├── scraper.py         # Content scraping classes
│   ├── builder.py         # EPUB generation
│   ├── mailer.py          # Email delivery with retry logic
│   ├── orchestrator.py    # Pipeline coordination
│   └── sent_manager.py    # Archive & history management
├── tests/                  # Test suite
│   ├── unit/              # Unit tests (28 tests)
│   │   ├── test_config.py
│   │   ├── test_session.py
│   │   ├── test_builder.py
│   │   └── test_mailer.py
│   ├── integration/       # Integration tests
│   │   └── test_pipeline.py
│   ├── run_tests.py       # Test runner script
│   └── README.md          # Testing documentation
├── docs/                   # Documentation
│   └── PHASE1_AUDIT.md    # Architecture audit
├── raw/                    # Scraped content (gitignored)
├── ebook/                  # Generated EPUBs
├── sent/                   # Archive of sent EPUBs
├── main.py                 # Entry point (uses modular imports)
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
├── .env.sample             # Alternative environment template
├── .gitignore              # Excludes .env, auth.json, raw/
├── pytest.ini             # Pytest configuration
├── ROADMAP.md             # Development roadmap
├── Dockerfile             # Docker container definition
├── docker-compose.yml     # Docker Compose configuration
└── .dockerignore          # Docker build exclusions
```

## Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd libmag2epub
```

### 2. Install Dependencies

See the [Dependencies & Installation](#dependencies--installation) section above for detailed requirements. Quick setup:

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install system dependencies (requires sudo)
./setup.sh
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials:
# LIBER_USER=your_email@example.com
# LIBER_PASS=your_password
# MAIL=your_gmail@gmail.com
# SEC=your_gmail_app_password
# KINDLE_EMAILS=kindle1@kindle.com,kindle2@kindle.com
```

### 4. Verify Setup with Tests

```bash
# Run all unit tests (no network required)
python -m pytest tests/unit/ -v

# Expected output: 28 passed
```

## Docker Setup (Alternative)

For a containerized setup with all dependencies pre-installed:

### Quick Start with Docker

```bash
# 1. Clone and enter directory
git clone <repository-url>
cd libmag2epub

# 2. Copy and configure environment
cp .env.example .env
# Edit .env with your credentials

# 3. Create empty auth.json (optional, for session persistence)
touch auth.json

# 4. Build and run
docker-compose up --build
```

**Note:** The `sent_history.txt` file is automatically created inside the container to track sent editions.

### Docker Commands

```bash
# Build the image
docker build -t libertapranois .

# Run with mounted volumes
docker run -v $(pwd)/.env:/app/.env:ro \
           -v $(pwd)/raw:/app/raw \
           -v $(pwd)/ebook:/app/ebook \
           -v $(pwd)/sent:/app/sent \
           libertapranois

# Run tests in container
docker run --rm libertapranois python -m pytest tests/ -v
```

### Docker Compose (Recommended)

```bash
# Run the pipeline
docker-compose up

# Create auth.json first, then run with session persistence
touch auth.json && docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**Benefits:**
- No local Python/Node.js installation needed
- Pandoc and Playwright pre-installed
- Consistent environment across systems
- Isolated from system dependencies

## Usage

### Run Full Pipeline

```bash
# Scrape, build, and email all new editions
python main.py
```

### Use Individual Components

```python
import asyncio
from src.orchestrator import process_recent, process_single
from src.scraper import get_editions, scrape_issue
from src.builder import build_epub
from src.mailer import Mailer

# Process 5 most recent editions
asyncio.run(process_recent(limit=5))

# Process specific edition
asyncio.run(process_single("edicao-18"))

# Or use components directly
async def custom_flow():
    # Get available editions
    editions = await get_editions()
    print(f"Found: {editions}")
    
    # Scrape specific edition
    await scrape_issue("edicao-18")
    
    # Build EPUB
    epub_path = build_epub("edicao-18")
    
    # Send via email
    if epub_path:
        mailer = Mailer()
        mailer.send_epub(epub_path)

asyncio.run(custom_flow())
```

### Run Tests

```bash
# All unit tests
python -m pytest tests/unit/ -v

# Specific test file
python -m pytest tests/unit/test_config.py -v

# With coverage
python -m pytest tests/ --cov=src --cov-report=html

# Integration tests (requires network/credentials)
python -m pytest tests/integration/ -v -m integration
```

## Configuration

All configuration is centralized in `src/config.py`:

- **Paths**: `RAW_DIR`, `EBOOK_DIR`, `SENT_DIR` (portable across VMs)
- **URLs**: `BASE_URL`, `INDEX_URL`, `LOGIN_URL`
- **Selectors**: CSS selectors for scraping (easily updated if site changes)
- **Timeouts**: `HTTP_TIMEOUT`, `PLAYWRIGHT_TIMEOUT` (all in seconds)
- **Build Settings**: Cover dimensions, image quality, author name
- **SMTP Settings**: Host, port, max retries, retry delay

## Testing

The project includes comprehensive tests:

| Test Category | Count | Description |
|--------------|-------|-------------|
| **Unit Tests** | 28 | No network required, test individual components |
| **Integration Tests** | 2+ | Require network/credentials, test full pipeline |

### Test Files

- `tests/unit/test_config.py` - Configuration validation
- `tests/unit/test_session.py` - Session/auth management
- `tests/unit/test_builder.py` - EPUB generation
- `tests/unit/test_mailer.py` - Email functionality
- `tests/integration/test_pipeline.py` - Full pipeline integration
- `tests/run_tests.py` - Test runner utility

See `tests/README.md` for detailed testing documentation.

## Dependencies & Installation

### System Requirements

This project requires both **system packages** and **Python packages** to run correctly.

#### Required System Dependencies

**Ubuntu/Debian:**
```bash
# Install pandoc (for EPUB generation)
sudo apt-get update
sudo apt-get install -y pandoc

# OR download standalone pandoc (if you don't have sudo):
cd /tmp
curl -L -o pandoc.tar.gz https://github.com/jgm/pandoc/releases/download/3.1.11/pandoc-3.1.11-linux-amd64.tar.gz
tar xvzf pandoc.tar.gz
sudo cp pandoc-3.1.11/bin/pandoc /usr/local/bin/
```

**macOS:**
```bash
brew install pandoc
```

#### Playwright Browser Dependencies

Playwright requires system libraries for Chromium. You can install them using the automated script:

```bash
# Run the setup script (requires sudo)
chmod +x setup.sh
./setup.sh
```

Or manually install the required libraries:

**Ubuntu/Debian:**
```bash
sudo apt-get install -y \
    libnspr4 \
    libnss3 \
    libnssutil3 \
    libsmime3 \
    libsqlite3-0 \
    libatk-1.0-0 \
    libatk-bridge-2.0-0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libasound2 \
    libcurl4
```

**macOS:**
Playwright dependencies are typically included with macOS, but you may need to install additional libraries if you encounter issues.

### Python Dependencies

All Python packages are listed in `requirements.txt`:

| Package | Version | Purpose |
|---------|---------|---------|
| `playwright` | >=1.40.0 | Browser automation for web scraping |
| `httpx` | >=0.25.0 | Async HTTP client for API requests |
| `trafilatura` | >=1.6.0 | HTML to Markdown content extraction |
| `Pillow` | >=10.0.0 | Image processing and optimization |
| `python-dotenv` | >=1.0.0 | Environment variable management |
| `lxml-html-clean` | >=0.1.0 | HTML cleaning (required by trafilatura) |
| `pytest` | >=8.0.0 | Testing framework |
| `pytest-asyncio` | >=0.23.0 | Async test support |

**Note:** The `lxml-html-clean` package is now required separately due to changes in the `lxml` library (as of lxml 5.2+).

### Complete Installation Steps

1. **Clone and setup Python environment:**
```bash
git clone <repository-url>
cd libertapranois
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. **Install system dependencies (choose one method):**

   **Option A - Automated (Recommended):**
   ```bash
   ./setup.sh
   ```

   **Option B - Manual:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install -y pandoc libnspr4 libnss3 libatk-1.0-0 libatk-bridge-2.0-0
   
   # Install Playwright browsers
   playwright install chromium
   
   # Install Playwright system dependencies
   playwright install-deps chromium
   ```

3. **Verify installation:**
```bash
# Run tests to verify everything works
python -m pytest tests/unit/ -v

# Check that pandoc is installed
which pandoc

# Check that playwright browsers are installed
playwright show-browsers
```

## Security

- `.env` - Contains credentials (gitignored)
- `auth.json` - Playwright session state (gitignored)
- `raw/` - Scraped content (gitignored)
- Never commit sensitive files - all are in `.gitignore`

## Development Roadmap

See `ROADMAP.md` for detailed development phases:

- ✅ **Phase 1**: Audit & Discovery (Complete)
- ✅ **Phase 2**: Modular Refactoring (Complete)
  - Eliminated subprocess chaining
  - Centralized configuration
  - Hardened resource management
  - Modernized mailer with retry logic
  - GitHub-ready structure
- 🔄 **Phase 3**: Security & Error Handling (In Progress)
- ⏳ **Phase 4**: GitHub Documentation & Cleanup (Todo)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Run `python -m pytest tests/ -v` to ensure all tests pass
5. Submit a pull request

## Troubleshooting

### Import Errors

```bash
# If you get ModuleNotFoundError, ensure you're in the project root
cd /path/to/libertapranois
python -c "from src.config import PROJECT_ROOT; print(PROJECT_ROOT)"
```

### Playwright Not Found

```bash
playwright install chromium
```

### Tests Failing

```bash
# Install test dependencies
pip install pytest pytest-asyncio lxml-html-clean

# Run with verbose output
python -m pytest tests/unit/ -v --tb=long
```

### Pandoc Not Found

The EPUB builder requires `pandoc` to be installed on your system:

```bash
# Run the setup script
./setup.sh

# Or install manually:
# Ubuntu/Debian
sudo apt-get install pandoc

# macOS
brew install pandoc

# Or download standalone binary:
cd /tmp
curl -L -o pandoc.tar.gz https://github.com/jgm/pandoc/releases/download/3.1.11/pandoc-3.1.11-linux-amd64.tar.gz
tar xvzf pandoc.tar.gz
sudo cp pandoc-3.1.11/bin/pandoc /usr/local/bin/
```

### Playwright Browser Dependencies Missing

If you see errors like `libnspr4.so: cannot open shared object file`, you need to install system libraries:

```bash
# Run the automated setup
./setup.sh

# Or manually install on Ubuntu/Debian:
sudo apt-get install -y libnspr4 libnss3 libnssutil3 libsmime3 libatk-1.0-0 libatk-bridge-2.0-0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1

# Then reinstall Playwright browsers:
playwright install chromium
```

### Dependency Check Script

Run this to check your installation:

```bash
# Check all dependencies
python -c "
import sys
print('Python:', sys.version)
print()

try:
    import playwright
    print('✓ playwright')
except ImportError:
    print('✗ playwright - pip install playwright')

try:
    import httpx
    print('✓ httpx')
except ImportError:
    print('✗ httpx - pip install httpx')

try:
    import trafilatura
    print('✓ trafilatura')
except ImportError:
    print('✗ trafilatura - pip install trafilatura')

try:
    from PIL import Image
    print('✓ Pillow')
except ImportError:
    print('✗ Pillow - pip install Pillow')

try:
    import dotenv
    print('✓ python-dotenv')
except ImportError:
    print('✗ python-dotenv - pip install python-dotenv')

try:
    import lxml_html_clean
    print('✓ lxml-html-clean')
except ImportError:
    print('✗ lxml-html-clean - pip install lxml-html-clean')

import subprocess
try:
    subprocess.run(['pandoc', '--version'], capture_output=True, check=True)
    print('✓ pandoc')
except:
    print('✗ pandoc - Install via ./setup.sh or package manager')
"
```

## License

[Add your license here]

## Status

**Current Status:** Phase 2 Complete ✅ - Modular architecture with comprehensive testing (33+ tests passing)

The project is now fully modular, well-tested, and ready for production use or further development.
