

class IndexScraper:
    """Scraper for the magazine index page."""
    
    def __init__(self):
        self.base_url = "https://revistaliber.ta.com.br/edicoes/"
    
    async def get_available_editions(self) -> List[str]:
        """Get list of available magazine editions."""
        from src.session import get_authenticated_context
        try:
            context = await get_authenticated_context(
                url=self.base_url,
                force_fresh=False,
                timeout=60
            )
            page = await context.new_page()
            try:
                await page.goto(self.base_url)
                selectors = [
                    '.edition-list a, .issue-grid a',
                    'a[href*="/edicao/"]'
                ]
                editions = []
                for sel in selectors:
                    try:
                        elements = await page.query_selector_all(sel)
                        for elem in elements:
                            href = await elem.get_attribute('href')
                            if href and 'revistaliber' in href.lower():
                                # Extract edition slug from URL
                                parts = href.split('/')
                                for part in parts:
                                    if part.startswith('edicao-'):
                                        editions.append(part)
                    except:
                        pass
                return list(set(editions))[:50]
            finally:
                await page.close()
        except Exception as e:
            print(f"Failed to get editions: {e}")
            return []
