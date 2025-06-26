#!/usr/bin/env python3
"""
Test script to verify Gemini functionality for sports information (no grounding).
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def test_gemini():
    """Test Gemini for sports queries (no grounding)."""
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    test_queries = [
        "What's the current Premier League table?",
        "Who won the last boxing match between Fury and Usyk?",
        "What are the latest transfer news in football?",
        "What's the current Championship promotion race?",
        "When is the next major boxing fight scheduled?"
    ]
    print("\n🧪 Testing Gemini for Sports Information (no grounding)")
    print("=" * 60)
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 40)
        try:
            chat = model.start_chat()
            response = chat.send_message(query)
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"❌ Error: {e}")
        print()

if __name__ == "__main__":
    print("Starting Gemini tests...")
    test_gemini()
    print("\n✅ Gemini tests completed!") 