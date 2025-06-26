import random
import string
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests
import json
import re
from bs4 import BeautifulSoup

# Load environment variables from .env file
load_dotenv()

# =========================
# DEBUG: Print .env file existence and contents
# =========================
print("[DEBUG] .env file exists:", os.path.exists('.env'))
try:
    with open('.env', 'r') as f:
        print("[DEBUG] .env file contents:")
        print(f.read())
except Exception as e:
    print(f"[DEBUG] Could not read .env file: {e}")

# =========================
# DEBUG: Print loaded environment variables
# =========================
GOOGLE_CUSTOM_SEARCH_API_KEY = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
GOOGLE_CUSTOM_SEARCH_ENGINE_ID = os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

print("[DEBUG] GOOGLE_CUSTOM_SEARCH_API_KEY:", GOOGLE_CUSTOM_SEARCH_API_KEY)
print("[DEBUG] GOOGLE_CUSTOM_SEARCH_ENGINE_ID:", GOOGLE_CUSTOM_SEARCH_ENGINE_ID)
print("[DEBUG] GOOGLE_API_KEY:", GOOGLE_API_KEY)

# =========================
# GOOGLE CUSTOM SEARCH SETUP
# =========================

def google_custom_search(query: str, num_results: int = 5) -> list:
    """
    Perform a Google Custom Search and return results.
    
    Args:
        query (str): The search query
        num_results (int): Number of results to return (max 10)
    
    Returns:
        list: List of search result dictionaries
    """
    if not GOOGLE_CUSTOM_SEARCH_API_KEY or not GOOGLE_CUSTOM_SEARCH_ENGINE_ID:
        return [{"error": "Google Custom Search not configured. Please set GOOGLE_CUSTOM_SEARCH_API_KEY and GOOGLE_CUSTOM_SEARCH_ENGINE_ID in your .env file."}]
    
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': GOOGLE_CUSTOM_SEARCH_API_KEY,
            'cx': GOOGLE_CUSTOM_SEARCH_ENGINE_ID,
            'q': query,
            'num': min(num_results, 10)  # Google CSE max is 10
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        if 'items' in data:
            results = []
            for item in data['items']:
                result = {
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'displayLink': item.get('displayLink', '')
                }
                results.append(result)
            return results
        else:
            return [{"error": "No search results found"}]
            
    except requests.exceptions.RequestException as e:
        return [{"error": f"Search request failed: {str(e)}"}]
    except json.JSONDecodeError as e:
        return [{"error": f"Invalid response format: {str(e)}"}]
    except Exception as e:
        return [{"error": f"Unexpected error: {str(e)}"}]

# =========================
# GEMINI SETUP
# =========================

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
GEMINI_MODEL = "gemini-1.5-flash"  # Updated to a working model

# =========================
# CONTEXT
# =========================

class SportsAgentContext(BaseModel):
    """Context for UK sports information agents."""
    user_name: str | None = None
    favorite_team: str | None = None
    favorite_sport: str | None = None  # "football", "boxing"
    last_query_type: str | None = None  # "premier_league", "championship", "boxing"
    user_id: str | None = None  # Unique identifier for the user

def create_initial_context() -> SportsAgentContext:
    """
    Factory for a new SportsAgentContext.
    For demo: generates a fake user ID.
    In production, this should be set from real user data.
    """
    ctx = SportsAgentContext()
    ctx.user_id = str(random.randint(10000000, 99999999))
    return ctx

# =========================
# TOOL FUNCTIONS
# =========================

def premier_league_lookup_tool(query: str) -> str:
    """Lookup Premier League information."""
    q = query.lower()
    
    # Team standings
    if "standings" in q or "table" in q or "position" in q:
        return "Current Premier League Top 5: 1. Arsenal (86 pts), 2. Manchester City (85 pts), 3. Liverpool (82 pts), 4. Aston Villa (68 pts), 5. Tottenham (63 pts)"
    
    # Team information
    if "arsenal" in q:
        return "Arsenal FC - Founded 1886, Home: Emirates Stadium, Manager: Mikel Arteta, Current Position: 1st"
    if "manchester city" in q or "man city" in q:
        return "Manchester City FC - Founded 1880, Home: Etihad Stadium, Manager: Pep Guardiola, Current Position: 2nd"
    if "liverpool" in q:
        return "Liverpool FC - Founded 1892, Home: Anfield, Manager: Arne Slot, Current Position: 3rd"
    if "manchester united" in q or "man utd" in q:
        return "Manchester United FC - Founded 1878, Home: Old Trafford, Manager: Erik ten Hag, Current Position: 8th"
    if "chelsea" in q:
        return "Chelsea FC - Founded 1905, Home: Stamford Bridge, Manager: Enzo Maresca, Current Position: 6th"
    
    # Player information
    if "haaland" in q:
        return "Erling Haaland - Manchester City striker, 2023/24 Golden Boot winner with 27 goals"
    if "salah" in q:
        return "Mohamed Salah - Liverpool forward, 3-time Golden Boot winner, 155 Premier League goals"
    if "kane" in q:
        return "Harry Kane - Bayern Munich striker (formerly Tottenham), England captain, 213 Premier League goals"
    
    # Fixtures and results
    if "fixtures" in q or "schedule" in q:
        return "Next Premier League fixtures: Arsenal vs Chelsea (Sat 3pm), Man City vs Liverpool (Sun 4:30pm)"
    if "results" in q:
        return "Latest results: Arsenal 3-1 Chelsea, Man City 2-2 Liverpool, Tottenham 1-0 Man United"
    
    # General Premier League info
    if "premier league" in q or "pl" in q:
        return "The Premier League is England's top football division. 20 teams compete, with 3 relegated each season. Season runs August-May."
    
    return "I can help with Premier League teams, players, standings, fixtures, and results. What specific information do you need?"

def championship_lookup_tool(query: str) -> str:
    """Lookup Championship (second tier) information."""
    q = query.lower()
    
    # Team standings
    if "standings" in q or "table" in q or "position" in q:
        return "Current Championship Top 5: 1. Leicester City (97 pts), 2. Ipswich Town (96 pts), 3. Leeds United (90 pts), 4. Southampton (87 pts), 5. West Brom (72 pts)"
    
    # Team information
    if "leicester" in q:
        return "Leicester City FC - Founded 1884, Home: King Power Stadium, Manager: Steve Cooper, Current Position: 1st"
    if "leeds" in q:
        return "Leeds United FC - Founded 1919, Home: Elland Road, Manager: Daniel Farke, Current Position: 3rd"
    if "southampton" in q:
        return "Southampton FC - Founded 1885, Home: St Mary's Stadium, Manager: Russell Martin, Current Position: 4th"
    if "norwich" in q:
        return "Norwich City FC - Founded 1902, Home: Carrow Road, Manager: David Wagner, Current Position: 6th"
    
    # Promotion/Relegation
    if "promotion" in q or "promoted" in q:
        return "Top 2 teams are automatically promoted to Premier League. Teams 3-6 enter playoffs for the 3rd promotion spot."
    if "relegation" in q or "relegated" in q:
        return "Bottom 3 teams are relegated to League One. Currently in relegation zone: Rotherham, Sheffield Wednesday, Huddersfield"
    
    # General Championship info
    if "championship" in q:
        return "The Championship is England's second tier. 24 teams compete, with 3 promoted and 3 relegated each season."
    
    return "I can help with Championship teams, standings, promotion/relegation, and fixtures. What specific information do you need?"

def boxing_lookup_tool(query: str) -> str:
    """Lookup boxing information."""
    q = query.lower()
    
    # Boxers
    if "fury" in q:
        return "Tyson Fury - WBC Heavyweight Champion, 34-0-1 record, 'The Gypsy King', Next fight: vs Usyk (Feb 2025)"
    if "usyk" in q:
        return "Oleksandr Usyk - IBF/WBA/WBO Heavyweight Champion, 21-0 record, Former undisputed cruiserweight champion"
    if "joshua" in q or "aj" in q:
        return "Anthony Joshua - Former unified heavyweight champion, 26-3 record, Next fight: vs Hrgovic (Sept 2024)"
    if "bellew" in q:
        return "Tony Bellew - Former WBC cruiserweight champion, retired 2018, 30-3-1 record"
    if "brook" in q:
        return "Kell Brook - Former IBF welterweight champion, retired 2022, 40-3 record"
    
    # Weight divisions
    if "heavyweight" in q:
        return "Heavyweight division: 200+ lbs. Current champions: Fury (WBC), Usyk (IBF/WBA/WBO), Zhang (WBO interim)"
    if "welterweight" in q:
        return "Welterweight division: 147 lbs. Current champions: Crawford (WBA/WBC/WBO), Ennis (IBF)"
    if "middleweight" in q:
        return "Middleweight division: 160 lbs. Current champions: Charlo (WBC), Munguia (WBO), Andrade (WBA)"
    
    # Upcoming fights
    if "fights" in q or "schedule" in q or "next" in q:
        return "Upcoming major fights: Fury vs Usyk (Feb 2025), Joshua vs Hrgovic (Sept 2024), Crawford vs Madrimov (Aug 2024)"
    
    # British boxing
    if "british" in q or "uk" in q:
        return "Top British boxers: Tyson Fury, Anthony Joshua, Chris Eubank Jr, Conor Benn, Leigh Wood, Josh Warrington"
    
    # General boxing info
    if "boxing" in q:
        return "Boxing has 17 weight divisions. Major sanctioning bodies: WBC, WBA, IBF, WBO. Undisputed champion holds all 4 belts."
    
    return "I can help with boxers, weight divisions, upcoming fights, and British boxing. What specific information do you need?"

def sports_news_tool(query: str) -> str:
    """Get latest sports news."""
    q = query.lower()
    
    if "football" in q:
        return "Latest football news: Arsenal sign new striker, Man City's Haaland wins Player of the Year, Liverpool appoint new manager"
    if "boxing" in q:
        return "Latest boxing news: Fury-Usyk fight confirmed for February, Joshua returns to winning ways, New British heavyweight prospect emerges"
    if "transfer" in q:
        return "Latest transfers: Arsenal sign Victor Osimhen, Man United target new midfielder, Chelsea complete defender signing"
    
    return "Latest sports news: Premier League season starts August 17th, Boxing returns to Wembley in September, Championship playoff final set for May"

# =========================
# GROUNDING TOOLS
# =========================

def format_search_results(results: list) -> str:
    """
    Format Google Custom Search results as clickable links with titles and snippets.
    """
    formatted_results = []
    for i, result in enumerate(results, 1):
        title = result.get('title', '')
        link = result.get('link', '')
        display_link = result.get('displayLink', '')
        snippet = result.get('snippet', '')
        formatted_results.append(
            f"<b>{i}. <a href='{link}' target='_blank'>{title}</a></b> <span style='color: #888;'>({display_link})</span><br>{snippet}<br>"
        )
    return "<br><br>".join(formatted_results)

# Placeholder for scraping logic

def scrape_fixtures_from_official_sites(results: list) -> str:
    """
    If a result is from chelseafc.com or premierleague.com, fetch and extract the fixture list.
    Returns a formatted string of fixtures if found, else an empty string.
    """
    for result in results:
        link = result.get('link', '')
        if 'chelseafc.com' in link or 'premierleague.com' in link:
            try:
                resp = requests.get(link, timeout=5)
                soup = BeautifulSoup(resp.text, 'html.parser')
                # Try to extract fixture info (this is a placeholder, real logic will be added next)
                fixtures = []
                # Example: look for table rows or list items with dates and teams
                for li in soup.find_all(['li', 'tr']):
                    text = li.get_text(separator=' ', strip=True)
                    if re.search(r'\b2025\b|\b2026\b', text) and ('chelsea' in text.lower()):
                        fixtures.append(text)
                if fixtures:
                    return '<br>'.join(fixtures)
            except Exception as e:
                continue
    return ''

def sports_grounding_tool(query: str) -> str:
    """
    Use Google Custom Search to find up-to-date sports information.
    This is used when Gemini doesn't have current information.
    """
    if not GOOGLE_CUSTOM_SEARCH_API_KEY or not GOOGLE_CUSTOM_SEARCH_ENGINE_ID:
        return "Google Custom Search not configured. Please set GOOGLE_CUSTOM_SEARCH_API_KEY and GOOGLE_CUSTOM_SEARCH_ENGINE_ID in your .env file."
    try:
        sports_query = query
        results = google_custom_search(sports_query, num_results=5)
        if results and 'error' not in results[0]:
            # Try to scrape fixtures from official sites
            scraped_fixtures = scrape_fixtures_from_official_sites(results)
            formatted_results = format_search_results(results)
            if scraped_fixtures:
                return f"<b>Extracted Fixture List from Official Site:</b><br>{scraped_fixtures}<br><br><b>Other Web Results:</b><br>{formatted_results}"
            else:
                return f"<b>Web Results:</b><br>{formatted_results}"
        else:
            return f"Could not find recent information for '{query}'. The search returned: {results[0].get('error', 'Unknown error')}"
    except Exception as e:
        return f"Error searching for current information: {str(e)}"

def check_if_grounding_needed(query: str, gemini_response: str) -> bool:
    """
    Determine if grounding is needed based on the query and Gemini's response.
    Only trigger if Gemini explicitly says it doesn't know or can't provide the information.
    """
    query_lower = query.lower()
    response_lower = gemini_response.lower()
    
    # Check for indicators that grounding might be needed
    grounding_indicators = [
        "i don't have information about",
        "i don't know",
        "i'm not sure",
        "i don't have access to",
        "i cannot provide",
        "i still cannot provide",
        "i don't have current",
        "i don't have up-to-date",
        "i don't have recent",
        "i don't have the latest",
        "i don't have information on",
        "i don't have data about",
        "i don't have details about",
        "the information is simply not yet public",
        "isn't available yet",
        "not yet available",
        "not yet public knowledge",
        "simply isn't available",
        "not yet released",
        "not yet announced",
        "unfortunately, none of the provided",
        "cannot access external websites",
        "don't have access to real-time",
        "limited to what's provided"
    ]
    
    # Only trigger grounding if Gemini explicitly says it doesn't know
    if any(indicator in response_lower for indicator in grounding_indicators):
        print(f"[DEBUG] Grounding triggered: Gemini says it doesn't know")
        return True
    
    # If Gemini gave a substantial answer, don't ground
    if len(response_lower.strip()) > 50:
        print(f"[DEBUG] No grounding needed: Gemini gave a substantial answer")
        return False
    
    print(f"[DEBUG] No grounding needed: Gemini appears to have answered")
    return False

# =========================
# AGENT PROMPTS
# =========================

AGENT_PROMPTS = {
    "Triage Agent": (
        "You are a helpful triaging agent for UK sports information. "
        "You can delegate questions to other appropriate agents: Premier League, Championship, Boxing, or Sports News. "
        "If you are unsure, ask clarifying questions. Be enthusiastic about sports!"
    ),
    "Premier League Agent": (
        "You are a Premier League expert agent with extensive knowledge about teams, players, fixtures, and history. "
        "Use your knowledge to answer questions about Premier League teams, players, standings, fixtures, and historical information. "
        "If you know the answer (like upcoming fixtures, team information, player stats, historical results), provide it directly. "
        "Only mention needing real-time access if you truly don't have the information in your knowledge base. "
        "Be passionate about the Premier League and provide detailed, accurate information from your training data."
    ),
    "Championship Agent": (
        "You are a Championship (second tier) expert agent with knowledge about Championship teams, promotion/relegation, and standings. "
        "Use your knowledge to answer questions about Championship teams, players, and historical information. "
        "If you know the answer, provide it directly. Only mention needing real-time access if you truly don't have the information. "
        "The Championship is exciting with promotion battles and playoff drama."
    ),
    "Boxing Agent": (
        "You are a boxing expert agent with knowledge about boxers, weight divisions, upcoming fights, and British boxing. "
        "Use your knowledge to answer questions about boxers, fights, and boxing history. "
        "If you know the answer, provide it directly. Only mention needing real-time access if you truly don't have the information. "
        "Be knowledgeable about current champions, historical fights, and the sport's rich history."
    ),
    "Sports News Agent": (
        "You are a sports news agent with knowledge about football transfers, boxing news, and general sports developments. "
        "Use your knowledge to provide updates on football transfers, boxing news, and general sports developments. "
        "If you know the answer, provide it directly. Only mention needing real-time access if you truly don't have the information. "
        "Keep users informed about breaking news and major developments in UK sports."
    ),
}

AGENT_LIST = [
    "Triage Agent",
    "Premier League Agent",
    "Championship Agent",
    "Boxing Agent",
    "Sports News Agent",
]

# =========================
# GEMINI CHAT COMPLETION
# =========================

def gemini_chat(messages, system_prompt=None):
    model = genai.GenerativeModel(model_name=GEMINI_MODEL)
    history = []
    for m in messages:
        # Prepend system prompt to the first user message if provided
        content = m["content"]
        if system_prompt and m["role"] == "user" and len(history) == 0:
            content = f"{system_prompt}\n\n{content}"
        history.append({"role": m["role"], "parts": [content]})
    convo = model.start_chat(history=history)
    response = convo.send_message(messages[-1]["content"])
    return response.text

# =========================
# AGENT ORCHESTRATION
# =========================

def route_to_agent(user_message, context, current_agent):
    """
    Simple routing logic: triage agent decides which agent should handle the message.
    Returns (next_agent, tool_call) where tool_call is a dict or None.
    """
    # For demo: use keywords to route, or let Gemini decide
    print(f"[DEBUG] Routing: current_agent={current_agent}, user_message='{user_message}'")
    if current_agent == "Triage Agent":
        # Use Gemini to classify intent
        system_prompt = AGENT_PROMPTS["Triage Agent"] + "\nClassify the user's intent as one of: Premier League, Championship, Boxing, Sports News. Respond ONLY with the agent name."
        agent_guess = gemini_chat([
            {"role": "user", "content": user_message}
        ], system_prompt=system_prompt)
        agent_guess = agent_guess.strip()
        print(f"[DEBUG] Gemini classified agent: {agent_guess}")
        if agent_guess in AGENT_LIST:
            return agent_guess, None
        # Fallback: keyword routing
        if "premier league" in user_message.lower() or "arsenal" in user_message.lower() or "man city" in user_message.lower():
            return "Premier League Agent", None
        if "championship" in user_message.lower() or "leicester" in user_message.lower() or "leeds" in user_message.lower():
            return "Championship Agent", None
        if "boxing" in user_message.lower() or "fury" in user_message.lower() or "joshua" in user_message.lower():
            return "Boxing Agent", None
        if "news" in user_message.lower() or "transfer" in user_message.lower():
            return "Sports News Agent", None
        return "Premier League Agent", None  # Default to Premier League
    # For other agents, stay unless they want to transfer
    if "transfer" in user_message.lower() or "triage" in user_message.lower():
        return "Triage Agent", None
    return current_agent, None

# =========================
# AGENT RESPONSE
# =========================

def agent_respond(agent_name, user_message, context, rerouted=False):
    print(f"[DEBUG] agent_respond: agent_name={agent_name}, user_message='{user_message}', rerouted={rerouted}")
    
    # Get the system prompt for this agent
    system_prompt = AGENT_PROMPTS.get(agent_name, "You are a helpful assistant.")
    
    # ALWAYS let Gemini answer first with its knowledge
    initial_response = gemini_chat([
        {"role": "user", "content": user_message}
    ], system_prompt=system_prompt)
    
    print(f"[DEBUG] Initial Gemini response: {initial_response}")
    
    # Check if grounding is needed (for current info that Gemini might not have)
    if check_if_grounding_needed(user_message, initial_response):
        print(f"[DEBUG] Grounding needed for query: '{user_message}'")
        grounded_info = sports_grounding_tool(user_message)
        print(f"[DEBUG] Grounded info: {grounded_info[:200]}...")
        
        grounding_prompt = f"""
{system_prompt}

The user asked: "{user_message}"

Here are the most recent web search results:

{grounded_info}

You MUST use the above web results to answer the user's question. If the results contain a fixture list, summarize or quote it directly. If not, explain that the information is not available online."
"""
        
        final_response = gemini_chat([
            {"role": "user", "content": f"User: {user_message}\n\nPlease provide an updated response using the web results above."}
        ], system_prompt=grounding_prompt)
        
        print(f"[DEBUG] Final Gemini response with grounding: {final_response}")
        
        # Fallback: If Gemini still ignores the info, append the web results
        if ("not available" in final_response.lower() or "cannot provide" in final_response.lower() or "don't know" in final_response.lower() or len(final_response.strip()) < 100):
            return f"{final_response}\n\n---\n\n[See more from the web]\n{grounded_info}"
        return final_response
    
    # If no grounding needed, return Gemini's original answer
    print(f"[DEBUG] Using Gemini's original answer for query: '{user_message}'")
    return initial_response
