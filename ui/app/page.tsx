"use client";

import { useEffect, useState } from "react";
import { AgentPanel } from "@/components/agent-panel";
import { Chat } from "@/components/Chat";
import type { Agent, AgentEvent, GuardrailCheck, Message } from "@/lib/types";
import { callChatAPI } from "@/lib/api";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="text-center">
        <h1 className="text-4xl font-bold mb-4">UK Sports Agent System</h1>
        <p className="text-lg text-gray-600 mb-8">
          An intelligent sports information system covering Premier League, Championship, and Boxing
        </p>
        <div className="space-y-2 text-sm text-gray-500">
          <p>• "What's the Premier League table?"</p>
          <p>• "Tell me about Tyson Fury"</p>
          <p>• "Championship promotion race"</p>
          <p>• "Latest sports news"</p>
        </div>
        <div className="mt-8">
          <a 
            href="/test" 
            className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
          >
            Go to Test Page
          </a>
        </div>
      </div>
    </main>
  );
}
