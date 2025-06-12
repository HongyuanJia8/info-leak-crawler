import asyncio
import logging
from typing import Dict, List, Any, Optional

from .base import BaseScraper
from .config import Config

logger = logging.getLogger(__name__)

class SocialMediaAggregator:
    
    def __init__(self, config=None):
        self.config = config or Config()
        self.platforms = {}
    
    async def search_all(self, query: str, platforms: List[str] = None) -> List[Dict[str, Any]]:
        # Return empty results since we're not using social media platforms
        return []