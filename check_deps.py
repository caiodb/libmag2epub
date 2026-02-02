#!/usr/bin/env python3
"""
Dependency check script for Libmag2epub
Run this to verify all dependencies are properly installed.
"""

import sys
import subprocess
import os
import glob


def check_python_package(name, import_name=None):
    """Check if a Python package is installed."""
    import_name = import_name or name
    try:
        __import__(import_name)
        print(f"  ✓ {name}")
        return True
    except ImportError:
        print(f"  ✗ {name} - pip install {name}")
        return False


def check_command(name, cmd=None):
    """Check if a system command is available."""
    cmd = cmd or [name, '--version']
    try:
        result = subprocess.run(cmd, capture_output=True, check=True, text=True)
        version = result.stdout.split('\n')[0] if result.stdout else "installed"
        print(f"  ✓ {name} ({version})")
        return True
    except:
        print(f"  ✗ {name} - not installed")
        return False


def check_playwright_browsers():
    """Check if Playwright browsers are installed."""
    cache_dir = os.path.expanduser('~/.cache/ms-playwright')
    if not os.path.exists(cache_dir):
        print(f"  ✗ Playwright browsers - run: playwright install chromium")
        return False
    
    # Check for chromium
    chromium_dirs = glob.glob(os.path.join(cache_dir, 'chromium*'))
    if chromium_dirs:
        print(f"  ✓ Playwright Chromium browsers")
        return True
    else:
        print(f"  ✗ Playwright browsers - run: playwright install chromium")
        return False


def main():
    print("=" * 60)
    print("Libmag2epub - Dependency Check")
    print("=" * 60)
    print()
    print(f"Python version: {sys.version}")
    print()
    
    all_ok = True
    
    print("Python Packages:")
    all_ok &= check_python_package("playwright")
    all_ok &= check_python_package("httpx")
    all_ok &= check_python_package("trafilatura")
    all_ok &= check_python_package("Pillow", "PIL")
    all_ok &= check_python_package("python-dotenv", "dotenv")
    all_ok &= check_python_package("lxml-html-clean", "lxml_html_clean")
    
    # Optional dev dependencies
    print()
    print("Development Packages (optional):")
    check_python_package("pytest")
    check_python_package("pytest-asyncio")
    
    print()
    print("External Tools:")
    all_ok &= check_command("pandoc")
    
    print()
    print("Playwright Browsers:")
    all_ok &= check_playwright_browsers()
    
    print()
    print("=" * 60)
    if all_ok:
        print("✓ All required dependencies are installed!")
        print("=" * 60)
        print()
        print("You're ready to run the pipeline:")
        print("  python main.py")
        return 0
    else:
        print("✗ Some dependencies are missing.")
        print("=" * 60)
        print()
        print("To install missing dependencies:")
        print("  ./setup.sh")
        print()
        print("Or see DEPENDENCIES.md for manual installation instructions.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
