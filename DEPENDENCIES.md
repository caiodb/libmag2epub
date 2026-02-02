# Dependencies Guide

This document provides detailed information about all dependencies required for the Liberta pra Nois project.

## Overview

The project requires three categories of dependencies:
1. **Python Packages** - Installed via pip
2. **System Libraries** - Required by Playwright's Chromium browser
3. **External Tools** - Pandoc for document conversion

## Python Dependencies

All Python packages are defined in `requirements.txt`:

### Core Dependencies

| Package | Version | Purpose | Importance |
|---------|---------|---------|------------|
| `playwright` | >=1.40.0 | Browser automation for scraping | **Required** |
| `httpx` | >=0.25.0 | Async HTTP client | **Required** |
| `trafilatura` | >=1.6.0 | HTML to text extraction | **Required** |
| `Pillow` | >=10.0.0 | Image processing | **Required** |
| `python-dotenv` | >=1.0.0 | Environment management | **Required** |
| `lxml-html-clean` | >=0.1.0 | HTML cleaning (trafilatura dep) | **Required** |

### Development Dependencies

| Package | Version | Purpose | Importance |
|---------|---------|---------|------------|
| `pytest` | >=8.0.0 | Testing framework | Development |
| `pytest-asyncio` | >=0.23.0 | Async test support | Development |

### Installing Python Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:

```bash
pip install playwright>=1.40.0 httpx>=0.25.0 trafilatura>=1.6.0 Pillow>=10.0.0
pip install python-dotenv>=1.0.0 lxml-html-clean>=0.1.0
pip install pytest>=8.0.0 pytest-asyncio>=0.23.0
```

## System Dependencies

### Why System Dependencies Are Needed

Playwright uses a real browser (Chromium) for web scraping. This browser requires system-level libraries for:
- Networking (libnspr4, libnss3, libcurl4)
- Graphics (libxcomposite1, libxdamage1, libxfixes3)
- Accessibility (libatk-1.0, libatk-bridge-2.0, libatspi2.0)
- Audio (libasound2)
- Graphics buffer (libgbm1)

### Ubuntu/Debian

Required packages:

```bash
sudo apt-get update
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
    libcurl4 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0
```

### macOS

macOS typically includes most required libraries. If you encounter issues:

```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies via Homebrew
brew install nss atk at-spi2-core
```

### Automated Installation

Use the provided setup script (run as normal user, NOT with sudo):

```bash
# Run as your normal user (the script will use sudo only when needed)
./setup.sh

# Or with bash explicitly
bash setup.sh
```

**Important:** Do NOT run with `sudo ./setup.sh` - this causes issues with virtual environments and Python package detection.

This script will:
1. Detect your operating system
2. Activate .venv if it exists, or guide you to create one
3. Install Python dependencies if missing
4. Install pandoc (using sudo only for this system package)
5. Install Playwright browsers
6. Install system libraries (using sudo only for these)
7. Verify the installation

## External Tools

### Pandoc

Pandoc is required for converting Markdown to EPUB format.

**Version required:** 2.0+ (tested with 3.1.11)

#### Installation

**Ubuntu/Debian:**

Required packages:

```bash
sudo apt-get update
sudo apt-get install -y \
    libnspr4 \
    libnss3 \
    libsqlite3-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libasound2 \
    libcurl4 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0
```

**Note:** Package names may vary slightly between Ubuntu versions. The `libnss3` package includes `libnssutil3` and `libsmime3`. If any packages are not found, run `./setup.sh` which handles this automatically.

**macOS:**
```bash
brew install pandoc
```

**Standalone Binary (no sudo required):**
```bash
cd /tmp
curl -L -o pandoc.tar.gz https://github.com/jgm/pandoc/releases/download/3.1.11/pandoc-3.1.11-linux-amd64.tar.gz
tar xvzf pandoc.tar.gz
# Copy to a location in your PATH
mkdir -p ~/.local/bin
cp pandoc-3.1.11/bin/pandoc ~/.local/bin/
# Add to PATH if not already there
export PATH="$HOME/.local/bin:$PATH"
```

**Verification:**
```bash
pandoc --version
```

## Verification

### Quick Check

Run this Python script to verify all dependencies:

```python
import sys
import subprocess

def check_python_package(name, import_name=None):
    """Check if a Python package is installed."""
    import_name = import_name or name
    try:
        __import__(import_name)
        print(f"✓ {name}")
        return True
    except ImportError:
        print(f"✗ {name} - pip install {name}")
        return False

def check_command(name, cmd=None):
    """Check if a system command is available."""
    cmd = cmd or [name, '--version']
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        print(f"✓ {name}")
        return True
    except:
        print(f"✗ {name} - not installed")
        return False

def check_playwright_browsers():
    """Check if Playwright browsers are installed."""
    import os
    import glob
    
    cache_dir = os.path.expanduser('~/.cache/ms-playwright')
    if not os.path.exists(cache_dir):
        print(f"✗ Playwright browsers - run: playwright install chromium")
        return False
    
    # Check for chromium
    chromium_dirs = glob.glob(os.path.join(cache_dir, 'chromium*'))
    if chromium_dirs:
        print(f"✓ Playwright Chromium browsers")
        return True
    else:
        print(f"✗ Playwright browsers - run: playwright install chromium")
        return False

print("Python version:", sys.version)
print()

print("Python Packages:")
all_ok = True
all_ok &= check_python_package("playwright")
all_ok &= check_python_package("httpx")
all_ok &= check_python_package("trafilatura")
all_ok &= check_python_package("Pillow", "PIL")
all_ok &= check_python_package("python-dotenv", "dotenv")
all_ok &= check_python_package("lxml-html-clean", "lxml_html_clean")

print()
print("External Tools:")
all_ok &= check_command("pandoc")

print()
print("Playwright Browsers:")
all_ok &= check_playwright_browsers()

print()
if all_ok:
    print("✓ All dependencies are installed!")
else:
    print("✗ Some dependencies are missing. Run ./setup.sh to install them.")
    sys.exit(1)
```

### Using the Test Suite

The test suite also verifies dependencies:

```bash
# Run all tests
python -m pytest tests/unit/ -v

# Expected: 28 tests passed
```

## Troubleshooting

### Missing Library Errors

If you see errors like:
- `libnspr4.so: cannot open shared object file`
- `libnss3.so: cannot open shared object file`
- `libatk-1.0.so.0: cannot open shared object file`

**Solution:** Install system dependencies
```bash
./setup.sh
# Or manually:
sudo apt-get install -y libnspr4 libnss3 libatk-1.0-0 libatk-bridge-2.0-0
```

### Playwright Browser Not Found

If you see:
- `Executable doesn't exist at /home/user/.cache/ms-playwright/...`

**Solution:** Install Playwright browsers
```bash
playwright install chromium
```

### Pandoc Not Found

If you see:
- `pandoc: command not found`
- `ERROR: pandoc not found. Please install pandoc.`

**Solution:** Install pandoc
```bash
# Option 1: Package manager
sudo apt-get install pandoc  # Ubuntu/Debian
brew install pandoc          # macOS

# Option 2: Standalone binary (no sudo)
cd /tmp
curl -L -o pandoc.tar.gz https://github.com/jgm/pandoc/releases/download/3.1.11/pandoc-3.1.11-linux-amd64.tar.gz
tar xvzf pandoc.tar.gz
mkdir -p ~/.local/bin
cp pandoc-3.1.11/bin/pandoc ~/.local/bin/
export PATH="$HOME/.local/bin:$PATH"
```

### Common Mistakes

#### Running setup.sh with sudo

**Problem:** You ran `sudo ./setup.sh` and get "Playwright not found" even after pip install.

**Why:** When you use sudo, the script runs as root and doesn't see your user's virtual environment. Playwright was installed in your venv, not in root's Python.

**Solution:** Run setup.sh as your normal user:
```bash
# Wrong: sudo ./setup.sh
# Correct:
./setup.sh
```

The script will automatically use `sudo` only when needed for system packages (pandoc, libnspr4, etc.), but will use your user's Python environment for Playwright and other Python packages.

#### Not activating virtual environment

**Problem:** Setup script warns about not being in a virtual environment.

**Solution:** 
```bash
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

Or let the script auto-activate it - if `.venv` directory exists, the script will activate it automatically.

### Permission Errors

If you encounter permission errors during installation:

1. Ensure you're in a virtual environment
2. Use `sudo` only for system packages (pandoc, system libraries)
3. Python packages should be installed without sudo when in a venv

## Docker Alternative

If you prefer not to install dependencies on your host system, you can use Docker:

```dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libnspr4 libnss3 libatk-1.0-0 libatk-bridge-2.0-0 \
    libxcomposite1 libxdamage1 libxfixes3 libxrandr2 \
    libgbm1 libxkbcommon0 libasound2 libcurl4 \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium

# Copy application
COPY . .

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t libertapranois .
docker run -v $(pwd)/.env:/app/.env libertapranois
```

## Version Compatibility

This project has been tested with:

- **Python:** 3.11, 3.12
- **Playwright:** 1.40.0+
- **Pandoc:** 2.0+, 3.1.11 recommended
- **OS:** Ubuntu 20.04/22.04, macOS 13+

## Getting Help

If you encounter dependency issues:

1. Run `./setup.sh` to automatically install dependencies
2. Check this guide for your specific error
3. Run the verification script above to identify missing components
4. Check the [README.md](README.md) Troubleshooting section
5. Open an issue with the full error message and your OS version
