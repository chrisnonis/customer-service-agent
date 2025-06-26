import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def test_gemini():
    try:
        # Try different model names
        models_to_try = [
            "gemini-1.5-flash",
            "gemini-1.5-pro", 
            "gemini-pro",
            "gemini-2.0-flash-exp"
        ]
        
        for model_name in models_to_try:
            try:
                print(f"Testing model: {model_name}")
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello, this is a test message.")
                print(f"✅ Success with {model_name}!")
                print(f"Response: {response.text}")
                return model_name
            except Exception as e:
                print(f"❌ {model_name} failed: {str(e)[:100]}...")
                continue
        
        print("❌ All models failed")
        return None
        
    except Exception as e:
        print(f"❌ General error: {e}")
        return None

if __name__ == "__main__":
    working_model = test_gemini()
    if working_model:
        print(f"\n🎉 Use this model in your main.py: {working_model}") 