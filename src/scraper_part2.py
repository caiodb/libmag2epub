
    async def _get_article_links(self, context: BrowserContext) -> List[str]:
        """Extract all article URLs from the magazine landing page."""
        page = await context.new_page()
        try:
            await page.goto(self.url)
            selectors = [
                '.article-list a, .content-grid a, .post-item a',
                'a[href*="/artigo/"], a[href*="/lendo-"], a[data-article]'
            ]
            links = []
            for sel in selectors:
                try:
                    elements = await page.query_selector_all(sel)
                    for elem in elements:
                        href = await elem.get_attribute('href')
                        if href and 'revistaliber' in href.lower():
                            links.append(href)
                except:
                    pass
            return list(set(links))[:20]
        finally:
            await page.close()
    
    async def _scrape_articles(self, context: BrowserContext):
        """Scrape individual article pages."""
        links = await self._get_article_links(context)
        for i, link in enumerate(links):
            print(f"Processing article {i+1}/{len(links)}: {link}")
            page = await context.new_page()
            try:
                await page.goto(link)
                title = await page.title() or "Untitled"
                content = await page.content()
                self.articles_data.append({
                    'title': title,
                    'url': link,
                    'content': content[:50000]  # Limit to first 50KB
                })
            except Exception as e:
                print(f"Error scraping article {link}: {e}")
            finally:
                await page.close()
    
    async def scrape(self) -> bool:
        """Main scraping entry point."""
        from src.session import get_authenticated_context
        try:
            context = await get_authenticated_context(
                url=self.url,
                force_fresh=True,
                timeout=60
            )
            print("Authenticated successfully!")
            self.cover_url = await self._download_cover(context)
            self.article_urls = await self._get_article_links(context)
            await self._scrape_articles(context)
            return True
        except Exception as e:
            print(f"Scraping failed: {e}")
            return False
