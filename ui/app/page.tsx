"use client";

import { useEffect, useState } from "react";
import { AgentPanel } from "@/components/agent-panel";
import { Chat } from "@/components/Chat";
import type { Agent, AgentEvent, GuardrailCheck, Message } from "@/lib/types";
import { callChatAPI } from "@/lib/api";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [currentAgent, setCurrentAgent] = useState<string>("");
  const [guardrails, setGuardrails] = useState<GuardrailCheck[]>([]);
  const [context, setContext] = useState<Record<string, any>>({});
  const [conversationId, setConversationId] = useState<string | null>(null);
  // Loading state while awaiting assistant response
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState<string | null>(null);

  // Boot the conversation
  useEffect(() => {
    (async () => {
      try {
        const data = await callChatAPI("", conversationId ?? "");
        if (!data) {
          setApiError("Unable to connect to the backend API. Please check your environment variables.");
          return;
        }
        
        setConversationId(data.conversation_id);
        setCurrentAgent(data.current_agent || "");
        setContext(data.context || {});
        const initialEvents = (data.events || []).map((e: any) => ({
          ...e,
          timestamp: e.timestamp ?? Date.now(),
        }));
        setEvents(initialEvents);
        setAgents(data.agents || []);
        setGuardrails(data.guardrails || []);
        if (Array.isArray(data.messages)) {
          setMessages(
            data.messages.map((m: any) => ({
              id: Date.now().toString() + Math.random().toString(),
              content: m.content,
              role: "assistant",
              agent: m.agent,
              timestamp: new Date(),
            }))
          );
        }
      } catch (error) {
        console.error("Error initializing chat:", error);
        setApiError("Failed to initialize the chat. Please try refreshing the page.");
      }
    })();
  }, []);

  // Send a user message
  const handleSendMessage = async (content: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      content,
      role: "user",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);
    setApiError(null);

    try {
      const data = await callChatAPI(content, conversationId ?? "");
      
      if (!data) {
        setApiError("Unable to connect to the backend API. Please check your environment variables.");
        setIsLoading(false);
        return;
      }

      if (!conversationId) setConversationId(data.conversation_id);
      setCurrentAgent(data.current_agent || "");
      setContext(data.context || {});
      if (data.events) {
        const stamped = data.events.map((e: any) => ({
          ...e,
          timestamp: e.timestamp ?? Date.now(),
        }));
        setEvents((prev) => [...prev, ...stamped]);
      }
      if (data.agents) setAgents(data.agents);
      // Update guardrails state
      if (data.guardrails) setGuardrails(data.guardrails);

      if (data.messages) {
        const responses: Message[] = data.messages.map((m: any) => ({
          id: Date.now().toString() + Math.random().toString(),
          content: m.content,
          role: "assistant",
          agent: m.agent,
          timestamp: new Date(),
        }));
        setMessages((prev) => [...prev, ...responses]);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setApiError("Failed to send message. Please try again.");
    }

    setIsLoading(false);
  };

  return (
    <main className="flex h-screen gap-2 bg-gray-100 p-2">
      <AgentPanel
        agents={agents}
        currentAgent={currentAgent}
        events={events}
        guardrails={guardrails}
        context={context}
      />
      <Chat
        messages={messages}
        onSendMessage={handleSendMessage}
        isLoading={isLoading}
      />
      {messages.length === 0 && !isLoading && !apiError && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="bg-white/80 backdrop-blur-sm rounded-lg p-6 shadow-lg max-w-md text-center">
            <h2 className="text-xl font-bold text-gray-800 mb-2">Welcome to UK Sports!</h2>
            <p className="text-gray-600 mb-4">
              Ask me about Premier League football, Championship teams, boxing, or the latest sports news.
            </p>
            <div className="text-sm text-gray-500 space-y-1">
              <p>• "What's the Premier League table?"</p>
              <p>• "Tell me about Tyson Fury"</p>
              <p>• "Championship promotion race"</p>
              <p>• "Latest sports news"</p>
            </div>
          </div>
        </div>
      )}
      {apiError && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6 shadow-lg max-w-md text-center">
            <h2 className="text-xl font-bold text-red-800 mb-2">API Connection Error</h2>
            <p className="text-red-600 mb-4">{apiError}</p>
            <div className="text-sm text-red-500">
              <p>Please check your environment variables in Vercel:</p>
              <p>• GOOGLE_API_KEY</p>
              <p>• GOOGLE_CSE_ID</p>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
