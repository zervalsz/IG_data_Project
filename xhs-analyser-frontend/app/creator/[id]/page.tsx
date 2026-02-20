"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";

interface CreatorProfile {
  user_id: string;
  nickname?: string;
  bio?: string;
  followers_count?: number;
  following_count?: number;
  platform: string;
  profile_data?: {
    user_style?: {
      persona?: string;
      tone?: string;
      interests?: string[];
      engagement_style?: string;
    };
    content_topics?: string[];
    typical_content?: string;
  };
}

export default function CreatorProfilePage() {
  const params = useParams();
  const creatorId = params?.id as string;
  
  const [profile, setProfile] = useState<CreatorProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (creatorId) {
      console.log('[CreatorProfile] Loading profile for:', creatorId);
      fetchProfile();
    }
  }, [creatorId]);

  const fetchProfile = async () => {
    try {
      console.log('[CreatorProfile] Fetching from:', `/api/proxy/creator/${creatorId}`);
      
      // Use Next.js API proxy
      const response = await fetch(`/api/proxy/creator/${creatorId}`);
      console.log('[CreatorProfile] Response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('[CreatorProfile] Error response:', errorData);
        throw new Error(errorData.error || 'Failed to fetch profile');
      }
      
      const data = await response.json();
      console.log('[CreatorProfile] Received profile data:', data);
      setProfile(data);
    } catch (error) {
      console.error('[CreatorProfile] Error fetching profile:', error);
      setError(error instanceof Error ? error.message : 'Failed to load creator profile');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Profile Not Found</h2>
          <p className="text-gray-600 mb-4">{error || 'This creator profile could not be loaded'}</p>
          <Link href="/" className="text-purple-600 hover:text-purple-700">
            Back to Home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 py-12">
      <div className="container mx-auto px-6 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <Link href="/" className="inline-flex items-center text-purple-600 hover:text-purple-700 mb-4">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Home
          </Link>
        </div>

        {/* Profile Card */}
        <div className="bg-white rounded-3xl shadow-xl overflow-hidden">
          {/* Header Section */}
          <div className="bg-gradient-to-r from-purple-600 to-pink-600 p-8 text-white">
            <div className="flex items-start justify-between">
              <div>
                <h1 className="text-4xl font-bold mb-2">@{profile.user_id}</h1>
                {profile.nickname && profile.nickname !== profile.user_id && (
                  <p className="text-purple-100 text-lg">{profile.nickname}</p>
                )}
              </div>
              <div className="bg-white/20 backdrop-blur-sm rounded-full px-4 py-2">
                <span className="text-sm font-semibold">Instagram</span>
              </div>
            </div>

            {profile.followers_count && (
              <div className="mt-6 flex gap-6">
                <div>
                  <div className="text-2xl font-bold">
                    {(profile.followers_count / 1000).toFixed(0)}K
                  </div>
                  <div className="text-purple-100 text-sm">Followers</div>
                </div>
                {profile.following_count && (
                  <div>
                    <div className="text-2xl font-bold">
                      {(profile.following_count / 1000).toFixed(0)}K
                    </div>
                    <div className="text-purple-100 text-sm">Following</div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Content Section */}
          <div className="p-8 space-y-6">
            {/* Bio */}
            {profile.bio && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Bio</h2>
                <p className="text-gray-700">{profile.bio}</p>
              </div>
            )}

            {/* Persona */}
            {profile.profile_data?.user_style?.persona && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Creator Persona</h2>
                <p className="text-gray-700">{profile.profile_data.user_style.persona}</p>
              </div>
            )}

            {/* Style & Tone */}
            {profile.profile_data?.user_style?.tone && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Content Tone</h2>
                <div className="flex flex-wrap gap-2">
                  {profile.profile_data.user_style.tone.split(',').map((tone, idx) => (
                    <span
                      key={idx}
                      className="px-4 py-2 bg-purple-100 text-purple-700 rounded-full font-medium"
                    >
                      {tone.trim()}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Interests */}
            {profile.profile_data?.user_style?.interests && profile.profile_data.user_style.interests.length > 0 && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Interests</h2>
                <div className="flex flex-wrap gap-2">
                  {profile.profile_data.user_style.interests.map((interest, idx) => (
                    <span
                      key={idx}
                      className="px-4 py-2 bg-blue-100 text-blue-700 rounded-full"
                    >
                      {interest}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Content Topics */}
            {profile.profile_data?.content_topics && profile.profile_data.content_topics.length > 0 && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Content Topics</h2>
                <div className="space-y-2">
                  {profile.profile_data.content_topics.map((topic, idx) => (
                    <div
                      key={idx}
                      className="flex items-start gap-2"
                    >
                      <span className="text-purple-600 mt-1">•</span>
                      <span className="text-gray-700">{topic}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Engagement Style */}
            {profile.profile_data?.user_style?.engagement_style && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Engagement Style</h2>
                <p className="text-gray-700">{profile.profile_data.user_style.engagement_style}</p>
              </div>
            )}

            {/* Typical Content */}
            {profile.profile_data?.typical_content && (
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Typical Content</h2>
                <p className="text-gray-700">{profile.profile_data.typical_content}</p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-4 pt-6">
              <Link
                href={`/style-generator?creator=${profile.user_id}`}
                className="flex-1 text-center py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl font-semibold hover:from-purple-700 hover:to-pink-700 transition-all"
              >
                Generate in This Style
              </Link>
              <a
                href={`https://instagram.com/${profile.user_id}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 text-center py-4 bg-gray-100 text-gray-700 rounded-xl font-semibold hover:bg-gray-200 transition-all"
              >
                View on Instagram
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
