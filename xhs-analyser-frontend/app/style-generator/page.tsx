"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface Creator {
  user_id: string;
  nickname?: string;
  topics?: string[];
  style?: string;
  profile_data?: {
    user_style?: {
      persona?: string;
      tone?: string;
    };
  };
}

export default function StyleGeneratorPage() {
  const [creators, setCreators] = useState<Creator[]>([]);
  const [selectedCreator, setSelectedCreator] = useState<string>("");
  const [topic, setTopic] = useState("");
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<string>("");
  const [error, setError] = useState<string>("");

  useEffect(() => {
    fetchCreators();
  }, []);

  const fetchCreators = async () => {
    try {
      // Use Next.js API proxy
      const response = await fetch('/api/proxy/creators');
      if (!response.ok) throw new Error('Failed to fetch creators');
      
      const data = await response.json();
      setCreators(data.creators || []);
    } catch (error) {
      console.error('Error fetching creators:', error);
      setError('Failed to load creators');
    }
  };

  const handleGenerate = async () => {
    if (!selectedCreator || !topic.trim()) {
      setError('Please select a creator and enter a topic');
      return;
    }

    setGenerating(true);
    setError('');
    setResult('');

    try {
      // Use Next.js API proxy
      const response = await fetch('/api/proxy/style/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          creator_name: selectedCreator,
          user_input: topic,
          platform: 'instagram'
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Generation failed');
      }
      
      const data = await response.json();
      setResult(data.content || '');
    } catch (error) {
      console.error('Error generating content:', error);
      setError(error instanceof Error ? error.message : 'Failed to generate content. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const selectedCreatorData = creators.find(c => c.user_id === selectedCreator);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 py-12">
      <div className="container mx-auto px-6">
        {/* Header */}
        <div className="mb-8">
          <Link href="/" className="inline-flex items-center text-purple-600 hover:text-purple-700 mb-4">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Home
          </Link>
          <h1 className="text-4xl font-bold text-gray-900">🎨 Style-Based Generator</h1>
          <p className="text-gray-600 mt-2">Pick a creator and topic to generate content in their unique style</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Input Panel */}
          <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Select Creator
              </label>
              <select
                value={selectedCreator}
                onChange={(e) => setSelectedCreator(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <option value="">Choose a creator...</option>
                {creators.map(creator => (
                  <option key={creator.user_id} value={creator.user_id}>
                    @{creator.user_id}
                    {creator.style && ` - ${creator.style.split(',')[0].trim()}`}
                  </option>
                ))}
              </select>
            </div>

            {selectedCreatorData && (
              <div className="bg-purple-50 rounded-lg p-4">
                <h3 className="font-semibold text-purple-900 mb-2">Creator Style</h3>
                {selectedCreatorData.profile_data?.user_style?.persona && (
                  <p className="text-sm text-purple-800 mb-2">
                    {selectedCreatorData.profile_data.user_style.persona}
                  </p>
                )}
                {selectedCreatorData.style && (
                  <p className="text-sm text-purple-700">
                    <span className="font-medium">Tone:</span> {selectedCreatorData.style}
                  </p>
                )}
                {selectedCreatorData.topics && selectedCreatorData.topics.length > 0 && (
                  <div className="mt-2">
                    <p className="text-sm text-purple-700 font-medium mb-1">Topics:</p>
                    <div className="flex flex-wrap gap-1">
                      {selectedCreatorData.topics.slice(0, 3).map((topic, idx) => (
                        <span key={idx} className="text-xs bg-purple-200 text-purple-800 px-2 py-1 rounded">
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Your Topic
              </label>
              <textarea
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                placeholder="e.g., how to save money for travel, healthy breakfast ideas, overcoming anxiety..."
                rows={4}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
              />
            </div>

            <button
              onClick={handleGenerate}
              disabled={generating || !selectedCreator || !topic.trim()}
              className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-4 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {generating ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Generating...
                </span>
              ) : (
                'Generate Content'
              )}
            </button>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                {error}
              </div>
            )}
          </div>

          {/* Result Panel */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Generated Content</h2>
            
            {result ? (
              <div className="space-y-4">
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-6">
                  <div className="prose prose-purple max-w-none">
                    <pre className="whitespace-pre-wrap font-sans text-gray-800 leading-relaxed">
                      {result}
                    </pre>
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => navigator.clipboard.writeText(result)}
                    className="flex-1 bg-purple-100 text-purple-700 py-2 rounded-lg hover:bg-purple-200 transition-colors font-medium"
                  >
                    📋 Copy to Clipboard
                  </button>
                  <button
                    onClick={() => {
                      setResult('');
                      setTopic('');
                    }}
                    className="flex-1 bg-gray-100 text-gray-700 py-2 rounded-lg hover:bg-gray-200 transition-colors font-medium"
                  >
                    🔄 Generate New
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-gray-400">
                <svg className="w-24 h-24 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="text-lg">Your generated content will appear here</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
