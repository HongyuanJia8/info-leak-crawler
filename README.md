# Privacy Leak Scanner Web Application

A web-based tool to check if your personal information is exposed online. This application searches for your information on the internet and provides an AI-powered analysis of potential privacy risks.

## Features

- 🔍 Search for personal information (name, email, phone, address) using Bing search engine
- 🤖 AI-powered analysis using ChatGPT 4 API
- 📊 Risk assessment with percentage visualization
- 💡 Personalized privacy protection recommendations
- 🎨 Beautiful, responsive web interface

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (for ChatGPT integration)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/privacy-leak-scanner.git
cd privacy-leak-scanner
```

2. Create and activate a virtual environment:
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up OpenAI API key (choose one method):

**Option 1: Configuration File (Recommended)**
```bash
cp config.example.json config.json
# Then edit config.json and replace the API key
```

**Option 2: Environment Variable**
Create a `.env` file in the root directory:
```
OPENAI_API_KEY=your_openai_api_key_here
```

**Option 3: Direct Code (Local Testing Only)**
Uncomment line 32 in `app.py` and add your key directly
⚠️ **Warning**: Never commit API keys to version control!

## Running the Application

1. Start the Flask server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Enter your personal information and click "Start Scan"

## How It Works

1. **Information Input**: Users enter their personal information (name, email, phone, address)
2. **Web Search**: The application searches Bing for the provided information
3. **Data Analysis**: Results are analyzed to identify potential privacy exposures
4. **AI Assessment**: ChatGPT provides a comprehensive analysis and risk percentage
5. **Recommendations**: The system provides personalized recommendations to improve privacy

## Project Structure

```
privacy-leak-scanner/
├── app.py                  # Flask application main file
├── requirements.txt        # Python dependencies
├── .env                   # Environment variables (create this)
├── templates/
│   └── index.html         # Web interface template
├── static/
│   ├── css/
│   │   └── style.css      # Styling
│   └── js/
│       └── script.js      # Frontend JavaScript
└── scrapers/
    ├── __init__.py
    ├── base.py            # Base scraper class
    ├── config.py          # Configuration settings
    ├── search_engines.py  # Bing search implementation
    ├── social_media.py    # Social media placeholder
    ├── privacy_scanner.py # Main scanner logic
    ├── data_extractor.py  # Data extraction utilities
    └── utils.py           # Utility functions
```

## Configuration

You can modify search behavior in `app.py`:

```python
options = {
    'search_engines': ['bing'],  # Currently only Bing is supported
    'social_platforms': [],      # Social platforms disabled
    'pages_per_engine': 3,       # Number of pages to search
    'max_detailed_results': 10   # Maximum detailed results to analyze
}
```

## Important Notes

- **Ethical Use**: Only search for your own information or with explicit permission
- **Rate Limiting**: The application includes delays to avoid being blocked by search engines
- **Privacy**: Your search queries are not stored; results are only saved locally
- **API Costs**: Using the OpenAI API incurs costs based on usage

## Troubleshooting

1. **No results found**: 
   - Ensure you're connected to the internet
   - Try different variations of your information
   - Check if Bing is accessible from your location

2. **ChatGPT analysis fails**:
   - Verify your OpenAI API key is correct
   - Check your OpenAI account has credits
   - The app will show a fallback analysis if ChatGPT is unavailable

3. **Port already in use**:
   - Change the port in `app.py`: `app.run(debug=True, port=5001)`

## License

This project is for educational purposes. Use responsibly and respect privacy laws in your jurisdiction.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.