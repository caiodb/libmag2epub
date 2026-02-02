"""
Test runner script for manual testing.
Run with: python tests/run_tests.py
"""

import subprocess
import sys
from pathlib import Path


def run_unit_tests():
    """Run all unit tests."""
    print("="*60)
    print("RUNNING UNIT TESTS")
    print("="*60)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/unit/", "-v", "--tb=short"],
        cwd=Path(__file__).parent.parent
    )
    return result.returncode


def run_integration_tests():
    """Run integration tests (requires network)."""
    print("\n" + "="*60)
    print("RUNNING INTEGRATION TESTS")
    print("="*60)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/integration/", "-v", "--tb=short", "-m", "integration"],
        cwd=Path(__file__).parent.parent
    )
    return result.returncode


def run_all_tests():
    """Run all tests."""
    print("="*60)
    print("RUNNING ALL TESTS")
    print("="*60)
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-m", "not integration"],
        cwd=Path(__file__).parent.parent
    )
    return result.returncode


def check_dependencies():
    """Check if pytest is installed."""
    try:
        import pytest
        import pytest_asyncio
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Install with: pip install pytest pytest-asyncio")
        return False


if __name__ == "__main__":
    if not check_dependencies():
        sys.exit(1)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "unit":
            exit_code = run_unit_tests()
        elif sys.argv[1] == "integration":
            exit_code = run_integration_tests()
        elif sys.argv[1] == "all":
            exit_code = run_all_tests()
        else:
            print(f"Unknown argument: {sys.argv[1]}")
            print("Usage: python tests/run_tests.py [unit|integration|all]")
            exit_code = 1
    else:
        exit_code = run_unit_tests()
    
    sys.exit(exit_code)
