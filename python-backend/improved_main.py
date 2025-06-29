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
import time
from typing import Optional, Dict, Any, List
import logging
from functools import lru_cache
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# =========================
# CONFIGURATION & VALIDATION
# =========================

class Config:
    """Centralized configuration management."""
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.google_custom_search_api_key = os.getenv("GOOGLE_CUSTOM_SEARCH_API_KEY")
        self.google_custom_search_engine_id = os.getenv("GOOGLE_CUSTOM_SEARCH_ENGINE_ID")
        self.gemini_model = "gemini-1.5-flash"
        self.max_search_results = 5
        self.request_timeout = 10
        self.cache_ttl = 300  # 5 minutes
        
        self._validate_config()
    
    def _validate_config(self):
        """Validate required configuration."""
        required_vars = {
            "GOOGLE_API_KEY": self.google_api_key,
            "GOOGLE_CUSTOM_SEARCH_API_KEY": self.google_custom_search_api_key,
            "GOOGLE_CUSTOM_SEARCH_ENGINE_ID": self.google_custom_search_engine_id
        }
        
        missing = [var for var, value in required_vars.items() if not value]
        if missing:
            logger.error(f"Missing required environment variables: {missing}")
            raise ValueError(f"Missing required environment variables: {missing}")

config = Config()

# =========================
# CACHING LAYER
# =========================

class SimpleCache:
    """Simple in-memory cache with TTL."""
    
    def __init__(self):
        self._cache = {}
        self._timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        if key in self._cache:
            if time.time() - self._timestamps[key] < config.cache_ttl:
                return self._cache[key]
            else:
                # Expired
                del self._cache[key]
                del self._timestamps[key]
        return None
    
    def set(self, key: str, value: Any):
        self._cache[key] = value
        self._timestamps[key] = time.time()
    
    def clear(self):
        self._cache.clear()
        self._timestamps.clear()

cache = SimpleCache()

# =========================
# ENHANCED ERROR HANDLING
# =========================

class APIError(Exception):
    """Custom API error with retry logic."""
    def __init__(self, message: str, retry_after: Optional[int] = None):
        self.message = message
        self.retry_after = retry_after
        super().__init__(message)

def handle_api_error(func):
    """Decorator for handling API errors with retry logic."""
    def wrapper(*args, **kwargs):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry {attempt + 1}")
                    time.sleep(wait_time)
                    continue
                elif attempt == max_retries - 1:
                    logger.error(f"API call failed after {max_retries} attempts: {e}")
                    raise APIError(f"API call failed: {str(e)}")
                else:
                    raise
    return wrapper

# =========================
# IMPROVED GEMINI SETUP
# =========================

genai.configure(api_key=config.google_api_key)

@handle_api_error
def safe_gemini_call(messages: List[Dict], system_prompt: Optional[str] = None) -> str:
    """Safe Gemini API call with error handling."""
    try:
        model = genai.GenerativeModel(model_name=config.gemini_model)
        
        # Build conversation history
        history = []
        for m in messages:
            content = m["content"]
            if system_prompt and m["role"] == "user" and len(history) == 0:
                content = f"{system_prompt}\n\n{content}"
            history.append({"role": m["role"], "parts": [content]})
        
        convo = model.start_chat(history=history)
        response = convo.send_message(messages[-1]["content"])
        return response.text
        
    except Exception as e:
        logger.error(f"Gemini API error: {e}")
        if "429" in str(e):
            raise APIError("Rate limit exceeded", retry_after=60)
        raise APIError(f"Gemini API error: {str(e)}")

# =========================
# ENHANCED CONTEXT MANAGEMENT
# =========================

class SportsAgentContext(BaseModel):
    """Enhanced context for UK sports information agents."""
    user_name: Optional[str] = None
    favorite_team: Optional[str] = None
    favorite_sport: Optional[str] = None
    last_query_type: Optional[str] = None
    user_id: Optional[str] = None
    conversation_history: List[Dict[str, Any]] = []
    preferences: Dict[str, Any] = {}
    session_start: Optional[float] = None

def create_initial_context() -> SportsAgentContext:
    """Factory for a new SportsAgentContext."""
    ctx = SportsAgentContext()
    ctx.user_id = str(random.randint(10000000, 99999999))
    ctx.session_start = time.time()
    return ctx

# =========================
# IMPROVED SEARCH & GROUNDING
# =========================

@lru_cache(maxsize=100)
def cached_google_search(query: str, num_results: int = 5) -> str:
    """Cached Google Custom Search."""
    cache_key = f"search:{query}:{num_results}"
    cached_result = cache.get(cache_key)
    if cached_result:
        return cached_result
    
    result = google_custom_search(query, num_results)
    cache.set(cache_key, json.dumps(result))
    return json.dumps(result)

@handle_api_error
def google_custom_search(query: str, num_results: int = 5) -> List[Dict]:
    """Enhanced Google Custom Search with better error handling."""
    if not config.google_custom_search_api_key or not config.google_custom_search_engine_id:
        return [{"error": "Google Custom Search not configured"}]
    
    try:
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': config.google_custom_search_api_key,
            'cx': config.google_custom_search_engine_id,
            'q': query,
            'num': min(num_results, 10),
            'safe': 'active'  # Safe search
        }
        
        response = requests.get(url, params=params, timeout=config.request_timeout)
        response.raise_for_status()
        
        data = response.json()
        
        if 'items' in data:
            results = []
            for item in data['items']:
                result = {
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', ''),
                    'displayLink': item.get('displayLink', ''),
                    'formattedUrl': item.get('formattedUrl', '')
                }
                results.append(result)
            return results
        else:
            return [{"error": "No search results found"}]
            
    except requests.exceptions.Timeout:
        return [{"error": "Search request timed out"}]
    except requests.exceptions.RequestException as e:
        return [{"error": f"Search request failed: {str(e)}"}]
    except json.JSONDecodeError as e:
        return [{"error": f"Invalid response format: {str(e)}"}]
    except Exception as e:
        return [{"error": f"Unexpected error: {str(e)}"}]

def intelligent_grounding_check(query: str, gemini_response: str) -> bool:
    """More intelligent grounding detection."""
    query_lower = query.lower()
    response_lower = gemini_response.lower()
    
    # Strong indicators that grounding is needed
    strong_indicators = [
        "i don't have information about",
        "i don't know",
        "i cannot provide",
        "i don't have access to",
        "i don't have current",
        "i don't have up-to-date",
        "i don't have recent",
        "not available in my training data"
    ]
    
    # Time-sensitive queries that likely need current data
    time_sensitive_patterns = [
        r'\b(2025|2026)\b',
        r'\b(latest|recent|current|today|now)\b',
        r'\b(fixtures?|schedule|upcoming)\b',
        r'\b(transfer|signing|news)\b'
    ]
    
    # Check for explicit "don't know" responses
    if any(indicator in response_lower for indicator in strong_indicators):
        logger.info(f"Grounding triggered: Gemini explicitly doesn't know")
        return True
    
    # Check for time-sensitive queries with short responses
    if len(response_lower.strip()) < 100:  # Short response might indicate lack of knowledge
        for pattern in time_sensitive_patterns:
            if re.search(pattern, query_lower):
                logger.info(f"Grounding triggered: Time-sensitive query with short response")
                return True
    
    return False

# =========================
# ENHANCED AGENT SYSTEM
# =========================

ENHANCED_AGENT_PROMPTS = {
    "Triage Agent": (
        "You are a friendly and knowledgeable UK sports triage agent. Your role is to understand what the user wants "
        "and route them to the most appropriate specialist agent. You have access to experts in:\n"
        "- Premier League (teams, players, fixtures, standings)\n"
        "- Championship (second tier football)\n"
        "- Boxing (fighters, matches, news)\n"
        "- Sports News (transfers, breaking news)\n\n"
        "Be conversational and helpful. If you're unsure about routing, ask clarifying questions. "
        "Always explain why you're transferring them to a specific agent."
    ),
    "Premier League Agent": (
        "You are a Premier League expert with comprehensive knowledge about all 20 teams, players, history, and statistics. "
        "Use your extensive training data to provide detailed, accurate information about:\n"
        "- Team information, history, and current status\n"
        "- Player profiles, statistics, and transfers\n"
        "- Historical results and standings\n"
        "- Match analysis and predictions\n\n"
        "Only mention needing real-time data if you truly don't have the information in your knowledge base. "
        "Be passionate and knowledgeable about the Premier League."
    ),
    "Championship Agent": (
        "You are a Championship football expert with deep knowledge of England's second tier. "
        "Provide detailed information about Championship teams, promotion/relegation battles, and player movements. "
        "Use your knowledge to discuss the excitement of the Championship with its playoff system and competitive nature."
    ),
    "Boxing Agent": (
        "You are a boxing expert with comprehensive knowledge of professional boxing, including:\n"
        "- Current and former world champions\n"
        "- Weight divisions and title holders\n"
        "- Fight history and upcoming matches\n"
        "- British boxing scene\n\n"
        "Provide detailed, accurate information from your training data. Only mention needing current information "
        "if you truly don't have the details in your knowledge base."
    ),
    "Sports News Agent": (
        "You are a sports news expert focusing on UK sports developments. "
        "Provide updates on transfers, breaking news, and major sports developments using your knowledge base. "
        "Cover football transfers, boxing news, and general sports developments in the UK."
    ),
}

def enhanced_agent_respond(agent_name: str, user_message: str, context: SportsAgentContext) -> str:
    """Enhanced agent response with better error handling and context awareness."""
    logger.info(f"Agent {agent_name} responding to: {user_message[:50]}...")
    
    try:
        # Get the system prompt for this agent
        system_prompt = ENHANCED_AGENT_PROMPTS.get(agent_name, "You are a helpful assistant.")
        
        # Add context to the prompt if available
        if context.favorite_team:
            system_prompt += f"\n\nUser's favorite team: {context.favorite_team}"
        if context.favorite_sport:
            system_prompt += f"\nUser's favorite sport: {context.favorite_sport}"
        
        # Get initial response from Gemini
        initial_response = safe_gemini_call([
            {"role": "user", "content": user_message}
        ], system_prompt=system_prompt)
        
        logger.info(f"Initial response length: {len(initial_response)}")
        
        # Check if grounding is needed
        if intelligent_grounding_check(user_message, initial_response):
            logger.info("Grounding needed, searching for current information...")
            
            # Get search results
            search_results_json = cached_google_search(user_message, config.max_search_results)
            search_results = json.loads(search_results_json)
            
            if search_results and 'error' not in search_results[0]:
                # Format search results
                formatted_results = format_search_results(search_results)
                
                # Get enhanced response with grounding
                grounding_prompt = f"""
{system_prompt}

The user asked: "{user_message}"

Here are current web search results:
{formatted_results}

Please provide a comprehensive response using both your knowledge and the web results above.
If the web results contain specific fixture information or current data, incorporate it into your response.
"""
                
                final_response = safe_gemini_call([
                    {"role": "user", "content": f"User: {user_message}\n\nPlease provide an updated response using the web results."}
                ], system_prompt=grounding_prompt)
                
                logger.info("Enhanced response with grounding generated")
                return final_response
            else:
                logger.warning("Search failed, using initial response")
                return initial_response + "\n\n(Note: Unable to fetch the latest information at this time.)"
        
        # Return initial response if no grounding needed
        logger.info("Using initial Gemini response")
        return initial_response
        
    except APIError as e:
        logger.error(f"API error in agent response: {e}")
        return f"I'm experiencing some technical difficulties right now. Please try again in a moment. ({e.message})"
    except Exception as e:
        logger.error(f"Unexpected error in agent response: {e}")
        return "I apologize, but I'm having trouble processing your request right now. Please try again."

def format_search_results(results: List[Dict]) -> str:
    """Enhanced search results formatting."""
    if not results:
        return "No search results available."
    
    formatted_results = []
    for i, result in enumerate(results, 1):
        title = result.get('title', 'No title')
        link = result.get('link', '')
        display_link = result.get('displayLink', '')
        snippet = result.get('snippet', 'No description available')
        
        formatted_results.append(
            f"<b>{i}. <a href='{link}' target='_blank'>{title}</a></b> "
            f"<span style='color: #888;'>({display_link})</span><br>"
            f"{snippet}<br>"
        )
    
    return "<br><br>".join(formatted_results)

# =========================
# IMPROVED ROUTING
# =========================

def smart_route_to_agent(user_message: str, context: SportsAgentContext, current_agent: str) -> tuple[str, Optional[Dict]]:
    """Enhanced routing with context awareness."""
    logger.info(f"Routing from {current_agent}: {user_message[:50]}...")
    
    if current_agent == "Triage Agent":
        # Use keyword-based routing with fallback to Gemini
        message_lower = user_message.lower()
        
        # Direct keyword routing
        if any(keyword in message_lower for keyword in ['premier league', 'arsenal', 'chelsea', 'manchester', 'liverpool', 'tottenham']):
            return "Premier League Agent", None
        elif any(keyword in message_lower for keyword in ['championship', 'leicester', 'leeds', 'norwich']):
            return "Championship Agent", None
        elif any(keyword in message_lower for keyword in ['boxing', 'fury', 'joshua', 'usyk', 'fight']):
            return "Boxing Agent", None
        elif any(keyword in message_lower for keyword in ['transfer', 'news', 'signing', 'latest']):
            return "Sports News Agent", None
        
        # Fallback to Gemini classification
        try:
            classification_prompt = (
                "Classify this sports query into one of these categories: "
                "Premier League, Championship, Boxing, Sports News. "
                "Respond with ONLY the category name."
            )
            
            agent_classification = safe_gemini_call([
                {"role": "user", "content": user_message}
            ], system_prompt=classification_prompt)
            
            agent_classification = agent_classification.strip()
            if agent_classification + " Agent" in ENHANCED_AGENT_PROMPTS:
                return agent_classification + " Agent", None
                
        except Exception as e:
            logger.warning(f"Agent classification failed: {e}")
        
        # Final fallback
        return "Premier League Agent", None
    
    # Handle transfers back to triage
    if any(keyword in user_message.lower() for keyword in ['transfer', 'triage', 'different', 'other']):
        return "Triage Agent", None
    
    return current_agent, None

# Export the enhanced functions
route_to_agent = smart_route_to_agent
agent_respond = enhanced_agent_respond

# Keep the original AGENT_LIST for compatibility
AGENT_LIST = [
    "Triage Agent",
    "Premier League Agent", 
    "Championship Agent",
    "Boxing Agent",
    "Sports News Agent"
]