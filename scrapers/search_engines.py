import asyncio
import re
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus, urlencode
from bs4 import BeautifulSoup
import logging

from .base import BaseScraper
from .utils import Utils
from .config import Config

logger = logging.getLogger(__name__)

class BingScraper(BaseScraper):
    
    BASE_URL = "https://www.bing.com/search"
    
    async def search(self, query: str, pages: int = 5) -> List[Dict[str, Any]]:
        results = []
        
        for page in range(pages):
            first = page * 10 + 1
            params = {
                'q': query,
                'first': first
            }
            
            url = f"{self.BASE_URL}?{urlencode(params)}"
            logger.info(f"Searching Bing: {url}")
            
            if page > 0:
                await asyncio.sleep(self.config.DEFAULT_DELAY)
            
            html = await self.fetch(url)
            if html:
                page_results = self.parse_results(html)
                results.extend(page_results)
            else:
                logger.warning(f"Failed to fetch Bing page {page + 1}")
                break
        
        return results
    
    def parse_results(self, html: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        for li in soup.find_all('li', class_='b_algo'):
            result = {}
            
            h2 = li.find('h2')
            if h2:
                link = h2.find('a')
                if link:
                    result['url'] = link.get('href', '')
                    result['title'] = link.get_text(strip=True)
            
            caption = li.find('div', class_='b_caption')
            if caption:
                p = caption.find('p')
                if p:
                    result['snippet'] = p.get_text(strip=True)
            
            result['source'] = 'bing'
            result['rank'] = len(results) + 1
            
            if result.get('url') and result.get('title'):
                results.append(result)
        
        return results

class SearchEngineAggregator:
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.engines = {
            'bing': BingScraper(config)
        }
    
    async def search_all(self, query: str, engines: List[str] = None, pages_per_engine: int = 3) -> List[Dict[str, Any]]:
        if engines is None:
            engines = ['bing']
        
        all_results = []
        
        tasks = []
        for engine_name in engines:
            if engine_name in self.engines:
                engine = self.engines[engine_name]
                task = self._search_engine(engine, query, pages_per_engine)
                tasks.append(task)
        
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        for results in results_lists:
            if isinstance(results, list):
                all_results.extend(results)
            else:
                logger.error(f"Search engine error: {results}")
        
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            url = Utils.clean_url(result.get('url', ''))
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
    
    async def _search_engine(self, engine: BaseScraper, query: str, pages: int) -> List[Dict[str, Any]]:
        try:
            async with engine:
                return await engine.search(query, pages)
        except Exception as e:
            logger.error(f"Error searching {engine.__class__.__name__}: {str(e)}")
            return []