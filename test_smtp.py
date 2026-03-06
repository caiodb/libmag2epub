#!/usr/bin/env python3
"""Debug script to check what values are loaded from .env"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import MAIL, SEC, KINDLE_EMAILS

print("Loaded configuration:")
print(f"MAIL: '{MAIL}'")
print(f"SEC: '{SEC}'")
print(f"SEC length: {len(SEC)}")
print(f"KINDLE_EMAILS: {KINDLE_EMAILS}")

# Test SMTP connection
import smtplib
print("\nTesting SMTP connection...")
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
        print("Connected to SMTP server")
        server.login(MAIL, SEC)
        print("Login successful!")
except Exception as e:
    print(f"Login failed: {e}")
    print(f"Error type: {type(e)}")
