import asyncio
import json
from scrapers.privacy_scanner import PrivacyScanner
from scrapers.config import Config

async def test_social_media():
    """Test script specifically for social media scraping"""
    scanner = PrivacyScanner()
    
    # Test data - use a well-known person for testing
    test_info = {
        'name': 'Elon Musk',
        'email': ''  # Leave empty for test
    }
    
    # Only test social media platforms
    options = {
        'search_engines': [],  # No search engines
        'social_platforms': ['twitter', 'linkedin', 'github', 'reddit'],
        'pages_per_engine': 1,
        'max_detailed_results': 5
    }
    
    print("Testing social media scraping...")
    print(f"Looking for: {test_info['name']}")
    print(f"Platforms: {', '.join(options['social_platforms'])}")
    print("-" * 50)
    
    try:
        results = await scanner.scan(test_info, options)
        
        print(f"\nTotal results found: {results['total_results_found']}")
        
        # Group results by source
        by_source = {}
        for result in results['detailed_results']:
            source = result.get('source', 'unknown')
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(result)
        
        # Display results by platform
        for platform, platform_results in by_source.items():
            print(f"\n=== {platform.upper()} ({len(platform_results)} results) ===")
            for i, result in enumerate(platform_results[:3], 1):
                print(f"{i}. {result.get('title', 'No title')}")
                print(f"   URL: {result.get('url', 'No URL')}")
                print(f"   Type: {result.get('type', 'unknown')}")
                if result.get('snippet'):
                    snippet = result['snippet'][:100] + "..." if len(result['snippet']) > 100 else result['snippet']
                    print(f"   Preview: {snippet}")
    
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_social_media())