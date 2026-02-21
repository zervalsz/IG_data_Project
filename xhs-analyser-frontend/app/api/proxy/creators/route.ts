import { NextResponse } from 'next/server';

export async function GET(request: Request) {
  try {
    // Backend is always accessible from the server via localhost
    const backendUrl = 'http://localhost:8000/api/creators/list?platform=instagram';
    
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
