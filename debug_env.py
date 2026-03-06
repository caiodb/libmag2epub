#!/usr/bin/env python3
"""Debug script to check environment configuration"""

import os
import sys

# Add src to path
sys.path.insert(0, '/app/src')

print("=" * 60)
print("ENVIRONMENT DEBUG")
print("=" * 60)

# Check raw env vars before loading config
print("\n1. Raw environment variables from Docker:")
print(f"   MAIL={os.getenv('MAIL', 'NOT SET')}")
print(f"   SEC={os.getenv('SEC', 'NOT SET')}")
print(f"   SEC length: {len(os.getenv('SEC', ''))}")

# Check .env file
env_path = '/app/.env'
print(f"\n2. .env file exists: {os.path.exists(env_path)}")
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        content = f.read()
        print(f"   .env file size: {len(content)} bytes")
        for line in content.split('\n'):
            if line.strip() and not line.startswith('#'):
                if 'SEC' in line or 'MAIL' in line:
                    print(f"   {line}")

# Now load config and check
print("\n3. After loading config.py:")
try:
    from config import MAIL, SEC, KINDLE_EMAILS
    print(f"   MAIL={MAIL}")
    print(f"   SEC={SEC}")
    print(f"   SEC length: {len(SEC)}")
    print(f"   KINDLE_EMAILS={KINDLE_EMAILS}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "=" * 60)

# Test SMTP connection
print("\n4. Testing SMTP connection...")
try:
    import smtplib
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
        print("   Connected to SMTP server")
        from config import MAIL, SEC
        server.login(MAIL, SEC)
        print("   Login successful!")
except Exception as e:
    print(f"   SMTP Error: {e}")

print("\n" + "=" * 60)
