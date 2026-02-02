"""
Magazine content scraper module with proper resource management and timeouts.
"""

import asyncio
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import httpx
import trafilatura
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from src.config import (
    RAW_DIR,
    BASE_URL,
    HTTP_TIMEOUT,
    BROWSER_NAVIGATION_TIMEOUT,
    SELECTOR_COVER_IMAGE,
    SELECTOR_ARTICLE_LINKS,
    SELECTOR_AUTHOR_CONTAINER,
    SELECTOR_AUTHOR_NAME,
    SELECTOR_AUTHOR_BIO,
)
from src.session import SessionManager


class MagazineScraper:
    """Scrapes magazine editions and extracts article content."""
    
    def __init__(self, issue_name: str):
        self.issue_name = issue_name
        self.issue_dir = RAW_DIR / issue_name
        self.session_manager = SessionManager()
        self._browser = None
        self._context = None
    
    async def scrape(self) -> bool:
        """
        Main scraping method with proper resource cleanup.
        
        Returns:
            bool: True if scraping succeeded, False otherwise
        """
        # Create issue directory
        self.issue_dir.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {self.issue_dir}")
        
        try:
            async with async_playwright() as p:
                self._browser = await p.chromium.launch(headless=True)
                self._context = await self.session_manager.get_or_create_context(self._browser)
                
                page = await self._context.new_page()
                
                print(f"--- Accessing Magazine: {self.issue_name} ---")
                await page.goto(
                    f"{BASE_URL}/edicao/{self.issue_name}",
                    wait_until="networkidle",
                    timeout=BROWSER_NAVIGATION_TIMEOUT
                )
                
                # Download cover image
                await self._download_cover(page)
                
                # Get article links
                article_links = await self._get_article_links(page)
                
                # Scrape each article
                await self._scrape_articles(page, article_links)
                
                await page.close()
                print(f"Scrape complete. Files are in: {self.issue_dir}")
                return True
                
        except Exception as e:
            print(f"Scraping failed for {self.issue_name}: {e}")
            return False
        finally:
            await self._cleanup()
    
    async def _download_cover(self, page) -> bool:
        """
        Download the magazine cover image with timeout.
        
        Args:
            page: Playwright page instance
            
        Returns:
            bool: True if cover was downloaded, False otherwise
        """
        cover_path = self.issue_dir / "cover.jpg"
        
        try:
            cover_element = page.locator(SELECTOR_COVER_IMAGE).first
            cover_url = await cover_element.get_attribute("src", timeout=10000)
            
            if cover_url:
                print(f"Downloading cover: {cover_url}")
                async with httpx.AsyncClient(timeout=HTTP_TIMEOUT) as client:
                    resp = await client.get(cover_url)
                    resp.raise_for_status()
                    with open(cover_path, "wb") as f:
                        f.write(resp.content)
                print(f"✓ Cover saved to {cover_path}")
                return True
        except PlaywrightTimeoutError:
            print("Cover image not found (timeout)")
        except httpx.TimeoutException:
            print("Cover download timed out")
        except Exception as e:
            print(f"Could not download cover image: {e}")
        
        return False
    
    async def _get_article_links(self, page) -> List[str]:
        """
        Extract unique article links from the magazine page.
        
        Args:
            page: Playwright page instance
            
        Returns:
            List[str]: List of unique article URLs
        """
        try:
            link_elements = await page.locator(SELECTOR_ARTICLE_LINKS).all()
            links = []
            
            for element in link_elements:
                href = await element.get_attribute("href")
                if href:
                    full_url = href if href.startswith("http") else f"{BASE_URL}{href}"
                    links.append(full_url)
            
            # Remove duplicates while preserving order
            unique_links = list(dict.fromkeys(links))
            print(f"Found {len(unique_links)} unique articles")
            return unique_links
            
        except Exception as e:
            print(f"Error extracting article links: {e}")
            return []
    
    async def _scrape_articles(self, page, article_links: List[str]) -> None:
        """
        Scrape content from each article page.
        
        Args:
            page: Playwright page instance
            article_links: List of article URLs to scrape
        """
        for i, link in enumerate(article_links):
            try:
                print(f"Processing ({i+1}/{len(article_links)}): {link}")
                
                await page.goto(link, wait_until="domcontentloaded", timeout=BROWSER_NAVIGATION_TIMEOUT)
                
                # Extract author information
                author_name, author_section = await self._extract_author(page)
                
                # Extract content
                html = await page.content()
                title = await page.title()
                clean_title = title.split('|')[0].split('-')[0].replace("Revista Liberta", "").replace("–", "").strip()
                
                content = trafilatura.extract(
                    html,
                    output_format='markdown',
                    include_images=True,
                    include_comments=False,
                    favor_precision=True
                )
                
                if content:
                    file_path = self.issue_dir / f"artigo_{i:02d}.md"
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(f"# {clean_title}\n\n")
                        if author_name:
                            f.write(f"**{author_name}**\n\n")
                        f.write(content)
                        if author_section:
                            f.write(f"\n\n{author_section}")
                    print(f"Saved: {file_path.name}")
                else:
                    print(f"  ! No content extracted for: {link}")
                    
            except PlaywrightTimeoutError:
                print(f"  ! Timeout loading article: {link}")
            except Exception as e:
                print(f"  ! Error processing article {link}: {e}")
    
    async def _extract_author(self, page) -> Tuple[Optional[str], str]:
        """
        Extract author name and bio from the article page.
        
        Args:
            page: Playwright page instance
            
        Returns:
            Tuple[Optional[str], str]: (author_name, formatted_author_section)
        """
        try:
            author_container = page.locator(SELECTOR_AUTHOR_CONTAINER)
            
            if await author_container.count() == 0:
                return None, ""
            
            name = ""
            bio = ""
            
            name_locator = author_container.locator(SELECTOR_AUTHOR_NAME)
            bio_locator = author_container.locator(SELECTOR_AUTHOR_BIO)
            
            if await name_locator.count() > 0:
                name = await name_locator.first.inner_text()
            
            if await bio_locator.count() > 0:
                bio = await bio_locator.first.inner_text()
            
            if name or bio:
                author_section = f"\n\n>**{name.strip()}**\n\n"
                if bio:
                    author_section += f"> *{bio.strip()}*\n\n"
                author_section += "---\n"
                return name.strip(), author_section
            
            return None, ""
            
        except Exception as e:
            print(f"Author extraction skipped: {e}")
            return None, ""
    
    async def _cleanup(self):
        """Ensure all resources are properly cleaned up."""
        if self._context:
            try:
                await self._context.close()
            except Exception:
                pass
            self._context = None
        
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass
            self._browser = None
        
        await self.session_manager.cleanup()


class IndexScraper:
    """Scrapes the index page to find available magazine editions."""
    
    def __init__(self):
        self.session_manager = SessionManager()
        self._browser = None
        self._context = None
    
    async def get_available_editions(self) -> List[str]:
        """
        Scrape the index page for all available magazine slugs.
        
        Returns:
            List[str]: List of edition slugs
        """
        from src.config import INDEX_URL, SELECTOR_EDITION_LINKS
        
        slugs = []
        
        try:
            async with async_playwright() as p:
                self._browser = await p.chromium.launch(headless=True)
                self._context = await self.session_manager.get_or_create_context(self._browser)
                
                page = await self._context.new_page()
                
                print("Searching for available editions...")
                await page.goto(INDEX_URL, timeout=BROWSER_NAVIGATION_TIMEOUT)
                
                links = await page.locator(SELECTOR_EDITION_LINKS).all()
                
                for link in links:
                    try:
                        href = await link.get_attribute("href")
                        if href:
                            # Clean the URL to get just the slug (e.g., 'edicao-18')
                            slug = href.strip("/").split("/")[-1]
                            if slug and slug not in slugs:
                                slugs.append(slug)
                    except Exception:
                        continue
                
                await page.close()
                print(f"Found {len(slugs)} editions")
                return slugs
                
        except Exception as e:
            print(f"Error getting available editions: {e}")
            return []
        finally:
            await self._cleanup()
    
    async def _cleanup(self):
        """Ensure all resources are properly cleaned up."""
        if self._context:
            try:
                await self._context.close()
            except Exception:
                pass
            self._context = None
        
        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass
            self._browser = None
        
        await self.session_manager.cleanup()


# Convenience functions for direct usage
async def scrape_issue(issue_name: str) -> bool:
    """
    Scrape a single magazine issue.
    
    Args:
        issue_name: The edition slug (e.g., 'edicao-18')
        
    Returns:
        bool: True if scraping succeeded, False otherwise
    """
    scraper = MagazineScraper(issue_name)
    return await scraper.scrape()


async def get_editions() -> List[str]:
    """
    Get list of available magazine editions.
    
    Returns:
        List[str]: List of edition slugs
    """
    scraper = IndexScraper()
    return await scraper.get_available_editions()
