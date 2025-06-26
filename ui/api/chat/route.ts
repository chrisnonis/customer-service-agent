import { NextRequest, NextResponse } from 'next/server';
import { GoogleGenerativeAI } from '@google/generative-ai';

// Initialize Gemini
const genai = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY!);
const GEMINI_MODEL = "gemini-1.5-flash";

// In-memory conversation store (for demo - use a database in production)
const conversations = new Map();

// Agent prompts
const AGENT_PROMPTS = {
  "Triage Agent": "You are a helpful triaging agent for an airline. You can delegate questions to other appropriate agents: FAQ, Seat Booking, Flight Status, or Cancellation. If you are unsure, ask clarifying questions.",
  "FAQ Agent": "You are an FAQ agent. Answer questions about the airline using your knowledge. If you cannot answer, transfer to the triage agent.",
  "Seat Booking Agent": "You are a seat booking agent. Help the customer update their seat. Ask for their confirmation number and desired seat if not provided. If the question is not about seat booking, transfer to the triage agent.",
  "Flight Status Agent": "You are a flight status agent. Help customers check flight status. If the question is not about flight status, transfer to the triage agent.",
  "Cancellation Agent": "You are a cancellation agent. Help the customer cancel their flight. Ask for confirmation and flight number if not provided. If the question is not about cancellation, transfer to the triage agent."
};

const AGENT_LIST = [
  "Triage Agent",
  "FAQ Agent", 
  "Seat Booking Agent",
  "Flight Status Agent",
  "Cancellation Agent"
];

// Tool functions
function faq_lookup_tool(question: string): string {
  const q = question.toLowerCase();
  
  if (q.includes('bag') || q.includes('baggage') || q.includes('luggage')) {
    if (q.includes('fee') || q.includes('cost') || q.includes('charge')) {
      return "Overweight bag fee is $75. Additional checked bags are $35 each.";
    }
    return "You are allowed to bring one carry-on bag (22x14x9 inches) and one checked bag (up to 50 lbs) for free. Overweight fees are $75.";
  }
  
  if (q.includes('seat') || q.includes('plane')) {
    return "There are 120 seats on the plane: 22 business class and 98 economy seats. Exit rows are 4 and 16, Economy Plus is rows 5-8.";
  }
  
  if (q.includes('wifi') || q.includes('internet')) {
    return "We have free wifi on the plane. Connect to 'Airline-Wifi' network. No password required.";
  }
  
  return "I'm here to help with airline-related questions. Could you please be more specific about what you'd like to know?";
}

function route_to_agent(userMessage: string, currentAgent: string): string {
  if (currentAgent === "Triage Agent") {
    // Simple keyword routing for demo
    const message = userMessage.toLowerCase();
    if (message.includes('seat')) return "Seat Booking Agent";
    if (message.includes('status') || message.includes('flight')) return "Flight Status Agent";
    if (message.includes('cancel')) return "Cancellation Agent";
    if (message.includes('faq') || message.includes('question')) return "FAQ Agent";
    return "FAQ Agent"; // Default
  }
  
  if (userMessage.toLowerCase().includes('transfer') || userMessage.toLowerCase().includes('triage')) {
    return "Triage Agent";
  }
  
  return currentAgent;
}

async function agent_respond(agentName: string, userMessage: string): Promise<string> {
  const systemPrompt = AGENT_PROMPTS[agentName as keyof typeof AGENT_PROMPTS];
  
  // Special tool calls
  if (agentName === "FAQ Agent") {
    const toolAnswer = faq_lookup_tool(userMessage);
    if (toolAnswer !== "I'm here to help with airline-related questions. Could you please be more specific about what you'd like to know?") {
      return toolAnswer;
    }
  }
  
  // Use Gemini for response
  try {
    const model = genai.getGenerativeModel({ model: GEMINI_MODEL });
    const prompt = `${systemPrompt}\n\nUser: ${userMessage}\n\nAgent:`;
    const result = await model.generateContent(prompt);
    const response = await result.response;
    return response.text();
  } catch (error) {
    console.error('Gemini API error:', error);
    return "I apologize, but I'm having trouble processing your request right now. Please try again later.";
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, conversation_id } = body;

    // TODO: Implement Gemini API call and agent orchestration logic here
    // For now, just echo the message
    return NextResponse.json({
      conversation_id: conversation_id || 'demo',
      current_agent: 'Triage Agent',
      messages: [{ content: `Echo: ${message}`, agent: 'Triage Agent' }],
      events: [],
      context: {},
      agents: [],
      guardrails: []
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 