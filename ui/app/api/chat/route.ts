import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, conversation_id } = body;
    
    // Check if we have the required environment variables
    const apiKey = process.env.GOOGLE_API_KEY;
    
    if (!apiKey) {
      return NextResponse.json({
        conversation_id: conversation_id || "mock-conversation-id",
        current_agent: "triage",
        context: {},
        events: [
          {
            type: "agent_selected",
            agent: "triage",
            timestamp: Date.now()
          }
        ],
        agents: [
          { id: "triage", name: "Triage Agent", description: "Routes your questions to the right specialist" },
          { id: "premier_league", name: "Premier League", description: "Premier League football expert" },
          { id: "championship", name: "Championship", description: "Championship football expert" },
          { id: "boxing", name: "Boxing", description: "Boxing expert" },
          { id: "sports_news", name: "Sports News", description: "Latest sports news and updates" }
        ],
        guardrails: [],
        messages: [
          {
            content: `I received your message: "${message}". Please set up your GOOGLE_API_KEY environment variable in Vercel to get real AI responses.`,
            agent: "triage",
            timestamp: Date.now()
          }
        ]
      });
    }
    
    // If we have the API key, try to call the Python backend
    try {
      const pythonResponse = await fetch(`${process.env.VERCEL_URL || 'http://localhost:3000'}/api/python-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message, conversation_id })
      });
      
      if (pythonResponse.ok) {
        return NextResponse.json(await pythonResponse.json());
      }
    } catch (error) {
      console.log('Python backend not available, using fallback');
    }
    
    // Fallback: Use a simple response
    return NextResponse.json({
      conversation_id: conversation_id || "conv-" + Date.now(),
      current_agent: "triage",
      context: {},
      events: [
        {
          type: "agent_selected",
          agent: "triage",
          timestamp: Date.now()
        }
      ],
      agents: [
        { id: "triage", name: "Triage Agent", description: "Routes your questions to the right specialist" },
        { id: "premier_league", name: "Premier League", description: "Premier League football expert" },
        { id: "championship", name: "Championship", description: "Championship football expert" },
        { id: "boxing", name: "Boxing", description: "Boxing expert" },
        { id: "sports_news", name: "Sports News", description: "Latest sports news and updates" }
      ],
      guardrails: [],
      messages: [
        {
          content: `I received your message: "${message}". The Python backend is not yet available. Please check your deployment configuration.`,
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