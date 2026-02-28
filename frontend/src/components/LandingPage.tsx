"use client";

import { useState } from "react";
import { Link } from "@/navigation";

export function LandingPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      {/* Hero Section */}
      <section className="container mx-auto px-6 py-16">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent">
            Instagram Creator Content Lab
          </h1>
          <p className="mt-6 text-xl text-gray-700 max-w-3xl mx-auto">
            Discover top Instagram creators across different niches and generate content powered by AI
          </p>
        </div>
      </section>

      {/* How It Works */}
      <section className="container mx-auto px-6 py-12">
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-3xl shadow-xl p-10 text-white">
          <h2 className="text-3xl font-bold text-center mb-4">How It Works</h2>
          <p className="text-center text-purple-100 mb-12 max-w-2xl mx-auto">
            Choose your path based on what you need: mimic a specific creator's style or generate trending content for your niche
          </p>
          
          <div className="grid md:grid-cols-2 gap-8">
            {/* Style Generator Track */}
            <div className="bg-white/10 rounded-2xl p-6 backdrop-blur-sm border border-white/20">
              <div className="flex items-center justify-center gap-3 mb-6">
                <span className="text-3xl">🎨</span>
                <h3 className="text-2xl font-bold">Style Generator</h3>
              </div>
              
              <div className="bg-blue-500/30 rounded-lg p-4 mb-6">
                <p className="text-sm font-semibold mb-1">Best for:</p>
                <p className="text-sm text-blue-100">
                  Matching a specific creator's voice, tone, and writing style
                </p>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="bg-white/20 w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 font-bold">1</div>
                  <div>
                    <p className="font-semibold">Explore Creators</p>
                    <p className="text-sm text-purple-100">Browse by category and learn about their style</p>
                  </div>
                </div>
                
                <div className="flex items-center justify-center">
                  <svg className="w-6 h-6 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </div>
                
                <div className="flex items-start gap-3">
                  <div className="bg-white/20 w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 font-bold">2</div>
                  <div>
                    <p className="font-semibold">Select a Creator</p>
                    <p className="text-sm text-purple-100">Pick one whose style resonates with you</p>
                  </div>
                </div>
                
                <div className="flex items-center justify-center">
                  <svg className="w-6 h-6 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </div>
                
                <div className="flex items-start gap-3">
                  <div className="bg-white/20 w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 font-bold">3</div>
                  <div>
                    <p className="font-semibold">Generate Content</p>
                    <p className="text-sm text-purple-100">Enter your topic and get AI-powered captions in their style</p>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Trend Generator Track */}
            <div className="bg-white/10 rounded-2xl p-6 backdrop-blur-sm border border-white/20">
              <div className="flex items-center justify-center gap-3 mb-6">
                <span className="text-3xl">📊</span>
                <h3 className="text-2xl font-bold">Trend Generator</h3>
              </div>
              
              <div className="bg-orange-500/30 rounded-lg p-4 mb-6">
                <p className="text-sm font-semibold mb-1">Best for:</p>
                <p className="text-sm text-orange-100">
                  Creating engagement-optimized content based on trending topics
                </p>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="bg-white/20 w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 font-bold">1</div>
                  <div>
                    <p className="font-semibold">Choose Your Niche</p>
                    <p className="text-sm text-purple-100">Select a category that matches your content</p>
                  </div>
                </div>
                
                <div className="flex items-center justify-center">
                  <svg className="w-6 h-6 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </div>
                
                <div className="flex items-start gap-3">
                  <div className="bg-white/20 w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 font-bold">2</div>
                  <div>
                    <p className="font-semibold">Generate Trending Content</p>
                    <p className="text-sm text-purple-100">Get captions optimized for maximum engagement</p>
                  </div>
                </div>
                
                <div className="h-[88px] flex items-center justify-center">
                  <p className="text-sm text-white/60 italic">Quick & direct path</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* What We Offer Section */}
      <section className="container mx-auto px-6 py-12 pb-20">
        <div className="bg-white rounded-3xl shadow-xl p-10">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">
            What Can You Do Here?
          </h2>
          
          <div className="grid md:grid-cols-2 gap-8 mt-12">
            {/* Path 1: Style-Based Generation */}
            <Link 
              href="/explore-creators"
              className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 p-8 text-white transition-all hover:shadow-2xl hover:scale-105"
            >
              <div className="relative z-10">
                <div className="text-5xl mb-4">🎨</div>
                <h3 className="text-2xl font-bold mb-4">Style-Based Generator</h3>
                <p className="text-blue-100 mb-6">
                  Pick a creator, give a topic, and we'll generate a post in their unique style
                </p>
                <div className="flex items-center gap-2 text-sm font-semibold">
                  <span>Start Creating</span>
                  <svg className="w-5 h-5 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </div>
              </div>
              <div className="absolute inset-0 bg-gradient-to-br from-blue-400 to-purple-500 opacity-0 group-hover:opacity-100 transition-opacity" />
            </Link>

            {/* Path 2: Trend-Based Generation */}
            <Link 
              href="/trend-generator"
              className="group relative overflow-hidden rounded-2xl bg-gradient-to-br from-pink-500 to-orange-500 p-8 text-white transition-all hover:shadow-2xl hover:scale-105"
            >
              <div className="relative z-10">
                <div className="text-5xl mb-4">📊</div>
                <h3 className="text-2xl font-bold mb-4">Trend-Based Generator</h3>
                <p className="text-pink-100 mb-6">
                  Pick a niche, and we'll generate content optimized for engagement based on trending posts
                </p>
                <div className="flex items-center gap-2 text-sm font-semibold">
                  <span>Discover Trends</span>
                  <svg className="w-5 h-5 group-hover:translate-x-2 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </div>
              </div>
              <div className="absolute inset-0 bg-gradient-to-br from-pink-400 to-orange-400 opacity-0 group-hover:opacity-100 transition-opacity" />
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
