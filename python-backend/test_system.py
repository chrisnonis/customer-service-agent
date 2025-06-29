#!/usr/bin/env python3
"""
Test script to verify the complete system functionality after quota reset.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
from main import agent_respond, route_to_agent, create_initial_context

# Load environment variables
load_dotenv()

def test_complete_system():
    """Test the complete agent system with various queries."""
    print("🧪 Testing Complete Agent System")
    print("=" * 60)
    
    # Test queries for each agent
    test_cases = [
        {
            "query": "What's the current Premier League table?",
            "expected_agent": "Premier League Agent",
            "description": "Premier League knowledge test"
        },
        {
            "query": "Tell me about Championship promotion race",
            "expected_agent": "Championship Agent", 
            "description": "Championship routing test"
        },
        {
            "query": "Who is Tyson Fury fighting next?",
            "expected_agent": "Boxing Agent",
            "description": "Boxing knowledge test"
        },
        {
            "query": "What are the latest transfer news?",
            "expected_agent": "Sports News Agent",
            "description": "Sports news test"
        },
        {
            "query": "What are Chelsea's fixtures for 2025/26?",
            "expected_agent": "Premier League Agent",
            "description": "Grounding trigger test (should use web search)"
        }
    ]
    
    context = create_initial_context()
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['description']}")
        print(f"Query: {test_case['query']}")
        print("-" * 50)
        
        try:
            # Test routing
            routed_agent, _ = route_to_agent(test_case['query'], context, "Triage Agent")
            print(f"✅ Routed to: {routed_agent}")
            
            # Test agent response
            response = agent_respond(routed_agent, test_case['query'], context)
            print(f"✅ Response length: {len(response)} characters")
            print(f"Response preview: {response[:150]}...")
            
            # Check if grounding was used (look for HTML links)
            if "<a href=" in response:
                print("🌐 Grounding was used (web results included)")
            else:
                print("🧠 Gemini knowledge was used")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

if __name__ == "__main__":
    print("🚀 Starting Complete System Test")
    print("Make sure your Gemini API quota has reset!")
    print("=" * 60)
    
    test_complete_system()
    
    print("✅ System test completed!")
    print("\nNext steps:")
    print("1. If all tests pass, the system is working correctly")
    print("2. If grounding tests fail, check your Google Custom Search setup")
    print("3. If routing fails, review agent prompts")