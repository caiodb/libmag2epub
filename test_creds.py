#!/usr/bin/env python3
"""Test SMTP with hardcoded credentials"""
import smtplib
import sys

# Test with your actual credentials (spaces removed from password)
MAIL = "13.correa@gmail.com"
SEC = "skmlncluukixrdjp"  # App password with spaces removed

print("Testing SMTP connection...")
print(f"Username: {MAIL}")
print(f"Password length: {len(SEC)}")

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
        print("✓ Connected to SMTP server")
        server.login(MAIL, SEC)
        print("✓ Login successful!")
        print("\nCredentials are working correctly!")
except Exception as e:
    print(f"✗ Error: {e}")
    print("\nPossible issues:")
    print("1. App password may have been revoked")
    print("2. Account may have security restrictions")
    print("3. Try generating a NEW app password")
