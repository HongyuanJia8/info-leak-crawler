# scrapers/base.py
import asyncio
import aiohttp
import logging
import random
from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
from datetime import datetime
import time

from .config import Config
from .utils import Utils

logger = logging.getLogger(__name__)

class BaseScraper(ABC):
    """Base class for all scrapers"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.session = None
        self.results_cache = {}
        
    async def __aenter__(self):
        """Async context manager entry"""
        timeout = aiohttp.ClientTimeout(total=self.config.DEFAULT_TIMEOUT)
        self.session = aiohttp.ClientSession(timeout=timeout)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def get_headers(self) -> Dict[str, str]:
        """Get randomized headers for requests"""
        return {
            'User-Agent': random.choice(self.config.USER_AGENTS),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    async def fetch(self, url: str, retries: int = 0) -> Optional[str]:
        """Fetch URL content with retries"""
        if retries >= self.config.MAX_RETRIES:
            logger.error(f"Max retries reached for {url}")
            return None
        
        try:
            headers = self.get_headers()
            proxy = self.get_proxy() if self.config.PROXY_ENABLED else None
            
            async with self.session.get(url, headers=headers, proxy=proxy) as response:
                if response.status == 200:
                    return await response.text()
                elif response.status == 429:  # Too many requests
                    wait_time = 2 ** retries * 5
                    logger.warning(f"Rate limited on {url}, waiting {wait_time}s")
                    await asyncio.sleep(wait_time)
                    return await self.fetch(url, retries + 1)
                else:
                    logger.warning(f"HTTP {response.status} for {url}")
                    return None
                    
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {url}")
            return await self.fetch(url, retries + 1)
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return await self.fetch(url, retries + 1)
    
    def get_proxy(self) -> Optional[str]:
        """Get a random proxy from the pool"""
        if self.config.PROXY_LIST:
            return random.choice(self.config.PROXY_LIST)
        return None
    
    @abstractmethod
    async def search(self, query: str, pages: int = 1) -> List[Dict[str, Any]]:
        """Search implementation - must be overridden by subclasses"""
        pass
    
    @abstractmethod
    def parse_results(self, html: str) -> List[Dict[str, Any]]:
        """Parse search results - must be overridden by subclasses"""
        pass
    
    async def extract_page_info(self, url: str, user_info: Dict[str, str]) -> Dict[str, Any]:
        """Extract relevant information from a webpage"""
        html = await self.fetch(url)
        if not html:
            return None
        
        # Extract text content (you might want to use BeautifulSoup here)
        text_content = self.extract_text(html)
        
        # Find matches
        matched_info = {}
        
        if user_info.get('name') and user_info['name'].lower() in text_content.lower():
            matched_info['name'] = {
                'value': user_info['name'],
                'confidence': 1.0,
                'context': Utils.extract_context(text_content, user_info['name'])
            }
        
        if user_info.get('email'):
            emails = Utils.extract_email(text_content)
            if user_info['email'] in emails:
                matched_info['email'] = {
                    'value': user_info['email'],
                    'confidence': 1.0,
                    'context': Utils.extract_context(text_content, user_info['email'])
                }
        
        if user_info.get('phone'):
            phones = Utils.extract_phone(text_content)
            if user_info['phone'] in phones:
                matched_info['phone'] = {
                    'value': user_info['phone'],
                    'confidence': 1.0,
                    'context': Utils.extract_context(text_content, user_info['phone'])
                }
        
        return matched_info
    
    def extract_text(self, html: str) -> str:
        """Extract text from HTML (simplified version)"""
        # In production, use BeautifulSoup
        import re
        # Remove script and style elements
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', html)
        # Clean up whitespace
        text = ' '.join(text.split())
        return text