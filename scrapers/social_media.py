# scrapers/social_media.py
import asyncio
import json
import re
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus, urlencode
from bs4 import BeautifulSoup
import logging

from .base import BaseScraper
from .utils import Utils
from .config import Config

# Import search engines for reuse
from .search_engines import GoogleScraper

logger = logging.getLogger(__name__)

class TwitterScraper(BaseScraper):
    """Twitter/X search scraper using Google search"""
    
    BASE_URL = "https://twitter.com/search"
    
    def __init__(self, config=None):
        super().__init__(config)
    
    async def search(self, query: str, pages: int = 3) -> List[Dict[str, Any]]:
        """Search Twitter using web scraping (no Selenium for easier setup)"""
        results = []
        
        # Use Google to search Twitter instead of direct Twitter scraping
        # This avoids the need for Selenium and Twitter's strict anti-scraping
        google_query = f"site:twitter.com {query}"
        
        # Reuse Google search functionality
        google_scraper = GoogleScraper(self.config)
        
        try:
            async with google_scraper:
                search_results = await google_scraper.search(google_query, pages=2)
                
                for result in search_results:
                    # Transform Google results to Twitter format
                    twitter_result = {
                        'source': 'twitter',
                        'type': 'tweet',
                        'url': result.get('url', ''),
                        'title': result.get('title', ''),
                        'snippet': result.get('snippet', ''),
                        'content': result.get('snippet', ''),
                        'author': self._extract_twitter_username(result.get('title', ''))
                    }
                    results.append(twitter_result)
        
        except Exception as e:
            logger.error(f"Error searching Twitter: {str(e)}")
        
        return results
    
    def _extract_twitter_username(self, title: str) -> str:
        """Extract Twitter username from title"""
        # Twitter usernames often appear as @username
        match = re.search(r'@(\w+)', title)
        if match:
            return match.group(1)
        # Or in format "Name (@username)"
        match = re.search(r'\((@\w+)\)', title)
        if match:
            return match.group(1)
        return "Unknown"
    
    def _setup_selenium_driver(self):
        """Setup Selenium Chrome driver - removed as not needed"""
        pass
    
    def _extract_tweets(self, driver) -> List[Dict[str, Any]]:
        """Extract tweet data - removed as not needed"""
        pass
    
    def parse_results(self, html: str) -> List[Dict[str, Any]]:
        """Parse results - not used for Twitter as we use Selenium"""
        return []

class LinkedInScraper(BaseScraper):
    """LinkedIn search scraper using Bing"""
    
    BASE_URL = "https://www.linkedin.com/search/results/people/"
    
    def __init__(self, config=None):
        super().__init__(config)
        # Import here to avoid circular imports
        from .search_engines import BingScraper
        self.BingScraper = BingScraper
    
    async def search(self, query: str, pages: int = 2) -> List[Dict[str, Any]]:
        """Search LinkedIn profiles using Bing"""
        results = []
        
        # Search LinkedIn via Bing (more reliable than Google)
        bing_query = f"site:linkedin.com/in/ {query}"
        
        # Use Bing search
        bing_scraper = self.BingScraper(self.config)
        
        try:
            async with bing_scraper:
                search_results = await bing_scraper.search(bing_query, pages=pages)
                
                for result in search_results:
                    # Transform Bing results to LinkedIn format
                    linkedin_result = {
                        'source': 'linkedin',
                        'type': 'profile',
                        'url': result.get('url', ''),
                        'title': result.get('title', ''),
                        'snippet': result.get('snippet', ''),
                        'profile_name': self._extract_profile_name(result.get('title', ''))
                    }
                    results.append(linkedin_result)
        
        except Exception as e:
            logger.error(f"Error searching LinkedIn: {str(e)}")
        
        return results
    
    def _extract_profile_name(self, title: str) -> str:
        """Extract profile name from LinkedIn title"""
        # LinkedIn titles often have format "Name - Title - LinkedIn"
        parts = title.split(' - ')
        if parts:
            return parts[0].strip()
        return title
    
    def _setup_selenium_driver(self):
        """Setup Selenium Chrome driver - removed as not needed"""
        pass
    
    def parse_results(self, html: str) -> List[Dict[str, Any]]:
        """Parse results - not used for LinkedIn as we use Selenium"""
        return []

class GitHubScraper(BaseScraper):
    """GitHub search scraper"""
    
    BASE_URL = "https://github.com/search"
    API_URL = "https://api.github.com/search"
    
    async def search(self, query: str, pages: int = 3) -> List[Dict[str, Any]]:
        """Search GitHub for code and users"""
        results = []
        
        # Search in code
        code_results = await self._search_code(query, pages)
        results.extend(code_results)
        
        # Search in users
        user_results = await self._search_users(query)
        results.extend(user_results)
        
        return results
    
    async def _search_code(self, query: str, pages: int) -> List[Dict[str, Any]]:
        """Search in GitHub code"""
        results = []
        
        for page in range(1, pages + 1):
            params = {
                'q': query,
                'type': 'code',
                'p': page
            }
            
            url = f"{self.BASE_URL}?{urlencode(params)}"
            
            if page > 1:
                await asyncio.sleep(self.config.DEFAULT_DELAY)
            
            html = await self.fetch(url)
            if html:
                page_results = self._parse_code_results(html)
                results.extend(page_results)
            else:
                break
        
        return results
    
    async def _search_users(self, query: str) -> List[Dict[str, Any]]:
        """Search GitHub users"""
        results = []
        
        params = {
            'q': query,
            'type': 'users'
        }
        
        url = f"{self.BASE_URL}?{urlencode(params)}"
        html = await self.fetch(url)
        
        if html:
            results = self._parse_user_results(html)
        
        return results
    
    def _parse_code_results(self, html: str) -> List[Dict[str, Any]]:
        """Parse GitHub code search results"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Find all code result divs
        for div in soup.find_all('div', class_='code-list-item'):
            result = {
                'source': 'github',
                'type': 'code'
            }
            
            # Extract file path and repository
            title_elem = div.find('a', class_='link-gray-dark')
            if title_elem:
                result['title'] = title_elem.text.strip()
                result['url'] = f"https://github.com{title_elem['href']}"
            
            # Extract code snippet
            code_elem = div.find('div', class_='code-list-item-code')
            if code_elem:
                result['snippet'] = code_elem.text.strip()
            
            # Extract repository info
            repo_elem = div.find('a', class_='link-gray')
            if repo_elem:
                result['repository'] = repo_elem.text.strip()
            
            if result.get('url'):
                results.append(result)
        
        return results
    
    def _parse_user_results(self, html: str) -> List[Dict[str, Any]]:
        """Parse GitHub user search results"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        # Find all user results
        for div in soup.find_all('div', class_='user-list-item'):
            result = {
                'source': 'github',
                'type': 'user'
            }
            
            # Extract username and profile URL
            user_elem = div.find('a', class_='color-text-primary')
            if user_elem:
                result['title'] = f"GitHub User: {user_elem.text.strip()}"
                result['url'] = f"https://github.com{user_elem['href']}"
                result['username'] = user_elem.text.strip()
            
            # Extract user details
            details_elem = div.find('div', class_='user-list-info')
            if details_elem:
                result['snippet'] = details_elem.text.strip()
            
            if result.get('url'):
                results.append(result)
        
        return results
    
    def parse_results(self, html: str) -> List[Dict[str, Any]]:
        """Generic parse method - not used as we have specific parsers"""
        return []

class RedditScraper(BaseScraper):
    """Reddit search scraper"""
    
    BASE_URL = "https://www.reddit.com/search"
    
    def __init__(self, config=None):
        super().__init__(config)
        # Import GoogleScraper here to avoid circular imports
        from .search_engines import GoogleScraper
        self.GoogleScraper = GoogleScraper
    
    async def search(self, query: str, pages: int = 3) -> List[Dict[str, Any]]:
        """Search Reddit posts and comments"""
        results = []
        
        params = {
            'q': query,
            'sort': 'relevance',
            't': 'all'  # Time: all
        }
        
        url = f"{self.BASE_URL}.json?{urlencode(params)}"
        
        # Reddit API requires a unique User-Agent
        headers = self.get_headers()
        headers.update({
            'User-Agent': 'PrivacyScanner/1.0 (by /u/your_username)',  # Reddit requires this format
            'Accept': 'application/json'
        })
        
        try:
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    results = self._parse_reddit_json(data)
                elif response.status == 403:
                    logger.warning("Reddit access forbidden - using Google search instead")
                    # Fallback to Google search for Reddit
                    google_query = f"site:reddit.com {query}"
                    google_scraper = self.GoogleScraper(self.config)
                    async with google_scraper:
                        google_results = await google_scraper.search(google_query, pages=2)
                        for g_result in google_results:
                            reddit_result = {
                                'source': 'reddit',
                                'type': 'post',
                                'url': g_result.get('url', ''),
                                'title': g_result.get('title', ''),
                                'snippet': g_result.get('snippet', '')
                            }
                            results.append(reddit_result)
                else:
                    logger.warning(f"Reddit returned status {response.status}")
        except Exception as e:
            logger.error(f"Error searching Reddit: {str(e)}")
            # Fallback to Google search
            try:
                google_query = f"site:reddit.com {query}"
                google_scraper = self.GoogleScraper(self.config)
                async with google_scraper:
                    google_results = await google_scraper.search(google_query, pages=2)
                    for g_result in google_results:
                        reddit_result = {
                            'source': 'reddit',
                            'type': 'post',
                            'url': g_result.get('url', ''),
                            'title': g_result.get('title', ''),
                            'snippet': g_result.get('snippet', '')
                        }
                        results.append(reddit_result)
            except Exception as e2:
                logger.error(f"Google fallback also failed: {str(e2)}")
        
        return results
    
    def _parse_reddit_json(self, data: Dict) -> List[Dict[str, Any]]:
        """Parse Reddit JSON response"""
        results = []
        
        try:
            posts = data.get('data', {}).get('children', [])
            
            for post in posts:
                post_data = post.get('data', {})
                
                result = {
                    'source': 'reddit',
                    'type': 'post',
                    'title': post_data.get('title', ''),
                    'url': f"https://reddit.com{post_data.get('permalink', '')}",
                    'snippet': post_data.get('selftext', '')[:200] + "..." if post_data.get('selftext') else '',
                    'author': post_data.get('author', ''),
                    'subreddit': post_data.get('subreddit', ''),
                    'score': post_data.get('score', 0)
                }
                
                if result['url'] and result['title']:
                    results.append(result)
        
        except Exception as e:
            logger.error(f"Error parsing Reddit JSON: {str(e)}")
        
        return results
    
    def parse_results(self, html: str) -> List[Dict[str, Any]]:
        """Parse HTML results - not used for Reddit as we use JSON"""
        return []

class SocialMediaAggregator:
    """Aggregate results from multiple social media platforms"""
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.platforms = {
            'github': GitHubScraper(config),
            'linkedin': LinkedInScraper(config)
        }
    
    async def search_all(self, query: str, platforms: List[str] = None) -> List[Dict[str, Any]]:
        """Search multiple social media platforms"""
        if platforms is None:
            platforms = ['github', 'linkedin']  # Default platforms
        
        all_results = []
        
        # Create tasks for all platforms
        tasks = []
        for platform_name in platforms:
            if platform_name in self.platforms:
                platform = self.platforms[platform_name]
                task = self._search_platform(platform, query)
                tasks.append(task)
        
        # Execute all searches concurrently
        results_lists = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine results
        for results in results_lists:
            if isinstance(results, list):
                all_results.extend(results)
            else:
                logger.error(f"Social media search error: {results}")
        
        return all_results
    
    async def _search_platform(self, platform: BaseScraper, query: str) -> List[Dict[str, Any]]:
        """Search a single platform with error handling"""
        try:
            async with platform:
                return await platform.search(query)
        except Exception as e:
            logger.error(f"Error searching {platform.__class__.__name__}: {str(e)}")
            return []