import { NextResponse } from 'next/server';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

// Increase timeout for trend generation (it can take 30-60 seconds)
export const maxDuration = 60; // Maximum execution time in seconds
export const dynamic = 'force-dynamic'; // Don't cache this route

export async function POST(request: Request) {
  try {
    const body = await request.json();
    
    // Backend is accessible via environment variable or localhost
    const backendUrl = `${API_BASE_URL}/api/trend/generate`;
    
    const response = await fetch(backendUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      // Set a longer timeout for trend generation (60 seconds)
      signal: AbortSignal.timeout(60000),
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      return NextResponse.json(
        { error: errorData.detail || 'Failed to generate trend content' },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Trend generation proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to backend' },
      { status: 500 }
    );
  }
}
