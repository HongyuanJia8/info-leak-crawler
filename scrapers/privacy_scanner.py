import asyncio
import logging
import re
import aiohttp
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
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.search_aggregator = SearchEngineAggregator(config)
        self.social_aggregator = SocialMediaAggregator(config)
        self.data_extractor = DataExtractor()
        self.results_cache = {}
        
    async def scan(self, user_info: Dict[str, str], options: Dict[str, Any] = None) -> Dict[str, Any]:
        options = options or {}
        start_time = datetime.utcnow()
        
        queries = Utils.generate_search_queries(user_info)
        logger.info(f"Generated {len(queries)} search queries")
        
        all_results = []
        
        search_engines = options.get('search_engines', ['google', 'bing'])
        for query in queries:
            logger.info(f"Searching for: {query}")
            
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
        
        social_platforms = options.get('social_platforms', ['github', 'reddit'])
        if social_platforms:
            for query in queries[:2]:
                social_results = await self.social_aggregator.search_all(
                    query,
                    platforms=social_platforms
                )
                all_results.extend(social_results)
        
        unique_results = self._deduplicate_results(all_results)
        logger.info(f"Found {len(unique_results)} unique results")
        
        detailed_results = []
        max_detailed = options.get('max_detailed_results', 20)
        
        for i, result in enumerate(unique_results[:max_detailed]):
            try:
                html = await self._fetch_with_retry(result['url'])
                if html:
                    extracted = await self.data_extractor.extract_personal_info(
                        result['url'],
                        html,
                        user_info
                    )
                    
                    detailed_result = {**result, **extracted}
                    detailed_results.append(detailed_result)
                else:
                    snippet_analysis = self._analyze_snippet(result, user_info)
                    detailed_result = {**result, **snippet_analysis}
                    detailed_results.append(detailed_result)
                    
            except Exception as e:
                logger.error(f"Error processing {result['url']}: {str(e)}")
        
        detailed_results.sort(key=lambda x: x.get('privacy_score', 0), reverse=True)
        
        summary = self._generate_summary(detailed_results, user_info)
        
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
        seen_urls = set()
        unique_results = []
        
        for result in results:
            url = Utils.clean_url(result.get('url', ''))
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_results.append(result)
        
        return unique_results
    
    def _analyze_snippet(self, result: Dict[str, Any], user_info: Dict[str, str]) -> Dict[str, Any]:
        snippet = result.get('snippet', '')
        title = result.get('title', '')
        combined_text = f"{title} {snippet}".lower()
        
        matched_info = {}
        privacy_score = 0
        
        if user_info.get('name') and user_info['name'].lower() in combined_text:
            matched_info['name'] = {
                'value': user_info['name'],
                'confidence': 0.8,
                'context': snippet,
                'match_type': 'snippet'
            }
            privacy_score += 15
        
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
        
        if user_info.get('phone'):
            phones = Utils.extract_phone(combined_text)
            user_phone = re.sub(r'\D', '', user_info['phone'])
            for phone in phones:
                clean_phone = re.sub(r'\D', '', phone)
                if user_phone == clean_phone:
                    matched_info['phone'] = {
                        'value': user_info['phone'],
                        'confidence': 0.85,
                        'context': snippet,
                        'match_type': 'snippet'
                    }
                    privacy_score += 30
                    break
        
        return {
            'matched_info': matched_info,
            'privacy_score': min(privacy_score, 70),
            'risk_assessment': {
                'risk_level': 'low' if privacy_score < 20 else 'medium' if privacy_score < 40 else 'high',
                'risks': [f"Information found in search snippet: {list(matched_info.keys())}"] if matched_info else []
            }
        }
    
    def _generate_summary(self, results: List[Dict[str, Any]], user_info: Dict[str, str]) -> Dict[str, Any]:
        total_results = len(results)
        risk_counts = defaultdict(int)
        exposed_info = defaultdict(int)
        domains = defaultdict(int)
        
        for result in results:
            risk_level = result.get('risk_assessment', {}).get('risk_level', 'unknown')
            risk_counts[risk_level] += 1
            
            matched_info = result.get('matched_info', {})
            for info_type in matched_info.keys():
                if info_type != 'additional_pii':
                    exposed_info[info_type] += 1
            
            url = result.get('url', '')
            if url:
                domain = Utils.get_domain(url)
                domains[domain] += 1
        
        overall_risk = 'low'
        if risk_counts.get('high', 0) > 0:
            overall_risk = 'high'
        elif risk_counts.get('medium', 0) > 2:
            overall_risk = 'medium'
        
        top_domains = dict(sorted(domains.items(), key=lambda x: x[1], reverse=True))
        
        recommendations = []
        if exposed_info.get('email', 0) > 2:
            recommendations.append("Consider using different email addresses for different services")
        if exposed_info.get('phone', 0) > 1:
            recommendations.append("Consider removing phone number from public profiles")
        if risk_counts.get('high', 0) > 0:
            recommendations.append("Review and remove personal information from high-risk sites")
        if not recommendations:
            recommendations.append("Your digital footprint appears relatively secure")
        
        return {
            'overall_risk_level': overall_risk,
            'total_exposures': total_results,
            'high_risk_exposures': risk_counts.get('high', 0),
            'medium_risk_exposures': risk_counts.get('medium', 0),
            'low_risk_exposures': risk_counts.get('low', 0),
            'exposed_information': dict(exposed_info),
            'top_domains': top_domains,
            'recommendations': recommendations
        }
