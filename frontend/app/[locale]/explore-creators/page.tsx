"use client";

import { Link } from "@/navigation";
import { AccountCategories } from "@/components/AccountCategories";

export default function ExploreCreatorsPage() {
  return (
    <main className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      {/* Header Section */}
      <section className="container mx-auto px-6 py-12">
        <div className="mb-8">
          <Link href="/" className="inline-flex items-center text-purple-600 hover:text-purple-700">
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Back to Home
          </Link>
        </div>
        <div className="text-center">
          <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-purple-600 via-pink-600 to-blue-600 bg-clip-text text-transparent">
            Explore Our Creators
          </h1>
          <p className="mt-4 text-lg text-gray-700 max-w-2xl mx-auto">
            Browse Instagram creators across different categories and select one to generate content in their unique style
          </p>
          
          {/* Skip Link */}
          <div className="mt-6">
            <Link 
              href="/style-generator"
              className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-purple-600 transition-colors group"
            >
              <span>Skip and go directly to style generator</span>
              <svg className="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
              <span className="text-xs text-gray-400">(not recommended)</span>
            </Link>
          </div>
        </div>
      </section>

      {/* Creators Grid */}
      <section className="container mx-auto px-6 pb-20">
        <div className="bg-white rounded-3xl shadow-xl p-10">
          <AccountCategories />
        </div>
      </section>
    </main>
  );
}
