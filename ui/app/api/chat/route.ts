import { NextRequest, NextResponse } from 'next/server';

// Simple fallback responses for when backend is not available
const FALLBACK_RESPONSES = {
  "premier league": "I can help with Premier League information! However, the full backend system is not currently available. Please ensure your Python backend is running on port 8000.",
  "championship": "I can help with Championship football! However, the full backend system is not currently available. Please ensure your Python backend is running on port 8000.",
  "boxing": "I can help with boxing information! However, the full backend system is not currently available. Please ensure your Python backend is running on port 8000.",
  "transfer": "I can help with transfer news! However, the full backend system is not currently available. Please ensure your Python backend is running on port 8000.",
  "default": "Hello! I'm your UK Sports assistant. I can help with Premier League, Championship, Boxing, and Sports News. However, the full backend system is not currently available. Please ensure your Python backend is running on port 8000."
};

function getFallbackResponse(message: string): string {
  const messageLower = message.toLowerCase();
  
  for (const [key, response] of Object.entries(FALLBACK_RESPONSES)) {
    if (key !== 'default' && messageLower.includes(key)) {
      return response;
    }
  }
  
  return FALLBACK_RESPONSES.default;
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, conversation_id } = body;
    
    // Validate input
    if (!message || typeof message !== 'string') {
      return NextResponse.json(
        { error: 'Message is required and must be a string' },
        { status: 400 }
      );
    }
    
    if (message.length > 1000) {
      return NextResponse.json(
        { error: 'Message too long (max 1000 characters)' },
        { status: 400 }
      );
    }
    
    // Try to call the Python backend first
    try {
      const backendUrl = process.env.NODE_ENV === 'development' 
        ? 'http://127.0.0.1:8000/chat'
        : `${process.env.VERCEL_URL || 'http://localhost:3000'}/api/python-chat`;
      
      const pythonResponse = await fetch(backendUrl, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ message, conversation_id }),
        signal: AbortSignal.timeout(10000) // 10 second timeout
      });
      
      if (pythonResponse.ok) {
        const data = await pythonResponse.json();
        return NextResponse.json(data);
      } else {
        console.log(`Python backend returned ${pythonResponse.status}`);
      }
    } catch (error) {
      console.log('Python backend not available:', error);
    }
    
    // Fallback response when backend is not available
    const fallbackMessage = getFallbackResponse(message);
    
    return NextResponse.json({
      conversation_id: conversation_id || "fallback-" + Date.now(),
      current_agent: "triage",
      context: {
        user_name: null,
        favorite_team: null,
        favorite_sport: null,
        last_query_type: null,
        user_id: null
      },
      events: [
        {
          id: "event-" + Date.now(),
          type: "agent_selected",
          agent: "triage",
          content: "Fallback mode activated",
          timestamp: Date.now()
        }
      ],
      agents: [
        { name: "Triage Agent", description: "Routes your questions to the right specialist", handoffs: [], tools: [], input_guardrails: [] },
        { name: "Premier League Agent", description: "Premier League football expert", handoffs: [], tools: [], input_guardrails: [] },
        { name: "Championship Agent", description: "Championship football expert", handoffs: [], tools: [], input_guardrails: [] },
        { name: "Boxing Agent", description: "Boxing expert", handoffs: [], tools: [], input_guardrails: [] },
        { name: "Sports News Agent", description: "Latest sports news and updates", handoffs: [], tools: [], input_guardrails: [] }
      ],
      guardrails: [],
      messages: [
        {
          content: fallbackMessage,
          agent: "triage",
          timestamp: Date.now()
        }
      ]
    });
    
  } catch (error) {
    console.error("API route error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    status: "healthy",
    message: "UK Sports Chat API is running",
    timestamp: Date.now()
  });
}