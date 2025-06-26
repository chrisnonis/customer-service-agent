import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, conversation_id } = body;
    
    // For now, return a mock response that matches the expected format
    // In production, this would call the Python backend
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
          content: `I received your message: "${message}". This is a mock response since the Python backend is not yet deployed. To get full functionality, you'll need to set up the Python backend with proper environment variables.`,
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