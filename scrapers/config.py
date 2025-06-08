import os
from typing import Dict, Any

class Config:
    """Configuration settings for the scraper module"""
    
    # Request settings
    DEFAULT_TIMEOUT = 30
    DEFAULT_DELAY = 2  # seconds between requests
    MAX_RETRIES = 3
    CONCURRENT_REQUESTS = 10
    
    # User agents
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    
    # Proxy settings
    PROXY_ENABLED = False
    PROXY_LIST = []
    
    # Search settings
    MAX_SEARCH_PAGES = 5
    RESULTS_PER_PAGE = 10
    
    # API Keys (set via environment variables)
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID', '')
    BING_API_KEY = os.getenv('BING_API_KEY', '')
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'scraper.log'