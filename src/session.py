"""
Session management module for handling authentication with the magazine website.
Ensures proper resource cleanup on all error paths to prevent memory leaks.
"""

import json
import os
from playwright.async_api import async_playwright, Browser, BrowserContext, TimeoutError as PlaywrightTimeoutError
from src.config import (
    AUTH_FILE,
    LIBER_USER,
    LIBER_PASS,
    LOGIN_URL,
    LOGIN_TIMEOUT,
    SELECTOR_LOGIN_USERNAME,
    SELECTOR_LOGIN_PASSWORD,
    SELECTOR_LOGIN_SUBMIT_ID,
    SELECTOR_LOGIN_SUBMIT_NAME,
    SELECTOR_LOGIN_SUBMIT_TEXT,
)


class SessionManager:
    """Manages browser sessions and authentication state."""
    
    def __init__(self):
        self._context = None
        self._browser = None
    
    async def get_or_create_context(self, browser: Browser) -> BrowserContext:
        """
        Get existing session context or perform login to create a new one.
        Ensures context.close() is called on all error paths.
        
        Args:
            browser: Playwright browser instance
            
        Returns:
            BrowserContext: Authenticated browser context
        """
        try:
            if self._is_valid_auth_file():
                print("Loading existing session...")
                self._context = await browser.new_context(
                    storage_state=str(AUTH_FILE),
                    viewport={"width": 1280, "height": 720}
                )
                return self._context
            else:
                print("No valid session found. Performing login...")
                self._context = await self._perform_login(browser)
                return self._context
        except Exception:
            raise
    
    def _is_valid_auth_file(self) -> bool:
        """
        Check if auth file exists and contains valid JSON.
        
        Returns:
            bool: True if file exists and has valid content
        """
        if not os.path.exists(AUTH_FILE):
            return False
        
        try:
            with open(AUTH_FILE, 'r') as f:
                content = f.read().strip()
                if not content:
                    return False
                # Try to parse as JSON
                json.loads(content)
                return True
        except (json.JSONDecodeError, IOError):
            return False
    
    async def _perform_login(self, browser: Browser) -> BrowserContext:
        """
        Perform automated login and save session state.
        Uses try-finally to ensure context is always closed on errors.
        
        Args:
            browser: Playwright browser instance
            
        Returns:
            BrowserContext: Authenticated browser context
        """
        context = None
        page = None
        
        try:
            context = await browser.new_context(viewport={"width": 1280, "height": 720})
            page = await context.new_page()
            
            print(f"Logging in as {LIBER_USER}...")
            
            # Navigate to login page with timeout
            await page.goto(LOGIN_URL, wait_until="networkidle", timeout=30000)
            
            # Fill credentials
            await page.fill(SELECTOR_LOGIN_USERNAME, LIBER_USER)
            await page.fill(SELECTOR_LOGIN_PASSWORD, LIBER_PASS)
            
            # Attempt to click login button with fallback selectors
            login_clicked = await self._click_login_button(page)
            
            if not login_clicked:
                raise RuntimeError("Could not find or click login button")
            
            # Wait for navigation to complete
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            # Verify login was successful (check for login form absence or dashboard presence)
            if await page.locator(SELECTOR_LOGIN_USERNAME).count() > 0:
                raise RuntimeError("Login failed: still on login page")
            
            # Save session state
            await context.storage_state(path=str(AUTH_FILE))
            print(f"Login successful. Session saved to {AUTH_FILE}")
            
            self._context = context
            return context
            
        except Exception as e:
            # Ensure context is closed on any error
            if context:
                try:
                    await context.close()
                except Exception:
                    pass
            raise RuntimeError(f"Login failed: {e}") from e
        finally:
            # Clean up page if context is not being returned
            if page and not self._context:
                try:
                    await page.close()
                except Exception:
                    pass
    
    async def _click_login_button(self, page) -> bool:
        """
        Try multiple selectors to click the login button.
        
        Args:
            page: Playwright page instance
            
        Returns:
            bool: True if button was clicked, False otherwise
        """
        selectors = [
            SELECTOR_LOGIN_SUBMIT_ID,
            SELECTOR_LOGIN_SUBMIT_NAME,
            SELECTOR_LOGIN_SUBMIT_TEXT,
        ]
        
        for selector in selectors:
            try:
                await page.click(selector, timeout=LOGIN_TIMEOUT)
                print(f"Clicked login button using selector: {selector}")
                return True
            except PlaywrightTimeoutError:
                continue
            except Exception:
                continue
        
        return False
    
    async def cleanup(self):
        """Explicitly clean up resources."""
        if self._context:
            try:
                await self._context.close()
            except Exception:
                pass
            self._context = None


async def perform_login(browser: Browser) -> BrowserContext:
    """
    Standalone function for backward compatibility.
    Creates a new SessionManager and performs login.
    
    Args:
        browser: Playwright browser instance
        
    Returns:
        BrowserContext: Authenticated browser context
    """
    manager = SessionManager()
    return await manager._perform_login(browser)


async def get_context(browser: Browser) -> BrowserContext:
    """
    Standalone function to get or create authenticated context.
    
    Args:
        browser: Playwright browser instance
        
    Returns:
        BrowserContext: Authenticated browser context
    """
    manager = SessionManager()
    return await manager.get_or_create_context(browser)
