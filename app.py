from flask import Flask, render_template, request, jsonify
import asyncio
import os
from datetime import datetime
import json
import uuid
from flask_cors import CORS
from scrapers import PrivacyScanner
from openai import OpenAI

app = Flask(__name__)
CORS(app)

def get_openai_client():
    """Get OpenAI client with multiple configuration options"""
    api_key = None
    
    # 1. Try to read from config.json file
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                api_key = config.get('openai_api_key')
                if api_key:
                    print("✅ Using OpenAI API key from config.json")
    except Exception as e:
        print(f"Failed to read config.json: {e}")
    
    # 2. Try environment variable if config file doesn't have it
    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            print("✅ Using OpenAI API key from environment variable")
    
    # 3. Try direct configuration (you can uncomment and add your key here)
    # SECURITY WARNING: Only use this for local testing, never commit to git!
    if not api_key:
        # api_key = "your-api-key-here"  # Uncomment and add your key for local use
        pass
    
    if api_key:
        try:
            return OpenAI(api_key=api_key)
        except Exception as e:
            print(f"Failed to initialize OpenAI client: {e}")
            return None
    else:
        print("⚠️  No OpenAI API key found. ChatGPT analysis will be disabled.")
        return None

openai_client = get_openai_client()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan():
    try:
        data = request.json
        user_info = {
            'name': data.get('name', ''),
            'email': data.get('email', ''),
            'phone': data.get('phone', ''),
            'location': data.get('location', ''),
            'social_media': data.get('social_media', '')
        }
        
        user_info = {k: v for k, v in user_info.items() if v.strip()}
        
        if not user_info:
            return jsonify({'error': 'Please provide at least one piece of information to scan'}), 400
        
        scanner = PrivacyScanner()
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(scanner.scan(user_info))
        finally:
            loop.close()
        
        leak_percentage = calculate_leak_percentage(results, user_info)
        
        chatgpt_analysis = ""
        if openai_client:
            try:
                analysis_prompt = f"""
                Analyze these privacy leak scan results and provide a brief assessment:
                
                User Information Searched: {', '.join(user_info.keys())}
                Results Found: {len(results.get('detailed_results', []))} items
                Leak Percentage: {leak_percentage}%
                
                Provide a 3-4 sentence analysis in English about the privacy exposure level and recommendations.
                """
                
                response = openai_client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a privacy security expert providing brief analysis of personal information exposure online."},
                        {"role": "user", "content": analysis_prompt}
                    ],
                    max_tokens=150,
                    temperature=0.7
                )
                
                chatgpt_analysis = response.choices[0].message.content.strip()
                
            except Exception as e:
                print(f"ChatGPT API error: {e}")
                chatgpt_analysis = get_fallback_analysis(leak_percentage)
        else:
            chatgpt_analysis = get_fallback_analysis(leak_percentage)
        
        scan_id = str(uuid.uuid4())[:8]
        
        result_data = {
            'scan_id': scan_id,
            'leak_percentage': leak_percentage,
            'risk_level': get_risk_level(leak_percentage),
            'summary': results.get('summary', 'Scan completed'),
            'detailed_results': results.get('detailed_results', []),
            'chatgpt_analysis': chatgpt_analysis,
            'recommendations': get_privacy_recommendations(leak_percentage)
        }
        
        with open(f'scan_results_{scan_id}.json', 'w') as f:
            json.dump(result_data, f, indent=2)
        
        return jsonify(result_data)
    
    except Exception as e:
        return jsonify({'error': f'Scan failed: {str(e)}'}), 500

def calculate_leak_percentage(results, user_info):
    if not results.get('detailed_results'):
        return 15
    
    base_percentage = min(len(results['detailed_results']) * 12, 85)
    
    info_multiplier = len(user_info) * 5
    base_percentage += info_multiplier
    
    return min(base_percentage, 95)

def get_risk_level(percentage):
    if percentage >= 70:
        return 'high'
    elif percentage >= 40:
        return 'medium'
    else:
        return 'low'

def get_fallback_analysis(leak_percentage):
    if leak_percentage >= 70:
        return "High privacy exposure detected. Your personal information is widely available online across multiple platforms. Consider immediate action to remove or limit accessible data and review your privacy settings."
    elif leak_percentage >= 40:
        return "Moderate privacy exposure found. Some of your personal information is discoverable online. Review your social media privacy settings and consider limiting publicly available information."
    else:
        return "Low privacy exposure detected. Your online privacy footprint appears minimal. Continue maintaining good privacy practices and regularly monitor your online presence."

def get_privacy_recommendations(leak_percentage):
    base_recommendations = [
        "Review and update privacy settings on all social media accounts",
        "Use strong, unique passwords for all online accounts",
        "Enable two-factor authentication where available",
        "Regularly monitor your online presence"
    ]
    
    if leak_percentage >= 70:
        base_recommendations.extend([
            "Contact websites to request removal of personal information",
            "Consider using privacy-focused search engines",
            "Limit sharing personal information on public platforms"
        ])
    elif leak_percentage >= 40:
        base_recommendations.extend([
            "Audit your social media profiles for excessive personal information",
            "Be cautious about sharing location and contact details online"
        ])
    
    return base_recommendations

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 