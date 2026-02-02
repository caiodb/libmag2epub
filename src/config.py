"""
Centralized configuration for the magazine automation pipeline.
Uses pathlib for portability across different environments.
"""

import os
from pathlib import Path
from dotenv import load_dotenv


# Project Root Directory (portable across any VM)
PROJECT_ROOT = Path(__file__).parent.parent.resolve()

# Load environment variables from .env file
ENV_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_PATH)


# =============================================================================
# PATHS
# =============================================================================

RAW_DIR = PROJECT_ROOT / "raw"
EBOOK_DIR = PROJECT_ROOT / "ebook"
SENT_DIR = PROJECT_ROOT / "sent"
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"
DOCS_DIR = PROJECT_ROOT / "docs"

# Ensure data directory exists (for Docker volume persistence)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Session state and history files (in data/ for Docker persistence)
AUTH_FILE = DATA_DIR / "auth.json"
SENT_HISTORY_FILE = DATA_DIR / "sent_history.txt"


# =============================================================================
# URLS
# =============================================================================

BASE_URL = "https://revistaliberta.com.br/digital"
INDEX_URL = f"{BASE_URL}/edicoes/"
LOGIN_URL = f"{BASE_URL}/login/"


# =============================================================================
# CREDENTIALS (from .env)
# =============================================================================

# Magazine login credentials
LIBER_USER = os.getenv("LIBER_USER", "")
LIBER_PASS = os.getenv("LIBER_PASS", "")

# Email credentials
MAIL = os.getenv("MAIL", "")
SEC = os.getenv("SEC", "")
KINDLE_EMAILS = [
    e.strip() 
    for e in os.getenv("KINDLE_EMAILS", "").split(",") 
    if e.strip()
]


# =============================================================================
# CSS SELECTORS (centralized for easy maintenance)
# =============================================================================

# Index page selectors
SELECTOR_EDITION_LINKS = "a.text-main-dark"

# Magazine edition page selectors
SELECTOR_COVER_IMAGE = "img.w-100"
SELECTOR_ARTICLE_LINKS = "a.text-main-dark"

# Author section selectors
SELECTOR_AUTHOR_CONTAINER = "#author"
SELECTOR_AUTHOR_NAME = "h6"
SELECTOR_AUTHOR_BIO = "p"

# Login page selectors
SELECTOR_LOGIN_USERNAME = 'input[name="log"]'
SELECTOR_LOGIN_PASSWORD = 'input[name="pwd"]'
SELECTOR_LOGIN_SUBMIT_ID = "#wp-submit"
SELECTOR_LOGIN_SUBMIT_NAME = 'input[name="wp-submit"]'
SELECTOR_LOGIN_SUBMIT_TEXT = 'text="Acessar"'


# =============================================================================
# TIMEOUTS (in seconds)
# =============================================================================

HTTP_TIMEOUT = 30
PLAYWRIGHT_TIMEOUT = 30000  # 30 seconds in milliseconds
LOGIN_TIMEOUT = 5000  # 5 seconds for login button clicks
BROWSER_NAVIGATION_TIMEOUT = 30000


# =============================================================================
# EPUB BUILD SETTINGS
# =============================================================================

AUTHOR_NAME = "Revista Liberta"
LANGUAGE = "pt-BR"
COVER_MAX_WIDTH = 1200
COVER_MAX_HEIGHT = 1920
COVER_QUALITY = 85
IMAGE_QUALITY = 80


# =============================================================================
# MAILER SETTINGS
# =============================================================================

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
SMTP_MAX_RETRIES = 3
SMTP_RETRY_DELAY = 5  # seconds between retries


# =============================================================================
# LOGGING
# =============================================================================

LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
