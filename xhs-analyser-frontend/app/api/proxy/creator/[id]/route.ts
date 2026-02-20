import { NextResponse } from 'next/server';

export async function GET(
  request: Request,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id: creatorId } = await params;
    
    console.log('[Proxy] Fetching creator profile for:', creatorId);
    
    // Backend is always accessible from the server via localhost
    const backendUrl = `http://localhost:5001/api/creators/${creatorId}?platform=instagram`;
    console.log('[Proxy] Backend URL:', backendUrl);
    
    const response = await fetch(backendUrl);
    console.log('[Proxy] Backend response status:', response.status);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('[Proxy] Backend error:', errorText);
      return NextResponse.json(
        { error: 'Creator not found' },
        { status: response.status }
      );
    }
    
    const data = await response.json();
    console.log('[Proxy] Returning creator data for:', creatorId);
    return NextResponse.json(data);
  } catch (error) {
    console.error('Creator profile proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to connect to backend' },
      { status: 500 }
    );
  }
}
