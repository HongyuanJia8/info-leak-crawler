
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

