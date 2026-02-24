import { NextResponse } from 'next/server'

/**
 * GET /api/style/creators
 * Proxy to backend API to get Instagram creators list
 */
export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const platform = searchParams.get('platform') || 'instagram'
    
    // Backend is always accessible from the server via localhost
    const backendUrl = `http://localhost:5000/api/creators/list?platform=${platform}`
    console.log('[api/style/creators] Proxying to:', backendUrl)
    
    const response = await fetch(backendUrl)
    
    if (!response.ok) {
      console.error('[api/style/creators] Backend error:', response.status)
      return NextResponse.json(
        { error: 'Failed to fetch creators from backend' },
        { status: response.status }
      )
    }
    
    const data = await response.json()
    console.log(`[api/style/creators] ✅ Fetched ${data.creators?.length || 0} creators`)
    
    // Return creators array directly (backend already returns {creators: [...], total: N})
    return NextResponse.json(data.creators || [])
    
  } catch (error) {
    console.error('[api/style/creators] ❌ Error:', error)
    return NextResponse.json(
      { error: 'Failed to connect to backend' },
      { status: 500 }
    )
  }
}
