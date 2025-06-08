# Privacy Exposure Assessment Tool - Social Media Crawler

A comprehensive Python-based social media crawler system designed to help users detect potential exposure of their personal information across social media platforms. This tool searches various social media platforms to identify possible privacy leaks.

## 🚨 **Important Disclaimer**

This tool is designed for **educational purposes and legitimate privacy assessment only**. Users must:
- Only search for their own personal information
- Respect robots.txt and terms of service of websites
- Comply with all applicable laws and regulations
- Use responsibly and ethically

## ✨ Features

### Core Functionality
- **Social Media Crawling**: Twitter, LinkedIn, GitHub, Facebook, and Instagram integration
- **Intelligent Data Extraction**: Advanced pattern matching for emails, phones, addresses
- **Proxy Management**: Built-in proxy rotation and health checking
- **Async Processing**: High-performance concurrent crawling
- **Smart Rate Limiting**: Respects website limitations and prevents blocking

### Advanced Capabilities
- **Query Strategy Generation**: Intelligent query combinations for comprehensive searching
- **Context-Aware Extraction**: Preserves surrounding text for better analysis
- **Confidence Scoring**: Machine learning-based relevance assessment
- **Duplicate Detection**: Advanced deduplication algorithms
- **Comprehensive Reporting**: Detailed analysis and recommendations

## 📁 Project Structure

```
info-leak-crawler/
├── scrapers/
│   ├── __init__.py              # Package initialization
│   ├── base.py                  # Base crawler class
│   ├── config.py                # Configuration management
│   ├── utils.py                 # Utility functions
│   ├── proxy_manager.py         # Proxy rotation and management
│   ├── data_extractor.py        # Data extraction and analysis
│   └── social_media.py          # Social media platform crawlers
├── tests/
│   ├── __init__.py              # Tests package
│   └── test_crawlers.py         # Comprehensive test suite
├── requirements.txt             # Python dependencies
├── simple_privacy_search.py     # Simple privacy search tool
├── example_usage.py             # Usage examples
└── README.md                    # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- Chrome browser (for Selenium-based crawling)
- ChromeDriver (for automated browser crawling)

### Step 1: Clone the Repository
```bash
git clone https://github.com/your-username/info-leak-crawler.git
cd info-leak-crawler
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Install ChromeDriver
For automated browser crawling:
```bash
# On macOS
brew install chromedriver

# On Ubuntu
sudo apt-get install chromium-chromedriver

# On Windows
# Download from https://chromedriver.chromium.org/
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file in the project root:

```bash
# Environment
CRAWLER_ENV=development

# API Keys (Optional)
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
GITHUB_TOKEN=your_github_token

# Proxy Settings (Optional)
PROXY_HTTP=http://proxy-server:port
PROXY_HTTPS=https://proxy-server:port
```

### Basic Configuration
The tool uses a hierarchical configuration system:

```python
from scrapers.config import get_config

# Development config (default)
config = get_config('development')

# Production config
config = get_config('production') 

# Testing config
config = get_config('testing')
```

## 🚀 Quick Start

### Simple Privacy Search Tool

The easiest way to use this tool is with the simple privacy search script:

```bash
python simple_privacy_search.py
```

This will prompt you for:
- Full Name
- Email Address  
- Phone Number

The tool will then analyze potential privacy exposure across social media platforms.

### Basic Usage Example

```python
import asyncio
from scrapers.config import get_config
from scrapers.social_media import SocialMediaManager
from scrapers.data_extractor import DataExtractor
from scrapers.utils import validate_personal_info

async def basic_search():
    # Your personal information to search for
    personal_info = {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'phone': '555-123-4567'
    }
    
    # Validate the information
    errors = validate_personal_info(personal_info)
    if errors:
        print("Validation errors:", errors)
        return
    
    # Initialize components
    config = get_config()
    social_manager = SocialMediaManager(config)
    data_extractor = DataExtractor(config.__dict__)
    
    # Perform search across social media platforms
    results = await social_manager.search_all_platforms(
        query=f'"{personal_info["name"]}" "{personal_info["email"]}"',
        max_results=20
    )
    
    print(f"Found results from {len(results)} platforms")
    for platform, platform_results in results.items():
        print(f"{platform}: {len(platform_results)} results")
    
    # Cleanup
    await social_manager.cleanup()

# Run the search
asyncio.run(basic_search())
```

### Running the Example Script

```bash
python example_usage.py
```

## 📖 Detailed Usage

### 1. Social Media Crawling

```python
from scrapers.social_media import GitHubCrawler, TwitterCrawler, LinkedInCrawler

# Individual social media platform usage
async with GitHubCrawler() as crawler:
    results = await crawler.search('john.doe@example.com', search_type='users')
    
    for result in results:
        print(f"Username: {result['username']}")
        print(f"URL: {result['url']}")
        print(f"Bio: {result.get('bio', 'N/A')}")

# Twitter search
async with TwitterCrawler() as crawler:
    tweets = await crawler.search('"John Doe" contact', max_results=10)
    
    for tweet in tweets:
        print(f"User: {tweet['username']}")
        print(f"Text: {tweet['text']}")
```

### 2. Comprehensive Social Media Search

```python
from scrapers.social_media import SocialMediaManager

async with SocialMediaManager() as manager:
    # Search all platforms simultaneously
    all_results = await manager.search_all_platforms(
        query='John Doe privacy',
        platforms=['twitter', 'linkedin', 'github', 'facebook', 'instagram'],
        max_results=15
    )
    
    # Process results from each platform
    for platform, results in all_results.items():
        print(f"\n{platform.upper()} Results:")
        for result in results:
            print(f"- {result.get('text', result.get('name', 'N/A'))}")
```

### 3. Data Extraction and Analysis

```python
from scrapers.data_extractor import DataExtractor

# Initialize data extractor
config = get_config()
extractor = DataExtractor(config.__dict__)

# Extract personal information from HTML content
target_info = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'phone': '555-123-4567'
}

extracted_data = extractor.extract_from_html(
    html_content,
    source_url='https://example.com/profile',
    target_info=target_info
)

# Analyze extracted information
for item in extracted_data:
    print(f"Type: {item.type}")
    print(f"Value: {item.value}")
    print(f"Confidence: {item.confidence:.2f}")
    print(f"Context: {item.full_context[:100]}...")
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_crawlers.py

# Run with coverage
pytest tests/ --cov=scrapers
```

### Test Categories

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Component interaction testing
3. **Mock Tests**: External service simulation
4. **Error Handling Tests**: Edge case and error scenarios

## 🔧 Advanced Configuration

### Custom Search Strategies

```python
# Custom query generation
from scrapers.utils import generate_query_combinations

personal_info = {
    'name': 'John Doe',
    'email': 'john.doe@company.com',
    'phone': '+1-555-123-4567',
    'address': '123 Main St, Anytown, USA'
}

queries = generate_query_combinations(personal_info)

# Add custom queries
custom_queries = [
    f'"John Doe" site:linkedin.com',
    f'"john.doe@company.com" filetype:pdf',
    f'"555-123-4567" site:whitepages.com'
]

all_queries = queries + custom_queries
```

### Rate Limiting and Anti-Detection

```python
# Configure rate limiting
config.REQUEST_DELAY_MIN = 2  # Minimum delay between requests
config.REQUEST_DELAY_MAX = 5  # Maximum delay between requests
config.MAX_CONCURRENT_REQUESTS = 5  # Concurrent request limit

# Configure user agents
config.USER_AGENTS = [
    'Custom User Agent 1.0',
    'Custom User Agent 2.0'
]
```

### Error Handling and Logging

```python
import logging
from scrapers.utils import setup_logging

# Configure logging
logging_config = {
    'level': logging.INFO,
    'file': 'crawler.log',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
}

logger = setup_logging(logging_config)
```

## 📊 Output and Reporting

### Generated Reports

The tool generates comprehensive JSON reports containing:

```json
{
  "personal_info": {
    "name": "John Doe",
    "email": "john.doe@example.com",
    "phone": "555-123-4567"
  },
  "search_summary": {
    "queries_generated": 15,
    "search_engines_used": ["google", "bing"],
    "total_results": 127,
    "pages_analyzed": 50
  },
  "findings": {
    "total_matches": 8,
    "high_confidence_matches": 3,
    "matches_by_type": {
      "email": 3,
      "phone": 2,
      "address": 1
    }
  },
  "detailed_results": [
    {
      "type": "email",
      "value": "john.doe@example.com",
      "source_url": "https://example.com/directory",
      "confidence": 0.95,
      "context": "Contact information for John Doe: john.doe@example.com"
    }
  ],
  "recommendations": [
    "High-confidence matches found. Consider contacting site owners for removal.",
    "Review privacy settings on social media platforms."
  ]
}
```

## 🛡️ Privacy and Security

### Data Protection
- **No Data Storage**: Personal information is not stored persistently
- **Secure Processing**: All processing is done in memory
- **Configurable Logging**: Control what information is logged
- **Proxy Support**: Route traffic through proxies for anonymity

### Compliance Features
- **Robots.txt Respect**: Automatically checks and respects robots.txt
- **Rate Limiting**: Prevents overwhelming target servers
- **User-Agent Rotation**: Reduces detection risk
- **Timeout Handling**: Prevents hanging requests

## 🚨 Limitations and Considerations

### Technical Limitations
1. **Dynamic Content**: Limited ability to crawl JavaScript-heavy sites
2. **Authentication**: Cannot access login-protected content
3. **Rate Limits**: Subject to search engine rate limiting
4. **Geographic Restrictions**: Some content may be geo-blocked

### Ethical Considerations
1. **Personal Use Only**: Should only be used for your own information
2. **Legal Compliance**: Must comply with local laws and regulations
3. **Website Terms**: Respect terms of service of crawled websites
4. **False Positives**: Results may include unrelated information

### Detection and Blocking
1. **Anti-Bot Measures**: Modern websites employ sophisticated detection
2. **IP Blocking**: Excessive requests may result in IP bans
3. **CAPTCHA Challenges**: May encounter CAPTCHAs requiring manual intervention
4. **Behavioral Analysis**: Advanced sites monitor crawling patterns

## 🤝 Contributing

### Development Setup

```bash
# Clone the repository
git clone https://github.com/your-username/info-leak-crawler.git
cd info-leak-crawler

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write comprehensive docstrings
- Add unit tests for new features

### Submitting Changes
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Legal Notice

This tool is provided for educational and legitimate privacy assessment purposes only. Users are responsible for:

- Ensuring compliance with all applicable laws
- Respecting website terms of service
- Using the tool ethically and responsibly
- Only searching for their own personal information

The developers are not responsible for any misuse of this tool.

## 📞 Support

### Getting Help
- Check the [Issues](https://github.com/your-username/info-leak-crawler/issues) page
- Review the [Wiki](https://github.com/your-username/info-leak-crawler/wiki)
- Read the [FAQ](https://github.com/your-username/info-leak-crawler/wiki/FAQ)

### Reporting Bugs
1. Check existing issues first
2. Provide detailed reproduction steps
3. Include system information
4. Attach relevant log files

### Feature Requests
1. Describe the use case
2. Explain the expected behavior
3. Consider implementation complexity
4. Discuss potential alternatives

---

**Remember**: Use this tool responsibly and only for legitimate privacy assessment purposes. Respect the privacy and terms of service of all websites you interact with.