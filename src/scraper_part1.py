#!/usr/bin/env python3
"""
Magazine scraper for Revista Liberta.
Handles authentication, article downloading, and EPUB generation.
Part 1/5 - Imports and MagazineScraper class
"""
from playwright.async_api import async_playwright, BrowserContext
import asyncio
import json
import os
from pathlib import Path
from typing import List

class MagazineScraper:
    """Main scraper class for fetching Revista Liberta magazine."""
    
    def __init__(self, edition: str):
        self.edition = edition
        self.url = f"https://revistaliber.ta.com.br/edicao/{edition}/"
        self.context = None
        self.page = None
        self.cover_url = None
        self.article_urls = []
        self.articles_data = []
    
    async def _download_cover(self, context: BrowserContext) -> str:
        """Download and save the magazine cover."""
        page = await context.new_page()
        try:
            await page.goto(self.url)
            cover_selector = '.cover-image img, .main-cover img'
            cover_url = await page.query_selector(cover_selector)
            if cover_url:
                src = await cover_url.get_attribute('src')
                print(f"Found cover at: {src}")
                base_url = 'https://revistaliber.ta.com.br/'
                full_cover_url = src if src.startswith(('http', '/')) else base_url + src
            else:
                print("No cover image found, using placeholder")
                full_cover_url = ""
        except Exception as e:
            print(f"Error downloading cover: {e}")
            full_cover_url = ""
        await page.close()
        return full_cover_url
