import { NextResponse } from 'next/server'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5000'

export async function GET(
  request: Request,
  { params }: { params: Promise<{ username: string }> }
) {
  try {
    const { username } = await params
    
    // Fetch creator detail from FastAPI backend
    const response = await fetch(
      `${API_BASE}/api/creators/${encodeURIComponent(username)}?platform=instagram`,
      { cache: 'no-store' }
    )
    
    if (!response.ok) {
      if (response.status === 404) {
        return NextResponse.json(
          { error: 'Creator not found' },
          { status: 404 }
        )
      }
      return NextResponse.json(
        { error: 'Failed to fetch creator' },
        { status: response.status }
      )
    }
    
    const data = await response.json()
    
    // Transform to frontend format
    const creator = {
      id: data.user_id,
      username: data.username || data.user_id,
      platform: data.platform,
      profileData: data.profile_data || {},
      createdAt: data.created_at,
      updatedAt: data.updated_at
    }
    
    return NextResponse.json(creator)
    
  } catch (error: any) {
    console.error('[Instagram Creator Detail API] Error:', error)
    return NextResponse.json(
      { error: error.message || 'Internal server error' },
      { status: 500 }
    )
  }
}
