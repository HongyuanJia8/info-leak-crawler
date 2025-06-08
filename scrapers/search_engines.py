# scrapers/search_engines.py
import asyncio
import re
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus, urlencode
from bs4 import BeautifulSoup
import logging
from .config import Config
from .base import BaseScraper
from .utils import Utils

logger = logging.getLogger(__name__)

class GoogleScraper(BaseScraper):
    """Google search scraper"""
    
    BASE_URL = "https://www.google.com/search"
    
    async def search(self, query: str, pages: int = 5) -> List[Dict[str, Any]]:
        """Search Google and return results"""
        results = []
        
        for page in range(pages):
            start = page * 10
            params = {
                'q': query,
                'start': start,
                'hl': 'en'
            }
            
            url = f"{self.BASE_URL}?{urlencode(params)}"
            logger.info(f"Searching Google: {url}")
            
            # Add delay between requests
            if page > 0:
                await asyncio.sleep(self.config.DEFAULT_DELAY)
            
            html = await self.fetch(url)
            if html:
                page_results = self.parse_results(html)
                results.extend(page_results)
            else:
                logger.warning(f"Failed to fetch Google page {page + 1}")
                break
        
        return results
    
    def parse_results(self, html: str) -> List[Dict[str, Any]]:
        """Parse Google search results"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Find all search result divs
        for g in soup.find_all('div', class_='g'):
            result = {}
            
            # Extract URL
            link = g.find('a')
            if link and link.get('href'):
                result['url'] = link['href']
            else:
                continue
            
            # Extract title
            h3 = g.find('h3')
            if h3:
                result['title'] = h3.get_text(strip=True)
            
            # Extract snippet
            snippet_div = g.find('div', class_='VwiC3b')
            if snippet_div:
                result['snippet'] = snippet_div.get_text(strip=True)
            
            # Add metadata
            result['source'] = 'google'
            result['rank'] = len(results) + 1
            
            if result.get('url') and result.get('title'):
                results.append(result)
        
        return results

class BingScraper(BaseScraper):
    """Bing search scraper"""
    
    BASE_URL = "https://www.bing.com/search"
    
    async def search(self, query: str, pages: int = 5) -> List[Dict[str, Any]]:
        """Search Bing and return results"""
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
        """Parse Bing search results"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Find all search results
        for li in soup.find_all('li', class_='b_algo'):
            result = {}
            
            # Extract URL and title
            h2 = li.find('h2')
            if h2:
                link = h2.find('a')
                if link:
                    result['url'] = link.get('href', '')
                    result['title'] = link.get_text(strip=True)
            
            # Extract snippet
            caption = li.find('div', class_='b_caption')
            if caption:
                p = caption.find('p')
                if p:
                    result['snippet'] = p.get_text(strip=True)
            
            # Add metadata
            result['source'] = 'bing'
            result['rank'] = len(results) + 1
            
            if result.get('url') and result.get('title'):
                results.append(result)
        
        return results

class BaiduScraper(BaseScraper):
    """Baidu search scraper (for Chinese users)"""
    
    BASE_URL = "https://www.baidu.com/s"
    
    async def search(self, query: str, pages: int = 5) -> List[Dict[str, Any]]:
        """Search Baidu and return results"""
        results = []
        
        for page in range(pages):
            pn = page * 10
            params = {
                'wd': query,
                'pn': pn,
                'ie': 'utf-8'
            }
            
            url = f"{self.BASE_URL}?{urlencode(params)}"
            logger.info(f"Searching Baidu: {url}")
            
            if page > 0:
                await asyncio.sleep(self.config.DEFAULT_DELAY)
            
            # Baidu requires specific headers
            self.session.headers.update({
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
            })
            
            html = await self.fetch(url)
            if html:
                page_results = self.parse_results(html)
                results.extend(page_results)
            else:
                logger.warning(f"Failed to fetch Baidu page {page + 1}")
                break
        
        return results
    
    def parse_results(self, html: str) -> List[Dict[str, Any]]:
        """Parse Baidu search results"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Find all search result containers
        for div in soup.find_all('div', class_='result'):
            result = {}
            
            # Extract URL and title
            h3 = div.find('h3', class_='t')
            if h3:
                link = h3.find('a')
                if link:
                    result['url'] = link.get('href', '')
                    result['title'] = link.get_text(strip=True)
            
            # Extract snippet
            abstract = div.find('div', class_='c-abstract')
            if not abstract:
                abstract = div.find('span', class_='content-right_8Zs40')
            
            if abstract:
                result['snippet'] = abstract.get_text(strip=True)
            
            # Add metadata
            result['source'] = 'baidu'
            result['rank'] = len(results) + 1
            
            if result.get('url') and result.get('title'):
                # Baidu uses redirect URLs, we need to resolve them
                result['url'] = self._resolve_baidu_url(result['url'])
                results.append(result)
        
        return results
    
    def _resolve_baidu_url(self, baidu_url: str) -> str:
        """Resolve Baidu's redirect URL to actual URL"""
        # In a real implementation, you would follow the redirect
        # For now, we'll just return the Baidu URL
        return baidu_url
    
class DuckDuckGoScraper(BaseScraper):
    """DuckDuckGo search scraper"""
    
    BASE_URL = "https://duckduckgo.com/html/"
    
    async def search(self, query: str, pages: int = 3) -> List[Dict[str, Any]]:
        """Search DuckDuckGo and return results"""
        results = []
        
        # DuckDuckGo HTML version only shows first page easily
        params = {
            'q': query,
            'kl': 'us-en'
        }
        
        url = f"{self.BASE_URL}?{urlencode(params)}"
        logger.info(f"Searching DuckDuckGo: {url}")
        
        html = await self.fetch(url)
        if html:
            results = self.parse_results(html)
        else:
            logger.warning("Failed to fetch DuckDuckGo results")
        
        return results
    
    def parse_results(self, html: str) -> List[Dict[str, Any]]:
        """Parse DuckDuckGo search results"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Find all result divs
        for div in soup.find_all('div', class_=['result', 'results_links_deep']):
            result = {}
            
            # Extract URL and title
            h2 = div.find('h2', class_='result__title')
            if h2:
                link = h2.find('a', class_='result__a')
                if link:
                    result['url'] = link.get('href', '')
                    result['title'] = link.get_text(strip=True)
            
            # Extract snippet
            snippet = div.find('a', class_='result__snippet')
            if snippet:
                result['snippet'] = snippet.get_text(strip=True)
            
            # Add metadata
            result['source'] = 'duckduckgo'
            result['rank'] = len(results) + 1
            
            if result.get('url') and result.get('title'):
                results.append(result)
        
        return results

class SearchEngineAggregator:
    """Aggregate results from multiple search engines"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.engines = {
            'google': GoogleScraper(config),
            'bing': BingScraper(config),
            'baidu': BaiduScraper(config),
            'duckduckgo': DuckDuckGoScraper(config)
        }
    
    async def search_all(self, query: str, engines: List[str] = None, pages_per_engine: int = 3) -> List[Dict[str, Any]]:
        """Search multiple engines and aggregate results"""
        if engines is None:
            engines = ['google', 'bing']  # Default engines
        
        all_results = []
        
        # Create tasks for all engines
        tasks = []
        for engine_name in engines:
            if engine_name in self.engines:
                engine = self.engines[engine_name]
                task = self._search_engine(engine, query, pages_per_engine)
                tasks.append(task)
        
        # Execute all searches concurrently
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        for results in results_lists:
            if isinstance(results, list):
                all_results.extend(results)
            else:
                logger.error(f"Search engine error: {results}")
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_results = []
        
        for result in all_results:
            url = Utils.clean_url(result.get('url', ''))
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
    
    async def _search_engine(self, engine: BaseScraper, query: str, pages: int) -> List[Dict[str, Any]]:
        """Search a single engine with error handling"""
        try:
            async with engine:
                return await engine.search(query, pages)
        except Exception as e:
            logger.error(f"Error searching {engine.__class__.__name__}: {str(e)}")
            return []