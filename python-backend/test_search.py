#!/usr/bin/env python3
"""
Test script to verify Google Custom Search and grounding functionality.
"""

from main import google_custom_search, sports_grounding_tool, check_if_grounding_needed

def test_google_custom_search():
    """Test the Google Custom Search function."""
    print("🧪 Testing Google Custom Search")
    print("=" * 50)
    
    test_queries = [
        "Premier League table 2025",
        "Arsenal transfers 2025",
        "Manchester City fixtures 2025/26",
        "Liverpool new manager 2025"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 30)
        results = google_custom_search(query, num_results=3)
        
        if results and 'error' not in results[0]:
            print(f"✅ Found {len(results)} results")
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['title']}")
                print(f"   URL: {result['link']}")
                print(f"   Snippet: {result['snippet'][:100]}...")
        else:
            print(f"❌ Error: {results[0].get('error', 'Unknown error')}")
        print()

def test_grounding_tool():
    """Test the sports grounding tool."""
    print("🧪 Testing Sports Grounding Tool")
    print("=" * 50)
    
    test_queries = [
        "Premier League fixtures 2025/26",
        "Latest Arsenal transfers",
        "Manchester City new signings 2025"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 30)
        result = sports_grounding_tool(query)
        print(f"Result: {result[:200]}...")
        print()

def test_grounding_detection():
    """Test the grounding detection logic."""
    print("🧪 Testing Grounding Detection")
    print("=" * 50)
    
    test_cases = [
        {
            "query": "Premier League fixtures 2025/26",
            "response": "I don't have information about the 2025/26 Premier League fixtures yet."
        },
        {
            "query": "What's the current Premier League table?",
            "response": "The current Premier League table shows Arsenal in 1st place with 86 points."
        },
        {
            "query": "Latest transfer news",
            "response": "I don't have access to the most recent transfer information."
        }
    ]
    
    for case in test_cases:
        needs_grounding = check_if_grounding_needed(case["query"], case["response"])
        print(f"Query: {case['query']}")
        print(f"Response: {case['response'][:50]}...")
        print(f"Needs grounding: {'✅ Yes' if needs_grounding else '❌ No'}")
        print()

if __name__ == "__main__":
    print("🚀 Starting Google Custom Search and Grounding Tests")
    print("=" * 60)
    
    # Test Google Custom Search
    test_google_custom_search()
    
    # Test Grounding Tool
    test_grounding_tool()
    
    # Test Grounding Detection
    test_grounding_detection()
    
    print("✅ All tests completed!") 