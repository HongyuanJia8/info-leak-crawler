# scrapers/privacy_scanner.py
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

from .config import Config
from .search_engines import SearchEngineAggregator
from .social_media import SocialMediaAggregator
from .data_extractor import DataExtractor
from .utils import Utils

logger = logging.getLogger(__name__)

class PrivacyScanner:
    """Main privacy scanner that coordinates all components"""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.search_aggregator = SearchEngineAggregator(config)
        self.social_aggregator = SocialMediaAggregator(config)
        self.data_extractor = DataExtractor()
        self.results_cache = {}
        
    async def scan(self, user_info: Dict[str, str], options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Perform a complete privacy scan for user information
        
        Args:
            user_info: Dictionary with user information (name, email, phone, address)
            options: Optional scan options (search_engines, social_platforms, max_results)
        
        Returns:
            Dictionary with scan results
        """
        options = options or {}
        start_time = datetime.utcnow()
        
        # Generate search queries
        queries = Utils.generate_search_queries(user_info)
        logger.info(f"Generated {len(queries)} search queries")
        
        # Perform searches
        all_results = []
        
        # Search engines
        search_engines = options.get('search_engines', ['google', 'bing'])
        for query in queries:
            logger.info(f"Searching for: {query}")
            
            # Check cache
            cache_key = f"{query}:{','.join(search_engines)}"
            if cache_key in self.results_cache:
                results = self.results_cache[cache_key]
            else:
                results = await self.search_aggregator.search_all(
                    query, 
                    engines=search_engines,
                    pages_per_engine=options.get('pages_per_engine', 3)
                )
                self.results_cache[cache_key] = results
            
            all_results.extend(results)
        
        # Social media platforms
        social_platforms = options.get('social_platforms', ['github', 'reddit'])
        if social_platforms:
            for query in queries[:2]:  # Limit social media queries
                social_results = await self.social_aggregator.search_all(
                    query,
                    platforms=social_platforms
                )
                all_results.extend(social_results)
        
        # Remove duplicates
        unique_results = self._deduplicate_results(all_results)
        logger.info(f"Found {len(unique_results)} unique results")
        
        # Extract detailed information from each result
        detailed_results = []
        max_detailed = options.get('max_detailed_results', 20)
        
        for i, result in enumerate(unique_results[:max_detailed]):
            try:
                # Fetch the actual page content
                html = await self._fetch_with_retry(result['url'])
                if html:
                    # Extract personal information
                    extracted = await self.data_extractor.extract_personal_info(
                        result['url'],
                        html,
                        user_info
                    )
                    
                    # Merge with search result
                    detailed_result = {**result, **extracted}
                    detailed_results.append(detailed_result)
                else:
                    # Use search result snippet only
                    snippet_analysis = self._analyze_snippet(result, user_info)
                    detailed_result = {**result, **snippet_analysis}
                    detailed_results.append(detailed_result)
                    
            except Exception as e:
                logger.error(f"Error processing {result['url']}: {str(e)}")
        
        # Sort by privacy score (highest risk first)
        detailed_results.sort(key=lambda x: x.get('privacy_score', 0), reverse=True)
        
        # Generate summary
        summary = self._generate_summary(detailed_results, user_info)
        
        # Calculate total scan time
        scan_time = (datetime.utcnow() - start_time).total_seconds()
        
        return {
            'scan_id': Utils.hash_content(str(user_info) + str(start_time)),
            'user_info': user_info,
            'scan_time': scan_time,
            'total_results_found': len(unique_results),
            'detailed_results': detailed_results,
            'summary': summary,
            'scan_date': start_time.isoformat(),
            'options': options
        }
    
    async def _fetch_with_retry(self, url: str, max_retries: int = 2) -> Optional[str]:
        """Fetch URL content with retries"""
        for attempt in range(max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {
                        'User-Agent': self.config.USER_AGENTS[0],
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                    }
                    async with session.get(url, headers=headers, timeout=30) as response:
                        if response.status == 200:
                            return await response.text()
                        elif response.status == 404:
                            return None
                        else:
                            logger.warning(f"HTTP {response.status} for {url}")
                            if attempt < max_retries - 1:
                                await asyncio.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Error fetching {url}: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
        
        return None
    
    def _deduplicate_results(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate results based on URL"""
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = Utils.clean_url(result.get('url', ''))
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
    
    def _analyze_snippet(self, result: Dict[str, Any], user_info: Dict[str, str]) -> Dict[str, Any]:
        """Analyze search result snippet for personal information"""
        snippet = result.get('snippet', '')
        title = result.get('title', '')
        combined_text = f"{title} {snippet}".lower()
        
        matched_info = {}
        privacy_score = 0
        
        # Check for name
        if user_info.get('name') and user_info['name'].lower() in combined_text:
            matched_info['name'] = {
                'value': user_info['name'],
                'confidence': 0.8,
                'context': snippet,
                'match_type': 'snippet'
            }
            privacy_score += 15
        
        # Check for email
        if user_info.get('email'):
            emails = Utils.extract_email(combined_text)
            if any(email.lower() == user_info['email'].lower() for email in emails):
                matched_info['email'] = {
                    'value': user_info['email'],
                    'confidence': 0.9,
                    'context': snippet,
                    'match_type': 'snippet'
                }
                privacy_score += 25
        
        # Check for phone
        if user_info.get('phone'):
            phones = Utils.extract_phone(combined_text)
            normalized_user = re.sub(r'\D', '', user_info['phone'])
            for phone in phones:
                if re.sub(r'\D', '', phone) == normalized_user:
                    matched_info['phone'] = {
                        'value': user_info['phone'],
                        'confidence': 0.9,
                        'context': snippet,
                        'match_type': 'snippet'
                    }
                    privacy_score += 30
                    break
        
        return {
            'matched_info': matched_info,
            'privacy_score': min(privacy_score, 70),  # Cap snippet-based scores
            'risk_assessment': {
                'risk_level': 'low' if privacy_score < 20 else 'medium' if privacy_score < 40 else 'high',
                'based_on': 'snippet_analysis'
            }
        }
    
    def _generate_summary(self, results: List[Dict[str, Any]], user_info: Dict[str, str]) -> Dict[str, Any]:
        """Generate a summary of the scan results"""
        summary = {
            'total_exposures': len(results),
            'high_risk_exposures': 0,
            'medium_risk_exposures': 0,
            'low_risk_exposures': 0,
            'exposed_information': defaultdict(int),
            'top_domains': defaultdict(int),
            'recommendations': [],
            'overall_risk_level': 'low'
        }
        
        # Count risk levels and exposed information
        for result in results:
            risk_level = result.get('risk_assessment', {}).get('risk_level', 'low')
            if risk_level == 'high':
                summary['high_risk_exposures'] += 1
            elif risk_level == 'medium':
                summary['medium_risk_exposures'] += 1
            else:
                summary['low_risk_exposures'] += 1
            
            # Count exposed information types
            for info_type in result.get('matched_info', {}).keys():
                if info_type != 'additional_pii':
                    summary['exposed_information'][info_type] += 1
            
            # Count domains
            domain = Utils.get_domain(result.get('url', ''))
            if domain:
                summary['top_domains'][domain] += 1
        
        # Determine overall risk level
        if summary['high_risk_exposures'] >= 3:
            summary['overall_risk_level'] = 'high'
        elif summary['high_risk_exposures'] >= 1 or summary['medium_risk_exposures'] >= 3:
            summary['overall_risk_level'] = 'medium'
        
        # Sort top domains
        summary['top_domains'] = dict(
            sorted(summary['top_domains'].items(), key=lambda x: x[1], reverse=True)[:10]
        )
        
        # Generate recommendations
        if summary['exposed_information'].get('email', 0) > 2:
            summary['recommendations'].append(
                "Your email appears on multiple sites. Consider using different emails for different purposes."
            )
        
        if summary['exposed_information'].get('phone', 0) > 0:
            summary['recommendations'].append(
                "Your phone number is publicly visible. Consider using a secondary number for online services."
            )
        
        if summary['exposed_information'].get('address', 0) > 0:
            summary['recommendations'].append(
                "Your physical address is exposed online. Review privacy settings on platforms where you've shared it."
            )
        
        if summary['overall_risk_level'] == 'high':
            summary['recommendations'].append(
                "HIGH RISK: Your personal information is widely exposed. Take immediate action to review and remove sensitive data."
            )
        
        return summary