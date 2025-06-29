#!/usr/bin/env python3
"""
Comprehensive environment and API keys checker.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
import requests

# Load environment variables
load_dotenv()

def check_environment():
    """Check all required environment variables and API connectivity."""
    print("🔍 Environment Variables Check")
    print("=" * 50)
    
    # Required environment variables
    required_vars = {
        "GOOGLE_API_KEY": "Google Gemini API Key",
        "GOOGLE_CUSTOM_SEARCH_API_KEY": "Google Custom Search API Key", 
        "GOOGLE_CUSTOM_SEARCH_ENGINE_ID": "Google Custom Search Engine ID"
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 20}...{value[-4:] if len(value) > 4 else '****'}")
        else:
            print(f"❌ {var}: Missing")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please add them to your .env file in the python-backend folder")
        return False
    
    print("\n🧪 API Connectivity Tests")
    print("=" * 50)
    
    # Test Gemini API
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content("Hello, this is a test.")
        print("✅ Gemini API: Working")
        print(f"   Sample response: {response.text[:50]}...")
    except Exception as e:
        print(f"❌ Gemini API: Failed - {str(e)[:100]}...")
        if "429" in str(e):
            print("   This is likely a quota limit. Wait or upgrade your plan.")
        return False
    
    # Test Google Custom Search API
    try:
        api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
        engine_id = os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': api_key,
            'cx': engine_id,
            'q': 'test search',
            'num': 1
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        if 'items' in data:
            print("✅ Google Custom Search API: Working")
            print(f"   Found {len(data['items'])} results")
        else:
            print("⚠️  Google Custom Search API: Connected but no results")
            
    except Exception as e:
        print(f"❌ Google Custom Search API: Failed - {str(e)[:100]}...")
        return False
    
    print("\n🎉 All environment checks passed!")
    return True

if __name__ == "__main__":
    print("🚀 Starting Environment Check")
    print("=" * 60)
    
    if check_environment():
        print("\n✅ Your system is ready for development!")
        print("You can now run the backend and frontend.")
    else:
        print("\n❌ Please fix the issues above before continuing.")