import os
import sys
import json
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add the python-backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'python-backend'))

try:
    from main import app
    import google.generativeai as genai
    from fastapi import Request
    from fastapi.responses import JSONResponse
    import asyncio
except ImportError as e:
    print(f"Import error: {e}")

def handle_chat_request(message: str, conversation_id: str = ""):
    """Handle chat request using the existing Python backend logic"""
    try:
        # Configure Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            return {
                "error": "GOOGLE_API_KEY not configured",
                "conversation_id": conversation_id,
                "current_agent": "triage",
                "context": {},
                "events": [],
                "agents": [],
                "guardrails": [],
                "messages": []
            }
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Simple response for now - you can expand this with your full agent logic
        response = model.generate_content(f"User message: {message}\n\nPlease provide a helpful response about UK sports (Premier League, Championship, Boxing, or general sports news).")
        
        return {
            "conversation_id": conversation_id or "conv-" + str(hash(message)),
            "current_agent": "triage",
            "context": {},
            "events": [
                {
                    "type": "agent_selected",
                    "agent": "triage",
                    "timestamp": int(asyncio.get_event_loop().time() * 1000)
                }
            ],
            "agents": [
                {"id": "triage", "name": "Triage Agent", "description": "Routes your questions to the right specialist"},
                {"id": "premier_league", "name": "Premier League", "description": "Premier League football expert"},
                {"id": "championship", "name": "Championship", "description": "Championship football expert"},
                {"id": "boxing", "name": "Boxing", "description": "Boxing expert"},
                {"id": "sports_news", "name": "Sports News", "description": "Latest sports news and updates"}
            ],
            "guardrails": [],
            "messages": [
                {
                    "content": response.text,
                    "agent": "triage",
                    "timestamp": int(asyncio.get_event_loop().time() * 1000)
                }
            ]
        }
    except Exception as e:
        print(f"Error in chat handler: {e}")
        return {
            "error": f"Backend error: {str(e)}",
            "conversation_id": conversation_id,
            "current_agent": "triage",
            "context": {},
            "events": [],
            "agents": [],
            "guardrails": [],
            "messages": []
        }

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Parse the request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            body = json.loads(post_data.decode('utf-8'))
            
            message = body.get('message', '')
            conversation_id = body.get('conversation_id', '')
            
            # Handle the chat request
            result = handle_chat_request(message, conversation_id)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            print(f"Handler error: {e}")
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers() 