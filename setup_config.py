#!/usr/bin/env python3
import json
import os

def setup_openai_config():
    """Interactive setup for OpenAI API key"""
    print("🔧 Privacy Leak Scanner - OpenAI API Configuration")
    print("=" * 50)
    
    # Check if config.json already exists
    if os.path.exists('config.json'):
        print("✅ config.json already exists.")
        choice = input("Do you want to update it? (y/n): ").lower().strip()
        if choice not in ['y', 'yes']:
            print("Setup cancelled.")
            return
    
    print("\nPlease enter your OpenAI API key.")
    print("You can get one from: https://platform.openai.com/api-keys")
    print("Note: This will be stored in config.json file locally.")
    print()
    
    while True:
        api_key = input("OpenAI API Key: ").strip()
        
        if not api_key:
            print("❌ API key cannot be empty. Please try again.")
            continue
            
        if not api_key.startswith('sk-'):
            print("⚠️  Warning: OpenAI API keys usually start with 'sk-'")
            choice = input("Continue anyway? (y/n): ").lower().strip()
            if choice not in ['y', 'yes']:
                continue
        
        # Create config.json
        config = {
            "openai_api_key": api_key,
            "description": "OpenAI API configuration for Privacy Leak Scanner"
        }
        
        try:
            with open('config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            print("\n✅ Configuration saved successfully!")
            print("📄 API key saved to config.json")
            print("\n🚀 You can now run the application with: python app.py")
            
            # Add to .gitignore if it exists
            if os.path.exists('.gitignore'):
                with open('.gitignore', 'r') as f:
                    gitignore_content = f.read()
                
                if 'config.json' not in gitignore_content:
                    with open('.gitignore', 'a') as f:
                        f.write('\n# Configuration files\nconfig.json\n')
                    print("🛡️  Added config.json to .gitignore for security")
            
            break
            
        except Exception as e:
            print(f"❌ Error saving configuration: {e}")
            return

if __name__ == "__main__":
    setup_openai_config() 