"use client";

import { useState } from "react";
import Link from "next/link";
import { AccountCategories } from "@/components/AccountCategories";

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
          <h2 className="text-3xl font-bold text-center mb-12">How It Works</h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-white/20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                1
              </div>
              <h3 className="text-xl font-semibold mb-2">Explore Creators</h3>
              <p className="text-purple-100">
                Browse creators by category and learn about their unique style
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-white/20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                2
              </div>
              <h3 className="text-xl font-semibold mb-2">Choose Your Path</h3>
              <p className="text-purple-100">
                Pick style-based generation or trend-optimized content
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-white/20 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
                3
              </div>
              <h3 className="text-xl font-semibold mb-2">Generate Content</h3>
              <p className="text-purple-100">
                Get AI-powered Instagram captions and hashtags instantly
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* What We Offer Section */}
      <section className="container mx-auto px-6 py-12">
        <div className="bg-white rounded-3xl shadow-xl p-10">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-8">
            What Can You Do Here?
          </h2>
          
          <div className="grid md:grid-cols-2 gap-8 mt-12">
            {/* Path 1: Style-Based Generation */}
            <Link 
              href="/style-generator"
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

      {/* Explore Creators Section */}
      <section id="creators" className="container mx-auto px-6 py-12 pb-20">
        <div className="bg-white rounded-3xl shadow-xl p-10">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-4">
            Explore Our Creators
          </h2>
          <p className="text-center text-gray-600 mb-10">
            Browse Instagram creators across different categories to understand their style and content
          </p>
          
          <AccountCategories />
        </div>
      </section>
    </main>
  );
}
