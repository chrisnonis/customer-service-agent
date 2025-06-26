import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // In production, this will be handled by the Python backend
    // For now, we'll return a simple response
    return NextResponse.json({
      message: "API route working",
      body: body
    });
  } catch (error) {
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
} 