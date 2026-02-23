"use client";

import { useState, useEffect } from "react";
import { Link } from "@/navigation";

interface Creator {
  user_id: string;
  nickname?: string;
  bio?: string;
  followers_count?: number;
  profile_data?: {
    user_style?: {
      persona?: string;
      tone?: string;
      interests?: string[];
    };
    content_topics?: string[];
  };
}

interface Category {
  id: string;
  name: string;
  icon: string;
  color: string;
  creators: Creator[];
}

export function AccountCategories() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted) {
      fetchCreators();
    }
  }, [mounted]);

  const fetchCreators = async () => {
    if (typeof window === 'undefined') {
      return; // Don't fetch during SSR
    }

    try {
      // Use Next.js API proxy to avoid CORS and port visibility issues
      const url = '/api/proxy/creators';
      console.log('[AccountCategories] Fetching from proxy:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });
      
      if (!response.ok) {
        console.error('[AccountCategories] Response not OK:', response.status, response.statusText);
        throw new Error(`Failed to fetch creators: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('[AccountCategories] Received data:', data);
      const creators: Creator[] = data.creators || [];

      // Categorize creators based on their interests and topics
      const categorized = categorizeCreators(creators);
      setCategories(categorized);
    } catch (error) {
      console.error('[AccountCategories] Error fetching creators:', error);
    } finally {
      setLoading(false);
    }
  };

  const categorizeCreators = (creators: Creator[]): Category[] => {
    const categoryMap: Record<string, Category> = {
      finance: {
        id: 'finance',
        name: 'Finance',
        icon: '💰',
        color: 'from-green-400 to-emerald-600',
        creators: []
      },
      food: {
        id: 'food',
        name: 'Food',
        icon: '🍳',
        color: 'from-orange-400 to-red-600',
        creators: []
      },
      fitness: {
        id: 'fitness',
        name: 'Fitness',
        icon: '💪',
        color: 'from-purple-400 to-pink-600',
        creators: []
      },
      fashion: {
        id: 'fashion',
        name: 'Fashion',
        icon: '👗',
        color: 'from-rose-400 to-pink-600',
        creators: []
      },
      tech: {
        id: 'tech',
        name: 'Tech',
        icon: '💻',
        color: 'from-indigo-400 to-blue-600',
        creators: []
      },
      wellness: {
        id: 'wellness',
        name: 'Wellness',
        icon: '🧘',
        color: 'from-blue-400 to-cyan-600',
        creators: []
      },
      lifestyle: {
        id: 'lifestyle',
        name: 'Lifestyle',
        icon: '✨',
        color: 'from-pink-400 to-teal-600',
        creators: []
      }
    };

    creators.forEach(creator => {
      // Use primary_category from backend (single category for UI display)
      const primaryCategory = (creator as any).primary_category;
      
      if (primaryCategory) {
        // Use GPT-assigned primary category
        const catLower = primaryCategory.toLowerCase();
        if (categoryMap[catLower]) {
          categoryMap[catLower].creators.push(creator);
        }
      } else {
        // Fallback: try categories array if no primary_category
        const storedCategories = (creator as any).categories || [];
        if (storedCategories.length > 0) {
          const catLower = storedCategories[0].toLowerCase();
          if (categoryMap[catLower]) {
            categoryMap[catLower].creators.push(creator);
          }
        } else {
          // Final fallback to keyword matching
          const interests = creator.profile_data?.user_style?.interests || [];
          const topics = creator.profile_data?.content_topics || [];
          const allText = [...interests, ...topics].join(' ').toLowerCase();

          if (allText.includes('finance') || allText.includes('invest') || allText.includes('money')) {
            categoryMap.finance.creators.push(creator);
          } else if (allText.includes('wellness') || allText.includes('psychology') || allText.includes('mental')) {
            categoryMap.wellness.creators.push(creator);
          } else if (allText.includes('food') || allText.includes('cook')) {
            categoryMap.food.creators.push(creator);
          } else if (allText.includes('fitness') || allText.includes('workout')) {
            categoryMap.fitness.creators.push(creator);
          } else if (allText.includes('tech') || allText.includes('technology')) {
            categoryMap.tech.creators.push(creator);
          } else if (allText.includes('fashion') || allText.includes('beauty')) {
            categoryMap.fashion.creators.push(creator);
          } else {
            categoryMap.lifestyle.creators.push(creator);
          }
        }
      }
    });

    return Object.values(categoryMap).filter(cat => cat.creators.length > 0);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
      </div>
    );
  }

  if (categories.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <svg className="w-16 h-16 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <h3 className="text-xl font-bold text-gray-900 mb-2">Unable to Load Creators</h3>
        <p className="text-gray-600 mb-4">Please make sure the backend server is running.</p>
        <button
          onClick={fetchCreators}
          className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Category Tabs */}
      <div className="flex flex-wrap gap-3 justify-center">
        <button
          onClick={() => setSelectedCategory(null)}
          className={`px-6 py-3 rounded-full font-semibold transition-all ${
            selectedCategory === null
              ? 'bg-purple-600 text-white shadow-lg'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          All Categories
        </button>
        {categories.map(category => (
          <button
            key={category.id}
            onClick={() => setSelectedCategory(category.id)}
            className={`px-6 py-3 rounded-full font-semibold transition-all ${
              selectedCategory === category.id
                ? 'bg-purple-600 text-white shadow-lg'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            {category.icon} {category.name}
          </button>
        ))}
      </div>

      {/* Category Cards */}
      <div className="space-y-8">
        {categories
          .filter(cat => !selectedCategory || cat.id === selectedCategory)
          .map(category => (
            <div key={category.id} className="space-y-4">
              <div className="flex items-center gap-3">
                <span className="text-4xl">{category.icon}</span>
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">{category.name}</h3>
                  <p className="text-gray-600">{category.creators.length} creators</p>
                </div>
              </div>

              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {category.creators.map(creator => (
                  <div
                    key={creator.user_id}
                    className="group bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-all hover:border-purple-300"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h4 className="font-bold text-lg text-gray-900">
                          @{creator.user_id}
                        </h4>
                        {creator.followers_count && (
                          <p className="text-sm text-gray-500">
                            {(creator.followers_count / 1000).toFixed(0)}K followers
                          </p>
                        )}
                      </div>
                      <div className={`w-12 h-12 rounded-full bg-gradient-to-br ${category.color} flex items-center justify-center text-white text-xl`}>
                        {category.icon}
                      </div>
                    </div>

                    {creator.profile_data?.user_style?.persona && (
                      <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                        {creator.profile_data.user_style.persona}
                      </p>
                    )}

                    {creator.profile_data?.user_style?.tone && (
                      <div className="mb-3">
                        <span className="text-xs font-semibold text-purple-600 bg-purple-50 px-2 py-1 rounded">
                          {creator.profile_data.user_style.tone.split(',')[0].trim()}
                        </span>
                      </div>
                    )}

                    {creator.profile_data?.content_topics && creator.profile_data.content_topics.length > 0 && (
                      <div className="mb-4">
                        <p className="text-xs text-gray-500 mb-1">Topics:</p>
                        <div className="flex flex-wrap gap-1">
                          {creator.profile_data.content_topics.slice(0, 2).map((topic, idx) => (
                            <span key={idx} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                              {topic.length > 20 ? topic.substring(0, 20) + '...' : topic}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="flex gap-2 mt-4">
                      <Link
                        href={`/instagram/${creator.user_id}`}
                        className="flex-1 text-center px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors text-sm font-medium"
                      >
                        View Profile
                      </Link>
                      <Link
                        href={`/style-generator?creator=${creator.user_id}`}
                        className="flex-1 text-center px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors text-sm font-medium"
                      >
                        Use Style
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
      </div>
    </div>
  );
}
