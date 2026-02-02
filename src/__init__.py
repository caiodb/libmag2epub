"""
Magazine automation pipeline package.
Converts magazine content into Kindle EPUB format.
"""

from src.config import (
    PROJECT_ROOT,
    RAW_DIR,
    EBOOK_DIR,
    SENT_DIR,
    BASE_URL,
    INDEX_URL,
)

from src.scraper import (
    MagazineScraper,
    IndexScraper,
    scrape_issue,
    get_editions,
)

from src.builder import (
    EpubBuilder,
    build_epub,
)

from src.mailer import (
    Mailer,
    send_via_gmail,
)

from src.orchestrator import (
    PipelineOrchestrator,
    process_all,
    process_recent,
    process_single,
)

from src.sent_manager import (
    SentManager,
    run_sent_manager,
)

from src.session import (
    SessionManager,
    perform_login,
    get_context,
)

__version__ = "2.0.0"
__all__ = [
    "MagazineScraper",
    "IndexScraper",
    "EpubBuilder",
    "Mailer",
    "PipelineOrchestrator",
    "SentManager",
    "SessionManager",
    "scrape_issue",
    "get_editions",
    "build_epub",
    "send_via_gmail",
    "process_all",
    "process_recent",
    "process_single",
    "run_sent_manager",
    "perform_login",
    "get_context",
]
