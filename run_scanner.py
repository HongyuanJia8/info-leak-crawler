import asyncio
import json
from scrapers.privacy_scanner import PrivacyScanner
from scrapers.config import Config

async def main():
    # Create scanner instance
    scanner = PrivacyScanner()
    
    # Get user input
    print("=== Privacy Exposure Assessment Tool ===")
    print("Enter personal information to check:")
    
    user_info = {
        'name': input("Full Name: ").strip() or None,
        'email': input("Email Address: ").strip() or None,
        'phone': input("Phone Number: ").strip() or None,
        'address': input("Address: ").strip() or None
    }
    
    # Remove empty values
    user_info = {k: v for k, v in user_info.items() if v}
    
    if not user_info:
        print("Error: Please enter at least one piece of information")
        return
    
    # Scan options - INCLUDING social media platforms
    options = {
        'search_engines': ['google', 'bing'],  # Can add 'baidu', 'duckduckgo'
        'social_platforms': ['twitter', 'linkedin', 'github', 'reddit'],  # Added twitter and linkedin
        'pages_per_engine': 2,  # Pages to crawl per search engine
        'max_detailed_results': 10  # Number of results to analyze in detail
    }
    
    print(f"\nStarting scan...")
    print(f"Search engines: {', '.join(options['search_engines'])}")
    print(f"Social platforms: {', '.join(options['social_platforms'])}")
    print("-" * 50)
    
    try:
        # Execute scan
        results = await scanner.scan(user_info, options)
        
        # Display summary
        summary = results['summary']
        print(f"\nScan completed! Time taken: {results['scan_time']:.2f} seconds")
        print(f"Total results found: {results['total_results_found']}")
        print(f"Results analyzed in detail: {len(results['detailed_results'])}")
        
        print(f"\n=== RISK ASSESSMENT ===")
        print(f"Overall Risk Level: {summary['overall_risk_level'].upper()}")
        print(f"High Risk Exposures: {summary['high_risk_exposures']}")
        print(f"Medium Risk Exposures: {summary['medium_risk_exposures']}")
        print(f"Low Risk Exposures: {summary['low_risk_exposures']}")
        
        if summary['exposed_information']:
            print(f"\n=== EXPOSED INFORMATION TYPES ===")
            for info_type, count in summary['exposed_information'].items():
                print(f"- {info_type}: Found in {count} places")
        
        if summary['top_domains']:
            print(f"\n=== TOP DOMAINS WITH YOUR INFORMATION ===")
            for domain, count in list(summary['top_domains'].items())[:5]:
                print(f"- {domain}: {count} occurrences")
        
        print(f"\n=== TOP 5 HIGH-RISK EXPOSURES ===")
        for i, result in enumerate(results['detailed_results'][:5], 1):
            print(f"\n{i}. {result.get('title', 'No title')}")
            print(f"   URL: {result['url']}")
            print(f"   Source: {result['source']}")
            print(f"   Privacy Score: {result.get('privacy_score', 0)}/100 (higher = more risk)")
            
            matched = result.get('matched_info', {})
            if matched:
                print("   Matched Information:")
                for info_type, details in matched.items():
                    if isinstance(details, dict) and info_type != 'additional_pii':
                        confidence = details.get('confidence', 0)
                        print(f"     - {info_type}: {details.get('value', 'N/A')} (confidence: {confidence:.0%})")
        
        if summary['recommendations']:
            print(f"\n=== PRIVACY PROTECTION RECOMMENDATIONS ===")
            for rec in summary['recommendations']:
                print(f"• {rec}")
        
        # Save complete results to file
        filename = f"scan_results_{results['scan_id'][:8]}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\nComplete results saved to: {filename}")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run async main function
    asyncio.run(main())