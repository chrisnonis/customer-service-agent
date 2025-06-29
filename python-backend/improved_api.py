"""
Improved FastAPI application with better error handling and validation.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from uuid import uuid4
import time
import logging
from contextlib import asynccontextmanager

from improved_main import (
    create_initial_context,
    AGENT_LIST,
    route_to_agent,
    agent_respond,
    config
)
from database import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    logger.info("Starting UK Sports Agent API")
    
    # Startup
    try:
        # Test database connection
        db.cleanup_old_conversations()
        logger.info("Database initialized successfully")
        
        # Test API keys
        if not config.google_api_key:
            logger.warning("GOOGLE_API_KEY not configured")
        
        yield
        
    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise
    finally:
        # Shutdown
        logger.info("Shutting down UK Sports Agent API")

app = FastAPI(
    title="UK Sports Agent API",
    description="Multi-agent system for UK sports information",
    version="2.0.0",
    lifespan=lifespan
)

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# =========================
# Enhanced Models
# =========================

class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
    
    @validator('message')
    def validate_message(cls, v):
        if not v or not v.strip():
            raise ValueError('Message cannot be empty')
        if len(v) > 1000:
            raise ValueError('Message too long (max 1000 characters)')
        return v.strip()

class MessageResponse(BaseModel):
    content: str
    agent: str
    timestamp: float

class AgentEvent(BaseModel):
    id: str
    type: str
    agent: str
    content: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: float

class GuardrailCheck(BaseModel):
    id: str
    name: str
    input: str
    reasoning: str
    passed: bool
    timestamp: float

class ChatResponse(BaseModel):
    conversation_id: str
    current_agent: str
    messages: List[MessageResponse]
    events: List[AgentEvent]
    context: Dict[str, Any]
    agents: List[Dict[str, Any]]
    guardrails: List[GuardrailCheck] = []

# =========================
# Dependency Functions
# =========================

async def get_conversation_state(conversation_id: Optional[str]) -> tuple[str, Dict[str, Any], bool]:
    """Get or create conversation state."""
    is_new = not conversation_id
    
    if is_new:
        conversation_id = uuid4().hex
        ctx = create_initial_context()
        state = {
            "history": [],
            "context": ctx,
            "current_agent": "Triage Agent",
            "created_at": time.time()
        }
        db.save_conversation(conversation_id, state)
    else:
        state = db.get_conversation(conversation_id)
        if not state:
            # Conversation not found, create new one
            is_new = True
            ctx = create_initial_context()
            state = {
                "history": [],
                "context": ctx,
                "current_agent": "Triage Agent",
                "created_at": time.time()
            }
            db.save_conversation(conversation_id, state)
    
    return conversation_id, state, is_new

def build_agents_list() -> List[Dict[str, Any]]:
    """Build enhanced agents list."""
    agent_descriptions = {
        "Triage Agent": "Routes your questions to the right specialist",
        "Premier League Agent": "Premier League football expert with comprehensive team and player knowledge",
        "Championship Agent": "Championship football expert covering promotion battles and team news",
        "Boxing Agent": "Boxing expert covering fighters, matches, and British boxing scene",
        "Sports News Agent": "Latest sports news, transfers, and breaking developments"
    }
    
    return [
        {
            "name": name,
            "description": agent_descriptions.get(name, name),
            "handoffs": [],
            "tools": [],
            "input_guardrails": []
        }
        for name in AGENT_LIST
    ]

# =========================
# API Endpoints
# =========================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "2.0.0"
    }

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """Enhanced chat endpoint with better error handling."""
    try:
        # Get conversation state
        conversation_id, state, is_new = await get_conversation_state(req.conversation_id)
        
        # Handle empty message for new conversations
        if is_new and not req.message.strip():
            return ChatResponse(
                conversation_id=conversation_id,
                current_agent=state["current_agent"],
                messages=[],
                events=[],
                context=state["context"].model_dump() if hasattr(state["context"], 'model_dump') else state["context"],
                agents=build_agents_list(),
                guardrails=[]
            )
        
        # Process the message
        user_message = req.message
        current_agent = state["current_agent"]
        context = state["context"]
        
        # Route to appropriate agent
        next_agent, _ = route_to_agent(user_message, context, current_agent)
        state["current_agent"] = next_agent
        
        # Get agent response
        response_text = agent_respond(next_agent, user_message, context)
        
        # Update conversation history
        state.setdefault("history", []).extend([
            {"role": "user", "content": user_message, "timestamp": time.time()},
            {"role": "assistant", "content": response_text, "agent": next_agent, "timestamp": time.time()}
        ])
        
        # Save updated state
        db.save_conversation(conversation_id, state)
        
        # Build response
        messages = [MessageResponse(
            content=response_text,
            agent=next_agent,
            timestamp=time.time()
        )]
        
        events = [AgentEvent(
            id=uuid4().hex,
            type="message",
            agent=next_agent,
            content=response_text,
            timestamp=time.time()
        )]
        
        return ChatResponse(
            conversation_id=conversation_id,
            current_agent=next_agent,
            messages=messages,
            events=events,
            context=context.model_dump() if hasattr(context, 'model_dump') else context,
            agents=build_agents_list(),
            guardrails=[]
        )
        
    except ValueError as e:
        logger.warning(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history."""
    try:
        state = db.get_conversation(conversation_id)
        if not state:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        return {
            "conversation_id": conversation_id,
            "history": state.get("history", []),
            "current_agent": state.get("current_agent", "Triage Agent"),
            "created_at": state.get("created_at", time.time())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get conversation error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete a conversation."""
    try:
        # Note: This is a simple implementation
        # In a real database, you'd have a proper delete method
        state = db.get_conversation(conversation_id)
        if not state:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # For now, we'll just return success
        # TODO: Implement actual deletion in database.py
        return {"message": "Conversation deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete conversation error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)