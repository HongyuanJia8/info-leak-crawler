# scrapers/utils.py
import re
import hashlib
import random
import time
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, quote_plus
import logging

logger = logging.getLogger(__name__)

class Utils:
    """Utility functions for the scraper module"""
    
    @staticmethod
    def extract_email(text: str) -> List[str]:
        """Extract email addresses from text"""
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_phone(text: str) -> List[str]:
        """Extract phone numbers from text (supports multiple formats)"""
        patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US format
            r'\b\d{11}\b',  # 11 digit format
            r'\b\+1[-\s]?\d{3}[-\s]?\d{3}[-\s]?\d{4}\b',  # US format with country code
            r'\b\(\d{3}\)\s*\d{3}[-.]?\d{4}\b',  # US format with parentheses
            r'\b\+44[-\s]?\d{4}[-\s]?\d{6}\b',  # UK format
        ]
        
        results = []
        for pattern in patterns:
            results.extend(re.findall(pattern, text))
        
        return list(set(results))
    
    @staticmethod
    def extract_address(text: str) -> List[str]:
        """Extract potential addresses from text"""
        # This is a simplified version - you might want to use a proper NLP library
        patterns = [
            r'\d+\s+[\w\s]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Lane|Ln|Drive|Dr|Court|Ct|Plaza|Pl)',  # US address
            r'\b\d{5}(?:-\d{4})?\b',  # ZIP codes
        ]
        
        results = []
        for pattern in patterns:
            results.extend(re.findall(pattern, text, re.IGNORECASE))
        
        return results
    
    @staticmethod
    def calculate_similarity(text1: str, text2: str) -> float:
        """Calculate similarity between two strings (0-1)"""
        if not text1 or not text2:
            return 0.0
        
        # Simple character-based similarity
        set1 = set(text1.lower())
        set2 = set(text2.lower())
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def extract_context(text: str, keyword: str, context_size: int = 50) -> str:
        """Extract text context around a keyword"""
        if keyword not in text:
            return ""
        
        index = text.find(keyword)
        start = max(0, index - context_size)
        end = min(len(text), index + len(keyword) + context_size)
        
        context = text[start:end]
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        
        return context
    
    @staticmethod
    def generate_search_queries(info: Dict[str, str]) -> List[str]:
        """Generate search queries from user information"""
        queries = []
        
        # Single field queries
        if info.get('name'):
            queries.append(f'"{info["name"]}"')
        
        # Combination queries
        if info.get('name') and info.get('phone'):
            queries.append(f'"{info["name"]}" "{info["phone"]}"')
        
        if info.get('name') and info.get('email'):
            queries.append(f'"{info["name"]}" "{info["email"]}"')
        
        if info.get('name') and info.get('address'):
            queries.append(f'"{info["name"]}" "{info["address"]}"')
        
        if info.get('email'):
            queries.append(f'"{info["email"]}"')
        
        if info.get('phone') and info.get('email'):
            queries.append(f'"{info["phone"]}" "{info["email"]}"')
        
        return queries
    
    @staticmethod
    def clean_url(url: str) -> str:
        """Clean and normalize URL"""
        if not url:
            return ""
        
        # Remove URL parameters
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    @staticmethod
    def get_domain(url: str) -> str:
        """Extract domain from URL"""
        parsed = urlparse(url)
        return parsed.netloc
    
    @staticmethod
    def random_delay(min_delay: float = 1.0, max_delay: float = 3.0):
        """Random delay between requests"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    @staticmethod
    def hash_content(content: str) -> str:
        """Generate hash for content deduplication"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()