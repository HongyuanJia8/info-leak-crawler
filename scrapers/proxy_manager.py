import random
import asyncio
from typing import List, Optional, Dict
import aiohttp
import logging

logger = logging.getLogger(__name__)

class ProxyManager:
    
    def __init__(self):
        self.proxy_list = []
        self.working_proxies = []
        self.failed_proxies = set()
        
    async def load_proxies(self, proxy_sources: List[str] = None):
        if proxy_sources is None:
            proxy_sources = [
                'https://www.proxy-list.download/api/v1/get?type=http',
                'https://api.proxyscrape.com/v2/?request=get&protocol=http'
            ]
        
        for source in proxy_sources:
            try:
                proxies = await self._fetch_proxy_list(source)
                self.proxy_list.extend(proxies)
            except Exception as e:
                logger.error(f"Failed to load proxies from {source}: {str(e)}")
        
        await self.validate_proxies()
    
    async def _fetch_proxy_list(self, url: str) -> List[str]:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    text = await response.text()
                    proxies = text.strip().split('\n')
                    return [f"http://{proxy.strip()}" for proxy in proxies if proxy.strip()]
        return []
    
    async def validate_proxies(self, test_url: str = "http://httpbin.org/ip"):
        logger.info(f"Validating {len(self.proxy_list)} proxies...")
        
        tasks = []
        for proxy in self.proxy_list:
            task = self._test_proxy(proxy, test_url)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for proxy, result in zip(self.proxy_list, results):
            if result is True:
                self.working_proxies.append(proxy)
            else:
                self.failed_proxies.add(proxy)
        
        logger.info(f"Found {len(self.working_proxies)} working proxies")
    
    async def _test_proxy(self, proxy: str, test_url: str) -> bool:
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(test_url, proxy=proxy) as response:
                    return response.status == 200
        except:
            return False
    
    def get_proxy(self) -> Optional[str]:
        if not self.working_proxies:
            return None
        
        proxy = random.choice(self.working_proxies)
        return proxy
    
    def mark_proxy_failed(self, proxy: str):
        if proxy in self.working_proxies:
            self.working_proxies.remove(proxy)
        self.failed_proxies.add(proxy)