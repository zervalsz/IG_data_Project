"use client";

import { useState, useEffect } from "react";
import Link from "next/link";

interface Creator {
  user_id: string;
  nickname?: string;
  topics?: string[];
  style?: string;
}

interface Category {
  id: string;
  name: string;
  icon: string;
  color: string;
  creators: string[];
}

export default function TrendGeneratorPage() {
  const [categories] = useState<Category[]>([
    {
      id: 'finance',
      name: 'Finance & Money',
      icon: '💰',
      color: 'from-green-400 to-emerald-600',
      creators: []
    },
    {
      id: 'wellness',
      name: 'Mental Health & Wellness',
      icon: '🧘',
      color: 'from-blue-400 to-cyan-600',
      creators: []
    },
    {
      id: 'food',
      name: 'Food & Cooking',
      icon: '🍳',
      color: 'from-orange-400 to-red-600',
      creators: []
    },
    {
      id: 'fitness',
      name: 'Fitness & Sports',
      icon: '💪',
      color: 'from-purple-400 to-pink-600',
      creators: []
    },
    {
      id: 'lifestyle',
      name: 'Lifestyle & Entertainment',
      icon: '✨',
      color: 'from-pink-400 to-rose-600',
      creators: []
    }
  ]);

  const [selectedCategory, setSelectedCategory] = useState<string>("");
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [trendInsights, setTrendInsights] = useState<any>(null);

  const handleGenerate = async () => {
    if (!selectedCategory) {
      setError('Please select a category');
      return;
    }

    setGenerating(true);
    setError('');
    setResult('');
    setTrendInsights(null);

    try {
      // Use Next.js API proxy
      const response = await fetch('/api/proxy/trend/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          category: selectedCategory,
          platform: 'instagram'
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Generation failed');
      }
      
      const data = await response.json();
      setResult(data.content || '');
      setTrendInsights(data.insights || null);
    } catch (error) {
      console.error('Error generating content:', error);
      setError(error instanceof Error ? error.message : 'Failed to generate trend content. Please try again.');
    } finally {
      setGenerating(false);
    }
  };

  const selectedCategoryData = categories.find(c => c.id === selectedCategory);

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 via-pink-50 to-purple-50 py-12">
      <div className="container mx-auto px-6">
        {/* Header */}
        <div className="mb-8">
          <Link href="/" className="inline-flex items-center text-pink-600 hover:text-pink-700 mb-4">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Home
          </Link>
          <h1 className="text-4xl font-bold text-gray-900">📊 Trend-Based Generator</h1>
          <p className="text-gray-600 mt-2">Generate content optimized for engagement based on trending posts in each category</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Input Panel */}
          <div className="bg-white rounded-2xl shadow-xl p-8 space-y-6">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Select Category
              </label>
              <div className="grid grid-cols-1 gap-3">
                {categories.map(category => (
                  <button
                    key={category.id}
                    onClick={() => setSelectedCategory(category.id)}
                    className={`p-4 rounded-xl border-2 transition-all text-left ${
                      selectedCategory === category.id
                        ? 'border-pink-500 bg-pink-50'
                        : 'border-gray-200 hover:border-pink-300 hover:bg-pink-50/50'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${category.color} flex items-center justify-center text-2xl`}>
                        {category.icon}
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{category.name}</h3>
                        <p className="text-sm text-gray-500">AI-optimized for engagement</p>
                      </div>
                      {selectedCategory === category.id && (
                        <svg className="w-6 h-6 text-pink-600 ml-auto" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                        </svg>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {selectedCategoryData && (
              <div className="bg-pink-50 rounded-lg p-4">
                <h3 className="font-semibold text-pink-900 mb-2">How It Works</h3>
                <ul className="text-sm text-pink-800 space-y-1">
                  <li>✓ Analyzes all posts in {selectedCategoryData.name}</li>
                  <li>✓ Identifies high-performing content patterns</li>
                  <li>✓ Uses engagement metrics (likes, views, comments)</li>
                  <li>✓ Generates optimized content for maximum reach</li>
                </ul>
              </div>
            )}

            <button
              onClick={handleGenerate}
              disabled={generating || !selectedCategory}
              className="w-full bg-gradient-to-r from-pink-600 to-orange-600 text-white py-4 rounded-lg font-semibold hover:from-pink-700 hover:to-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              {generating ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Analyzing Trends...
                </span>
              ) : (
                'Generate Trending Content'
              )}
            </button>

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-start gap-2">
                  <svg className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <div className="flex-1">
                    <h4 className="font-semibold text-red-900 mb-1">Error</h4>
                    <p className="text-sm text-red-800">{error}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Result Panel */}
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Generated Content</h2>
            
            {result ? (
              <div className="space-y-4">
                {trendInsights && (
                  <div className="bg-gradient-to-br from-pink-50 to-orange-50 rounded-lg p-4 mb-4">
                    <h3 className="font-semibold text-pink-900 mb-3">📊 Trend Insights</h3>
                    
                    {trendInsights.engagement_rate && (
                      <div className="bg-white/70 rounded-lg p-3 mb-3 text-sm text-gray-700">
                        <div className="font-medium text-pink-900 mb-1">💡 Engagement Rate: {trendInsights.engagement_rate}%</div>
                        <div className="text-xs">
                          Based on actual follower data from {trendInsights.creators_analyzed || 'multiple'} established creators. 
                          Metrics below are projected for a ~10K follower account.
                        </div>
                      </div>
                    )}
                    
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div className="bg-white/50 rounded p-2">
                        <div className="text-2xl font-bold text-pink-600">{trendInsights.avg_likes?.toLocaleString() || '0'}</div>
                        <div className="text-xs text-gray-600">Expected Likes</div>
                      </div>
                      <div className="bg-white/50 rounded p-2">
                        <div className="text-2xl font-bold text-pink-600">{trendInsights.avg_comments?.toLocaleString() || '0'}</div>
                        <div className="text-xs text-gray-600">Expected Comments</div>
                      </div>
                      <div className="bg-white/50 rounded p-2">
                        <div className="text-2xl font-bold text-pink-600">{trendInsights.avg_engagement?.toLocaleString() || '0'}</div>
                        <div className="text-xs text-gray-600">Total Engagement</div>
                      </div>
                    </div>
                  </div>
                )}

                <div className="bg-gradient-to-br from-pink-50 to-orange-50 rounded-lg p-6">
                  <div className="prose prose-pink max-w-none">
                    <pre className="whitespace-pre-wrap font-sans text-gray-800 leading-relaxed">
                      {result}
                    </pre>
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => navigator.clipboard.writeText(result)}
                    className="flex-1 bg-pink-100 text-pink-700 py-2 rounded-lg hover:bg-pink-200 transition-colors font-medium"
                  >
                    📋 Copy to Clipboard
                  </button>
                  <button
                    onClick={() => {
                      setResult('');
                      setTrendInsights(null);
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
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
                <p className="text-lg">Your trend-optimized content will appear here</p>
                <p className="text-sm mt-2">Select a category to get started</p>
              </div>
            )}
          </div>
        </div>

        {/* Info Banner */}
        <div className="mt-8 bg-gradient-to-r from-pink-50 to-orange-50 rounded-2xl shadow-lg p-6 border-l-4 border-pink-500">
          <h3 className="font-semibold text-gray-900 mb-2">✨ How Trend Generation Works</h3>
          <ul className="text-sm text-gray-700 space-y-2">
            <li className="flex items-start gap-2">
              <span className="text-pink-600 mt-0.5">✓</span>
              <span><strong>Data Analysis:</strong> We analyze all posts from creators in your selected category</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-pink-600 mt-0.5">✓</span>
              <span><strong>Engagement Metrics:</strong> Identifies high-performing content based on likes and comments</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-pink-600 mt-0.5">✓</span>
              <span><strong>Pattern Recognition:</strong> Finds successful patterns and themes in top posts</span>
            </li>
            <li className="flex items-start gap-2">
              <span className="text-pink-600 mt-0.5">✓</span>
              <span><strong>AI Optimization:</strong> Generates content optimized for maximum engagement</span>
            </li>
          </ul>
          
          <div className="mt-4 pt-4 border-t border-pink-200">
            <p className="text-xs text-gray-600">
              💡 <strong>Tip:</strong> The more posts we have in a category, the better our recommendations become. Trend-based content is optimized for your target audience's preferences!
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
