# tools.py

import os
import aiohttp
import asyncio
import requests
from crewai_tools import BaseTool
from bs4 import BeautifulSoup

class EnhancedSerperDevTool(BaseTool):
    name: str = "Enhanced Internet Search"
    description: str = "Perform an internet search and return results."

    def _run(self, query: str, num_results: int = 10):
        url = "https://google.serper.dev/search"
        payload = {"q": query, "num": num_results}
        headers = {
            'X-API-KEY': os.environ['SERPER_API_KEY'],
            'Content-Type': 'application/json'
        }
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
                return data.get('organic', [])
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    return f"Failed to perform search after {max_retries} attempts: {str(e)}"
                asyncio.sleep(1)  # Wait before retrying

class WebScraper(BaseTool):
    name: str = "Web Scraper"
    description: str = "Scrape content from given URLs asynchronously."

    async def scrape_url(self, session, url):
        try:
            async with session.get(url, timeout=10) as response:
                content = await response.text()
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text(separator='\n', strip=True)
                return url, text[:10000]  # Limit to first 10000 characters
        except Exception as e:
            return url, f"Failed to scrape {url}: {str(e)}"

    async def _run(self, urls):
        async with aiohttp.ClientSession() as session:
            tasks = [self.scrape_url(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
        return dict(results)

search_tool = EnhancedSerperDevTool()
scrape_tool = WebScraper()