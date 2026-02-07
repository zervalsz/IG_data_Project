"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface InstagramCreator {
  id: string;
  name: string;
  platform: string;
  followers: number;
  topics: string[];
  style: string;
  profileData?: any;
}

export function InstagramCreatorsList() {
  const [creators, setCreators] = useState<InstagramCreator[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchCreators() {
      try {
        setLoading(true);
        const response = await fetch('/api/instagram/creators?platform=instagram');
        
        if (!response.ok) {
          throw new Error(`Failed to fetch: ${response.status}`);
        }
        
        const data = await response.json();
        setCreators(data.creators || []);
        setError(null);
      } catch (err: any) {
        console.error('[InstagramCreatorsList] Error:', err);
        setError(err.message || 'Failed to load creators');
      } finally {
        setLoading(false);
      }
    }

    fetchCreators();
  }, []);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading Instagram creators...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
        <p className="text-red-600 mb-2">⚠️ Error loading creators</p>
        <p className="text-sm text-red-500">{error}</p>
        <p className="text-xs text-gray-500 mt-2">
          Make sure the FastAPI backend is running at http://localhost:5001
        </p>
      </div>
    );
  }

  if (creators.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-8 text-center">
        <p className="text-gray-700 text-lg mb-2">📭 No Instagram creators found</p>
        <p className="text-sm text-gray-600 mb-4">
          Run the pipeline to analyze Instagram users first
        </p>
        <code className="bg-gray-100 px-3 py-1 rounded text-sm">
          python3 collectors/instagram/pipeline.py --fetch_username username
        </code>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          Instagram Creators ({creators.length})
        </h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {creators.map((creator) => (
          <div
            key={creator.id}
            className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6 border border-gray-200"
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 truncate">
                  @{creator.name}
                </h3>
                <p className="text-sm text-gray-500">
                  {creator.platform}
                </p>
              </div>
              <div className="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold">
                {creator.name[0].toUpperCase()}
              </div>
            </div>

            {creator.topics && creator.topics.length > 0 && (
              <div className="mb-4">
                <p className="text-xs text-gray-500 mb-2">Topics</p>
                <div className="flex flex-wrap gap-2">
                  {creator.topics.slice(0, 3).map((topic, idx) => (
                    <span
                      key={idx}
                      className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full"
                    >
                      {topic}
                    </span>
                  ))}
                  {creator.topics.length > 3 && (
                    <span className="text-xs text-gray-500">
                      +{creator.topics.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            )}

            {creator.style && creator.style !== 'Unknown' && (
              <div className="mb-4">
                <p className="text-xs text-gray-500 mb-1">Style</p>
                <p className="text-sm text-gray-700 line-clamp-2">
                  {creator.style}
                </p>
              </div>
            )}

            <Link
              href={`/instagram/${creator.name}`}
              className="block w-full text-center bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg transition-colors text-sm font-medium"
            >
              View Profile
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
