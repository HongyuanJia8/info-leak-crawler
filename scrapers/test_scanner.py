"""
Test script for the privacy scanner
"""
import asyncio
import logging
from privacy_scanner import PrivacyScanner

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_scanner():
    """Test the privacy scanner with sample data"""
    
    # Test user information
    test_user_info = {
        'name': 'John Smith',
        'email': 'john.smith@example.com',
        'phone': '555-123-4567',
        'address': 'New York, NY'
    }
    
    # Scan options
    options = {
        'search_engines': ['google', 'bing'],
        'social_platforms': ['github', 'reddit'],
        'pages_per_engine': 2,
        'max_detailed_results': 10
    }
    
    # Create scanner instance
    scanner = PrivacyScanner()
    
    print("Starting privacy scan...")
    print(f"Searching for: {test_user_info}")
    print("-" * 50)
    
    try:
        # Perform scan
        results = await scanner.scan(test_user_info, options)
        
        # Print results
        print(f"\nScan completed in {results['scan_time']:.2f} seconds")
        print(f"Total results found: {results['total_results_found']}")
        print(f"Detailed results analyzed: {len(results['detailed_results'])}")
        
        # Print summary
        summary = results['summary']
        print("\n--- SUMMARY ---")
        print(f"Overall Risk Level: {summary['overall_risk_level'].upper()}")
        print(f"High Risk Exposures: {summary['high_risk_exposures']}")
        print(f"Medium Risk Exposures: {summary['medium_risk_exposures']}")
        print(f"Low Risk Exposures: {summary['low_risk_exposures']}")
        
        print("\nExposed Information Types:")
        for info_type, count in summary['exposed_information'].items():
            print(f"  - {info_type}: {count} exposures")
        
        print("\nTop Domains with Your Information:")
        for domain, count in list(summary['top_domains'].items())[:5]:
            print(f"  - {domain}: {count} results")
        
        print("\nRecommendations:")
        for rec in summary['recommendations']:
            print(f"  • {rec}")
        
        # Print top detailed results
        print("\n--- TOP PRIVACY EXPOSURES ---")
        for i, result in enumerate(results['detailed_results'][:5], 1):
            print(f"\n{i}. {result.get('title', 'No title')}")
            print(f"   URL: {result['url']}")
            print(f"   Source: {result['source']}")
            print(f"   Privacy Score: {result.get('privacy_score', 'N/A')}")
            print(f"   Risk Level: {result.get('risk_assessment', {}).get('risk_level', 'N/A')}")
            
            matched = result.get('matched_info', {})
            if matched:
                print("   Matched Information:")
                for info_type, details in matched.items():
                    if isinstance(details, dict):
                        print(f"     - {info_type}: {details.get('value', 'N/A')} "
                              f"(confidence: {details.get('confidence', 0):.0%})")
            
            risks = result.get('risk_assessment', {}).get('risks', [])
            if risks:
                print("   Risks:")
                for risk in risks[:2]:
                    print(f"     - {risk}")
        
    except Exception as e:
        print(f"Error during scan: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_scanner())