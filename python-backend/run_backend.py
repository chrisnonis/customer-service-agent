#!/usr/bin/env python3
"""
Simple script to run the backend with proper error handling.
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check if environment is properly set up."""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("Please create a .env file with your API keys.")
        print("See .env.example for the required variables.")
        return False
    
    required_vars = ["GOOGLE_API_KEY", "GOOGLE_CUSTOM_SEARCH_API_KEY", "GOOGLE_CUSTOM_SEARCH_ENGINE_ID"]
    missing = []
    
    from dotenv import load_dotenv
    load_dotenv()
    
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        return False
    
    print("✅ Environment variables configured")
    return True

def run_backend():
    """Run the backend server."""
    if not check_environment():
        return
    
    print("🚀 Starting UK Sports Backend...")
    print("Backend will be available at: http://127.0.0.1:8000")
    print("Health check: http://127.0.0.1:8000/health")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        import uvicorn
        from improved_api import app
        
        uvicorn.run(
            app, 
            host="127.0.0.1", 
            port=8000, 
            reload=True,
            log_level="info"
        )
    except ImportError:
        print("❌ uvicorn not installed. Installing...")
        os.system("pip install uvicorn[standard]")
        import uvicorn
        from improved_api import app
        uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
    except KeyboardInterrupt:
        print("\n👋 Backend stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")

if __name__ == "__main__":
    run_backend()