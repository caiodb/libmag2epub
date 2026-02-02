"""
Orchestrator module that coordinates the scraping and building pipeline.
Replaces subprocess calls with direct module imports.
"""

import asyncio
from pathlib import Path
from typing import List, Optional

from src.config import (
    RAW_DIR,
    EBOOK_DIR,
    PROJECT_ROOT,
)
from src.scraper import IndexScraper, MagazineScraper
from src.builder import EpubBuilder


class PipelineOrchestrator:
    """Orchestrates the magazine processing pipeline."""
    
    def __init__(self):
        self.index_scraper = IndexScraper()
    
    async def run(self, max_editions: Optional[int] = None) -> None:
        """
        Run the full pipeline: discover editions, scrape, and build.
        
        Args:
            max_editions: Maximum number of editions to process (None for all)
        """
        print("=" * 60)
        print("STARTING MAGAZINE PIPELINE")
        print("=" * 60)
        
        # Step 1: Get available editions
        editions = await self.index_scraper.get_available_editions()
        
        if not editions:
            print("No editions found. Check the CSS selectors.")
            return
        
        print(f"Found {len(editions)} editions. Checking for updates...")
        
        # Step 2: Process each edition
        processed_count = 0
        for slug in editions:
            if max_editions and processed_count >= max_editions:
                print(f"\nReached maximum of {max_editions} editions. Stopping.")
                break
            
            try:
                if await self._process_magazine(slug):
                    processed_count += 1
            except Exception as e:
                print(f"Failed to process {slug}: {e}")
        
        print(f"\n{'='*60}")
        print(f"PIPELINE COMPLETE: Processed {processed_count} editions")
        print(f"{'='*60}")
    
    async def _process_magazine(self, slug: str) -> bool:
        """
        Process a single magazine edition: scrape and build.
        
        Args:
            slug: The edition slug
            
        Returns:
            bool: True if processing was successful
        """
        # Check if already processed
        if self._is_already_processed(slug):
            print(f"-> Skipping {slug}: Already processed")
            return False
        
        print(f"\n{'='*40}")
        print(f"PROCESSING NEW EDITION: {slug}")
        print(f"{'='*40}")
        
        # Step 1: Scrape
        print(f"\n[1/2] Scraping content for {slug}...")
        scraper = MagazineScraper(slug)
        scrape_success = await scraper.scrape()
        
        if not scrape_success:
            print(f"X Scraping failed for {slug}")
            return False
        
        # Step 2: Build
        print(f"\n[2/2] Building EPUB for {slug}...")
        builder = EpubBuilder(slug)
        epub_path = builder.build()
        
        if not epub_path:
            print(f"X Build failed for {slug}")
            return False
        
        print(f"✓ Successfully processed {slug}")
        return True
    
    def _is_already_processed(self, slug: str) -> bool:
        """
        Check if a magazine edition has already been processed.
        
        Args:
            slug: The edition slug
            
        Returns:
            bool: True if already processed
        """
        # Check multiple locations
        epub_path = PROJECT_ROOT / f"{slug}.epub"
        ebook_path = EBOOK_DIR / f"{slug}.epub"
        raw_path = RAW_DIR / slug
        
        return (
            epub_path.exists() or 
            ebook_path.exists() or 
            raw_path.exists()
        )


# Convenience functions for different usage patterns
async def process_all() -> None:
    """Process all available editions."""
    orchestrator = PipelineOrchestrator()
    await orchestrator.run()


async def process_recent(limit: int = 5) -> None:
    """
    Process the most recent N editions.
    
    Args:
        limit: Number of recent editions to process
    """
    orchestrator = PipelineOrchestrator()
    await orchestrator.run(max_editions=limit)


async def process_single(issue_name: str) -> bool:
    """
    Process a single edition by name.
    
    Args:
        issue_name: The edition slug
        
    Returns:
        bool: True if processing succeeded
    """
    orchestrator = PipelineOrchestrator()
    return await orchestrator._process_magazine(issue_name)
