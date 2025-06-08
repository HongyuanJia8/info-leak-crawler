# scrapers/data_extractor.py
import re
from typing import Dict, List, Any, Tuple
from bs4 import BeautifulSoup
import logging
from datetime import datetime

from .utils import Utils

logger = logging.getLogger(__name__)

class DataExtractor:
    """Extract and analyze personal information from web content"""
    
    def __init__(self):
        self.pii_patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone_us': r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',
            'phone_cn': r'\b(?:\+?86[-\s]?)?1[3-9]\d{9}\b',
            'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
            'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
            'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
            'date': r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b',
        }
    
    async def extract_personal_info(self, url: str, html_content: str, user_info: Dict[str, str]) -> Dict[str, Any]:
        """Extract personal information from webpage content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Extract matches
        matches = self._find_matches(text, user_info)
        
        # Calculate privacy score
        privacy_score = self._calculate_privacy_score(matches, url)
        
        # Generate risk assessment
        risk_assessment = self._assess_risk(matches, url)
        
        return {
            'url': url,
            'matched_info': matches,
            'privacy_score': privacy_score,
            'risk_assessment': risk_assessment,
            'extracted_at': datetime.utcnow().isoformat()
        }
    
    def _find_matches(self, text: str, user_info: Dict[str, str]) -> Dict[str, Any]:
        """Find matches of user information in text"""
        matches = {}
        text_lower = text.lower()
        
        # Check name
        if user_info.get('name'):
            name = user_info['name']
            name_lower = name.lower()
            
            # Exact match
            if name_lower in text_lower:
                matches['name'] = {
                    'value': name,
                    'confidence': 1.0,
                    'context': Utils.extract_context(text, name),
                    'match_type': 'exact'
                }
            else:
                # Check for partial matches (first/last name)
                name_parts = name.split()
                partial_matches = []
                for part in name_parts:
                    if len(part) > 2 and part.lower() in text_lower:
                        partial_matches.append(part)
                
                if partial_matches:
                    matches['name'] = {
                        'value': name,
                        'confidence': len(partial_matches) / len(name_parts),
                        'context': Utils.extract_context(text, partial_matches[0]),
                        'match_type': 'partial',
                        'matched_parts': partial_matches
                    }
        
        # Check email
        if user_info.get('email'):
            email = user_info['email'].lower()
            emails_found = Utils.extract_email(text)
            
            for found_email in emails_found:
                if found_email.lower() == email:
                    matches['email'] = {
                        'value': user_info['email'],
                        'confidence': 1.0,
                        'context': Utils.extract_context(text, found_email),
                        'match_type': 'exact'
                    }
                    break
                elif email.split('@')[0] in found_email.lower():
                    matches['email'] = {
                        'value': user_info['email'],
                        'confidence': 0.7,
                        'context': Utils.extract_context(text, found_email),
                        'match_type': 'partial',
                        'found_value': found_email
                    }
        
        # Check phone
        if user_info.get('phone'):
            phone = user_info['phone']
            phones_found = Utils.extract_phone(text)
            
            # Normalize phone number for comparison
            normalized_user_phone = re.sub(r'\D', '', phone)
            
            for found_phone in phones_found:
                normalized_found = re.sub(r'\D', '', found_phone)
                
                if normalized_found == normalized_user_phone:
                    matches['phone'] = {
                        'value': phone,
                        'confidence': 1.0,
                        'context': Utils.extract_context(text, found_phone),
                        'match_type': 'exact'
                    }
                    break
                elif normalized_user_phone in normalized_found or normalized_found in normalized_user_phone:
                    matches['phone'] = {
                        'value': phone,
                        'confidence': 0.8,
                        'context': Utils.extract_context(text, found_phone),
                        'match_type': 'partial',
                        'found_value': found_phone
                    }
        
        # Check address
        if user_info.get('address'):
            address = user_info['address']
            address_lower = address.lower()
            
            # Check for full address
            if address_lower in text_lower:
                matches['address'] = {
                    'value': address,
                    'confidence': 1.0,
                    'context': Utils.extract_context(text, address),
                    'match_type': 'exact'
                }
            else:
                # Check for address components
                address_parts = re.split(r'[,\s]+', address)
                found_parts = []
                
                for part in address_parts:
                    if len(part) > 2 and part.lower() in text_lower:
                        found_parts.append(part)
                
                if len(address_parts) >= 2:  # At least 2 parts found
                    matches['address'] = {
                        'value': address,
                        'confidence': len(found_parts) / len(address_parts),
                        'context': Utils.extract_context(text, found_parts[0]),
                        'match_type': 'partial',
                        'matched_parts': found_parts
                    }
        
        # Check for additional PII that might be exposed
        additional_pii = self._find_additional_pii(text)
        if additional_pii:
            matches['additional_pii'] = additional_pii
        
        return matches
    
    def _find_additional_pii(self, text: str) -> Dict[str, List[str]]:
        """Find additional PII that might be exposed"""
        additional = {}
        
        for pii_type, pattern in self.pii_patterns.items():
            found = re.findall(pattern, text, re.IGNORECASE)
            if found and pii_type not in ['email', 'phone_us', 'phone_cn']:  # Skip already checked
                additional[pii_type] = list(set(found))[:5]  # Limit to 5 examples
        
        return additional if additional else None
    
    def _calculate_privacy_score(self, matches: Dict[str, Any], url: str) -> int:
        """Calculate privacy risk score (0-100, higher is worse)"""
        score = 0
        
        # Base scores for each type of information
        scores = {
            'name': 20,
            'email': 30,
            'phone': 40,
            'address': 35,
            'additional_pii': 25
        }
        
        for info_type, base_score in scores.items():
            if info_type in matches:
                match = matches[info_type]
                confidence = match.get('confidence', 1.0) if isinstance(match, dict) else 1.0
                score += base_score * confidence
        
        # Adjust based on source credibility
        domain = Utils.get_domain(url)
        if any(social in domain for social in ['facebook', 'twitter', 'linkedin', 'instagram']):
            score *= 1.2  # Social media exposure is more serious
        elif any(data in domain for data in ['pastebin', 'github', 'breach']):
            score *= 1.5  # Data dumps are very serious
        
        return min(100, int(score))
    
    def _assess_risk(self, matches: Dict[str, Any], url: str) -> Dict[str, Any]:
        """Assess privacy risk based on matches"""
        risk_level = 'low'
        risks = []
        recommendations = []
        
        # Determine risk level
        matched_types = len([k for k in matches.keys() if k != 'additional_pii'])
        
        if matched_types >= 3:
            risk_level = 'high'
        elif matched_types >= 2:
            risk_level = 'medium'
        elif 'email' in matches or 'phone' in matches:
            risk_level = 'medium'
        
        # Identify specific risks
        if 'email' in matches:
            risks.append("Email address exposed - risk of spam and phishing")
            recommendations.append("Consider using a different email for public profiles")
        
        if 'phone' in matches:
            risks.append("Phone number exposed - risk of unwanted calls and SMS scams")
            recommendations.append("Use a secondary phone number for online services")
        
        if 'address' in matches:
            risks.append("Physical address exposed - risk to personal safety")
            recommendations.append("Avoid sharing full address online; use city/state only")
        
        if 'name' in matches and 'email' in matches:
            risks.append("Name and email combination - high risk of targeted attacks")
            recommendations.append("Review and limit information shared on this platform")
        
        if matches.get('additional_pii'):
            risks.append("Additional sensitive information detected")
            recommendations.append("Review all information visible on this page")
        
        return {
            'risk_level': risk_level,
            'risks': risks,
            'recommendations': recommendations,
            'domain': Utils.get_domain(url)
        }