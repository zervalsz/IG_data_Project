"use client";

import { useState, useEffect } from "react";
import { Link } from "@/navigation";
import { useSearchParams } from "next/navigation";

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

interface ConsistencyEvidence {
  metric: string;
  status: string;
  detail: string;
}

interface ConsistencyScore {
  overall_score: number;
  level: string;
  evidence: ConsistencyEvidence[];
  explanation: string;
}

interface GenerateResult {
  content: string;
  consistency_score?: ConsistencyScore;
}

export default function StyleGeneratorPage() {
  const searchParams = useSearchParams();
  const creatorParam = searchParams.get('creator');
  
  const [creators, setCreators] = useState<Creator[]>([]);
  const [selectedCreator, setSelectedCreator] = useState<string>("");
  const [topic, setTopic] = useState("");
  const [generating, setGenerating] = useState(false);
  const [result, setResult] = useState<GenerateResult | null>(null);
  const [error, setError] = useState<string>("");
  
  // Customization options
  const [tone, setTone] = useState<string>("engaging");
  const [length, setLength] = useState<string>("medium");
  const [format, setFormat] = useState<string>("post");

  useEffect(() => {
    fetchCreators();
  }, []);

  // Set selected creator from URL parameter after creators are loaded
  useEffect(() => {
    if (creatorParam && creators.length > 0) {
      const creatorExists = creators.some(c => c.user_id === creatorParam);
      if (creatorExists) {
        setSelectedCreator(creatorParam);
      }
    }
  }, [creatorParam, creators]);

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
    setResult(null);

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
          platform: 'instagram',
          tone,
          length,
          format
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || 'Generation failed');
      }
      
      const data = await response.json();
      setResult({
        content: data.content || '',
        consistency_score: data.consistency_score
      });
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
          <Link href="/explore-creators" className="inline-flex items-center text-purple-600 hover:text-purple-700 mb-4">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Explore Creators
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
            
            {/* Customization Options */}
            <div className="space-y-4">
              <h3 className="font-semibold text-gray-900">Customize Output</h3>
              
              {/* Tone */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Tone</label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => setTone("engaging")}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      tone === "engaging"
                        ? "bg-purple-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    Engaging
                  </button>
                  <button
                    onClick={() => setTone("professional")}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      tone === "professional"
                        ? "bg-purple-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    Professional
                  </button>
                  <button
                    onClick={() => setTone("casual")}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      tone === "casual"
                        ? "bg-purple-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    Casual
                  </button>
                </div>
              </div>
              
              {/* Length */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Length</label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => setLength("short")}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      length === "short"
                        ? "bg-purple-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    Short
                  </button>
                  <button
                    onClick={() => setLength("medium")}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      length === "medium"
                        ? "bg-purple-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    Medium
                  </button>
                  <button
                    onClick={() => setLength("long")}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      length === "long"
                        ? "bg-purple-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    Long
                  </button>
                </div>
              </div>
              
              {/* Format */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Format</label>
                <div className="grid grid-cols-3 gap-2">
                  <button
                    onClick={() => setFormat("post")}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      format === "post"
                        ? "bg-purple-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    Post
                  </button>
                  <button
                    onClick={() => setFormat("bullets")}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      format === "bullets"
                        ? "bg-purple-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    Bullet Points
                  </button>
                  <button
                    onClick={() => setFormat("script")}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      format === "script"
                        ? "bg-purple-600 text-white"
                        : "bg-gray-100 text-gray-700 hover:bg-gray-200"
                    }`}
                  >
                    Script
                  </button>
                </div>
              </div>
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
                {/* Consistency Score Display */}
                {result.consistency_score && (
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border-2 border-purple-200">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-bold text-gray-900">Style Consistency</h3>
                      <div className="flex items-center gap-3">
                        <div className={`text-3xl font-bold ${
                          result.consistency_score.level === 'high' ? 'text-green-600' :
                          result.consistency_score.level === 'medium' ? 'text-yellow-600' :
                          'text-orange-600'
                        }`}>
                          {result.consistency_score.overall_score}/100
                        </div>
                        <div className={`px-3 py-1 rounded-full text-sm font-semibold ${
                          result.consistency_score.level === 'high' ? 'bg-green-100 text-green-700' :
                          result.consistency_score.level === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                          'bg-orange-100 text-orange-700'
                        }`}>
                          {result.consistency_score.level.toUpperCase()}
                        </div>
                      </div>
                    </div>
                    
                    <p className="text-sm text-gray-700 mb-4">
                      {result.consistency_score.explanation}
                    </p>
                    
                    {/* Evidence Breakdown */}
                    <div className="space-y-2">
                      <h4 className="font-semibold text-gray-800 text-sm mb-2">Evidence:</h4>
                      {result.consistency_score.evidence.map((item, idx) => (
                        <div key={idx} className="flex items-start gap-2 text-sm">
                          <span className="text-lg">
                            {item.status === 'perfect' ? '✅' : 
                             item.status === 'close' || item.status === 'matched' ? '✓' : 
                             item.status === 'estimated' ? '≈' : '⚠️'}
                          </span>
                          <div className="flex-1">
                            <span className="font-semibold text-gray-800">{item.metric}:</span>
                            <span className="text-gray-600 ml-2">{item.detail}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Generated Content */}
                <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-6">
                  <h3 className="font-semibold text-gray-900 mb-3">Generated Content</h3>
                  <div className="prose prose-purple max-w-none">
                    <pre className="whitespace-pre-wrap font-sans text-gray-800 leading-relaxed">
                      {result.content}
                    </pre>
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <button
                    onClick={() => navigator.clipboard.writeText(result.content)}
                    className="flex-1 bg-purple-100 text-purple-700 py-2 rounded-lg hover:bg-purple-200 transition-colors font-medium"
                  >
                    📋 Copy to Clipboard
                  </button>
                  <button
                    onClick={() => {
                      setResult(null);
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
