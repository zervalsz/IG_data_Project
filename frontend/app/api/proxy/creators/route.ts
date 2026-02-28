import { NextResponse } from 'next/server';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000';

export async function GET(request: Request) {
  try {
    // Backend is accessible via environment variable or localhost
    const backendUrl = `${API_BASE_URL}/api/creators/list?platform=instagram`;
    
    const response = await fetch(backendUrl);
    
    if (!response.ok) {
      return NextResponse.json(
        { error: 'Failed to fetch from backend' },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to backend' },
      { status: 500 }
    );
  }
}
