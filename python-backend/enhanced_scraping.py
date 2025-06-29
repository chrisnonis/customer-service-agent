#!/usr/bin/env python3
"""
Enhanced web scraping for sports fixtures and results.
"""

import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import json

def scrape_premier_league_fixtures():
    """
    Scrape Premier League fixtures from official sources.
    """
    try:
        # Try Premier League official site
        url = "https://www.premierleague.com/fixtures"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        fixtures = []
        
        # Look for fixture elements (this is a simplified example)
        fixture_elements = soup.find_all(['div', 'li'], class_=re.compile(r'fixture|match'))
        
        for element in fixture_elements[:10]:  # Limit to 10 fixtures
            text = element.get_text(separator=' ', strip=True)
            
            # Look for patterns like "Team A vs Team B" and dates
            if re.search(r'\w+\s+vs?\s+\w+|\w+\s+v\s+\w+', text, re.IGNORECASE):
                # Extract date if present
                date_match = re.search(r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}|\d{1,2}\s+\w+\s+\d{4}', text)
                date_str = date_match.group() if date_match else "Date TBD"
                
                fixtures.append({
                    'text': text[:100],  # Limit length
                    'date': date_str,
                    'source': 'Premier League Official'
                })
        
        return fixtures
        
    except Exception as e:
        print(f"Error scraping Premier League fixtures: {e}")
        return []

def scrape_chelsea_fixtures():
    """
    Scrape Chelsea fixtures from official site.
    """
    try:
        url = "https://www.chelseafc.com/en/matches/fixtures"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        fixtures = []
        
        # Look for Chelsea-specific fixture patterns
        fixture_elements = soup.find_all(['div', 'article'], class_=re.compile(r'fixture|match|game'))
        
        for element in fixture_elements[:5]:  # Limit to 5 fixtures
            text = element.get_text(separator=' ', strip=True)
            
            if 'chelsea' in text.lower() and len(text) > 20:
                fixtures.append({
                    'text': text[:150],
                    'source': 'Chelsea FC Official'
                })
        
        return fixtures
        
    except Exception as e:
        print(f"Error scraping Chelsea fixtures: {e}")
        return []

def enhanced_fixture_scraping(search_results):
    """
    Enhanced fixture scraping that tries multiple sources.
    """
    all_fixtures = []
    
    # Try official sources first
    if any('premier' in result.get('link', '').lower() for result in search_results):
        pl_fixtures = scrape_premier_league_fixtures()
        all_fixtures.extend(pl_fixtures)
    
    if any('chelsea' in result.get('link', '').lower() for result in search_results):
        chelsea_fixtures = scrape_chelsea_fixtures()
        all_fixtures.extend(chelsea_fixtures)
    
    # Format the results
    if all_fixtures:
        formatted = "<b>📅 Extracted Fixtures:</b><br><br>"
        for i, fixture in enumerate(all_fixtures, 1):
            formatted += f"{i}. {fixture['text']}<br>"
            if 'date' in fixture:
                formatted += f"   📅 {fixture['date']}<br>"
            formatted += f"   🔗 Source: {fixture['source']}<br><br>"
        return formatted
    
    return ""

# Test the scraping
if __name__ == "__main__":
    print("🧪 Testing Enhanced Fixture Scraping")
    print("=" * 50)
    
    # Test Premier League scraping
    print("Testing Premier League fixtures...")
    pl_fixtures = scrape_premier_league_fixtures()
    print(f"Found {len(pl_fixtures)} Premier League fixtures")
    
    # Test Chelsea scraping  
    print("\nTesting Chelsea fixtures...")
    chelsea_fixtures = scrape_chelsea_fixtures()
    print(f"Found {len(chelsea_fixtures)} Chelsea fixtures")
    
    if pl_fixtures or chelsea_fixtures:
        print("\n✅ Scraping is working!")
        print("You can integrate this into your main.py grounding function.")
    else:
        print("\n⚠️  No fixtures found. This might be due to:")
        print("- Website structure changes")
        print("- Rate limiting")
        print("- Network issues")