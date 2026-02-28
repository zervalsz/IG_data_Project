import { NextResponse } from 'next/server'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000'

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url)
    const platform = searchParams.get('platform') || 'instagram'
    
    // Fetch creators from FastAPI backend
    const response = await fetch(`${API_BASE}/api/creators/list?platform=${platform}`, {
      cache: 'no-store' // Disable caching for fresh data
    })
    
    if (!response.ok) {
      console.error('[Instagram API] Backend returned non-OK status:', response.status)
      return NextResponse.json(
        { error: 'Failed to fetch creators from backend', creators: [] },
        { status: response.status }
      )
    }
    
    const data = await response.json()
    
    // Transform the data to match frontend expectations
    const creators = (data.creators || []).map((creator: any) => ({
      id: creator.user_id || creator.username,
      name: creator.username || creator.user_id,
      platform: creator.platform || 'instagram',
      followers: 0, // TODO: Add follower count if available
      topics: (creator.topics || []).map((t: any) => 
        typeof t === 'string' ? t : t.topic || 'unknown'
      ),
      style: creator.content_style || 'Unknown',
      profileData: creator.profile_data || {}
    }))
    
    return NextResponse.json({
      creators,
      total: data.total || creators.length,
      platform
    })
    
  } catch (error: any) {
    console.error('[Instagram API] Error:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error', creators: [] },
      { status: 500 }
    )
  }
}
