"use client";

import { useState, useEffect } from "react";
import { Link } from "@/navigation";
import { use } from "react";

interface CreatorDetail {
  id: string;
  username: string;
  platform: string;
  profileData: {
    user_style?: {
      persona?: string;
      tone?: string;
      interests?: string[];
    };
    content_topics?: Array<{ topic: string; percentage?: number }>;
    posting_pattern?: {
      frequency?: string;
      best_time_to_post?: string;
      content_mix?: string[];
    };
    audience_type?: string[];
    engagement_style?: string;
    brand_fit?: string[];
  };
  createdAt?: string;
  updatedAt?: string;
}

export default function CreatorDetailPage({
  params,
}: {
  params: Promise<{ username: string }>;
}) {
  const resolvedParams = use(params);
  const [creator, setCreator] = useState<CreatorDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCreator() {
      try {
        setLoading(true);
        const response = await fetch(
          `/api/instagram/creators/${encodeURIComponent(resolvedParams.username)}`
        );

        if (!response.ok) {
          if (response.status === 404) {
            setError("Creator not found");
          } else {
            setError(`Failed to fetch creator: ${response.status}`);
          }
          return;
        }

        const data = await response.json();
        setCreator(data);
        setError(null);
      } catch (err: any) {
        console.error("[CreatorDetail] Error:", err);
        setError(err.message || "Failed to load creator");
      } finally {
        setLoading(false);
      }
    }

    fetchCreator();
  }, [resolvedParams.username]);

  if (loading) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading creator profile...</p>
        </div>
      </main>
    );
  }

  if (error || !creator) {
    return (
      <main className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
        <div className="container mx-auto px-6 py-12">
          <Link
            href="/instagram"
            className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-8"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
              className="w-5 h-5 mr-2"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"
              />
            </svg>
            Back to Instagram Creators
          </Link>

          <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
            <p className="text-red-600 text-lg mb-2">⚠️ {error}</p>
            <p className="text-sm text-gray-600">
              The creator @{resolvedParams.username} was not found in the database.
            </p>
          </div>
        </div>
      </main>
    );
  }

  const { profileData } = creator;
  const userStyle = profileData.user_style || {};
  const topics = profileData.content_topics || [];
  const postingPattern = profileData.posting_pattern || {};
  const audienceTypes = profileData.audience_type || [];
  const brandFit = profileData.brand_fit || [];

  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      <div className="container mx-auto px-6 py-12 max-w-5xl">
        {/* Header */}
        <Link
          href="/instagram"
          className="inline-flex items-center text-blue-600 hover:text-blue-700 mb-8"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2}
            stroke="currentColor"
            className="w-5 h-5 mr-2"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18"
            />
          </svg>
          Back to Instagram Creators
        </Link>

        {/* Profile Header */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-6">
          <div className="flex items-center gap-6">
            <div className="w-24 h-24 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white text-4xl font-bold flex-shrink-0">
              {creator.username[0].toUpperCase()}
            </div>
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                @{creator.username}
              </h1>
              <div className="flex items-center gap-4 text-sm text-gray-600">
                <span className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full">
                  📸 Instagram
                </span>
                {creator.updatedAt && (
                  <span>
                    Updated: {new Date(creator.updatedAt).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>
          </div>

          {userStyle.persona && (
            <div className="mt-6 pt-6 border-t border-gray-200">
              <p className="text-gray-700 leading-relaxed">{userStyle.persona}</p>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* User Style */}
          {(userStyle.tone || (userStyle.interests && userStyle.interests.length > 0)) && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span>🎨</span> Style
              </h2>
              
              {userStyle.tone && (
                <div className="mb-4">
                  <p className="text-sm text-gray-500 mb-2">Tone</p>
                  <p className="text-gray-700">{userStyle.tone}</p>
                </div>
              )}
              
              {userStyle.interests && userStyle.interests.length > 0 && (
                <div>
                  <p className="text-sm text-gray-500 mb-2">Interests</p>
                  <div className="flex flex-wrap gap-2">
                    {userStyle.interests.map((interest, idx) => (
                      <span
                        key={idx}
                        className="bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-sm"
                      >
                        {interest}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Content Topics */}
          {topics.length > 0 && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span>📊</span> Content Topics
              </h2>
              <div className="space-y-3">
                {topics.map((topic, idx) => (
                  <div key={idx}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-gray-700">
                        {typeof topic === "string" ? topic : topic.topic}
                      </span>
                      {typeof topic === "object" && topic.percentage && (
                        <span className="text-gray-500">{topic.percentage}%</span>
                      )}
                    </div>
                    {typeof topic === "object" && topic.percentage && (
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${topic.percentage}%` }}
                        ></div>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Posting Pattern */}
          {(postingPattern.frequency || postingPattern.best_time_to_post || 
            (postingPattern.content_mix && postingPattern.content_mix.length > 0)) && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span>📅</span> Posting Pattern
              </h2>
              <div className="space-y-3">
                {postingPattern.frequency && (
                  <div>
                    <p className="text-sm text-gray-500">Frequency</p>
                    <p className="text-gray-700">{postingPattern.frequency}</p>
                  </div>
                )}
                {postingPattern.best_time_to_post && (
                  <div>
                    <p className="text-sm text-gray-500">Best Time to Post</p>
                    <p className="text-gray-700">{postingPattern.best_time_to_post}</p>
                  </div>
                )}
                {postingPattern.content_mix && postingPattern.content_mix.length > 0 && (
                  <div>
                    <p className="text-sm text-gray-500 mb-2">Content Mix</p>
                    <div className="flex flex-wrap gap-2">
                      {postingPattern.content_mix.map((type, idx) => (
                        <span
                          key={idx}
                          className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-sm"
                        >
                          {type}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Audience & Engagement */}
          {(audienceTypes.length > 0 || profileData.engagement_style) && (
            <div className="bg-white rounded-xl shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span>👥</span> Audience & Engagement
              </h2>
              <div className="space-y-3">
                {audienceTypes.length > 0 && (
                  <div>
                    <p className="text-sm text-gray-500 mb-2">Audience Type</p>
                    <div className="flex flex-wrap gap-2">
                      {audienceTypes.map((type, idx) => (
                        <span
                          key={idx}
                          className="bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm"
                        >
                          {type}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                {profileData.engagement_style && (
                  <div>
                    <p className="text-sm text-gray-500">Engagement Style</p>
                    <p className="text-gray-700">{profileData.engagement_style}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Brand Fit */}
          {brandFit.length > 0 && (
            <div className="bg-white rounded-xl shadow-md p-6 md:col-span-2">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <span>🎯</span> Brand Fit
              </h2>
              <div className="flex flex-wrap gap-2">
                {brandFit.map((brand, idx) => (
                  <span
                    key={idx}
                    className="bg-orange-100 text-orange-700 px-4 py-2 rounded-full text-sm font-medium"
                  >
                    {brand}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
