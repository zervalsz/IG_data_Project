"use client";

import { useState, useEffect } from "react";
import { useTranslations } from "next-intl";
import Link from "next/link";
import { CreatorUniverse } from "@/components/CreatorUniverse";
import type { CreatorNode } from "@/data/creators";

function generateMockEdges(creators: CreatorNode[]) {
  const edges: any[] = [];
  for (let i = 0; i < creators.length; i++) {
    for (let j = i + 1; j < creators.length; j++) {
      const a = creators[i];
      const b = creators[j];
      const same = a.primaryTrack === b.primaryTrack;
      const should = same ? Math.random() > 0.4 : Math.random() > 0.8;
      if (should) {
        edges.push({
          source: a.id,
          target: b.id,
          weight: parseFloat((0.3 + Math.random() * 0.5).toFixed(2)),
          types: { keyword: 0, audience: 0, style: 0 },
        });
      }
    }
  }
  return edges;
}

export function HomePage() {
  const t = useTranslations("home");
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [creatorsData, setCreatorsData] = useState<CreatorNode[]>([]);
  const [edgesData, setEdgesData] = useState<any[]>([]);
  const [clustersData, setClustersData] = useState<Record<string, string[]>>({});

  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 400);
    };
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    // fetch creators from API route (defensive: handle non-JSON or error HTML responses)
    let mounted = true;
    (async () => {
      try {
        // Fetch Instagram creators directly from FastAPI backend
        // Construct backend URL for GitHub Codespaces
        let apiBaseUrl = 'http://localhost:5001';
        if (typeof window !== 'undefined' && window.location.hostname.includes('github.dev')) {
          apiBaseUrl = window.location.origin.replace('-3000.', '-5001.');
        }
        console.log('[HomePage] API URL:', apiBaseUrl);
        const r = await fetch(`${apiBaseUrl}/api/creators/network?platform=instagram`);
        if (!mounted) return;

          const contentType = r.headers.get('content-type') || '';
          if (!r.ok) {
            console.warn('Creators API not OK', r.status);
            return;
          }

          if (!contentType.includes('application/json')) {
            const txt = await r.text();
            console.warn('Creators API returned non-json response', txt.slice(0, 500));
            return;
          }

          const json = await r.json();
          console.log('[HomePage] Loaded Instagram creators data:', json);
          if (!json) return;

          // The network API returns creators and edges directly
          if (Array.isArray(json.creators)) setCreatorsData(json.creators);
          else setCreatorsData([]);

          if (Array.isArray(json.edges)) setEdgesData(json.edges);
          else if (Array.isArray(json.creators)) setEdgesData(generateMockEdges(json.creators));

          // trackClusters is not in the network response, so leave empty
          setClustersData({});

          // trendingKeywordGroups is optional; frontend currently doesn't store it here
      } catch (err) {
        console.error('[HomePage] Failed to load creators', err);
      }
    })();
    return () => { mounted = false };
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  return (
    <main className="bg-[url('https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=1400&q=80')] bg-cover bg-fixed bg-center bg-no-repeat">
      <div className="backdrop-blur-sm">
        <section className="container mx-auto px-6 pb-16 pt-12">
          <div className="rounded-3xl bg-white/85 p-10 shadow-lg">
            <h1 className="text-4xl font-semibold text-black md:text-5xl">
              {t("hero.title")}
            </h1>
            <p className="mt-4 max-w-3xl text-lg text-black/70">
              {t("hero.subtitle")}
            </p>
            
            {/* 新功能入口 */}
            <div className="mt-6 flex flex-wrap gap-4">
              <Link
                href="/zh/style-generator"
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-700 transition-colors"
              >
                ✨ AI风格生成器
              </Link>
              
              <Link
                href="/instagram"
                className="inline-flex items-center gap-2 rounded-lg bg-gradient-to-r from-purple-600 to-pink-600 px-6 py-3 text-white font-medium hover:from-purple-700 hover:to-pink-700 transition-colors"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  fill="currentColor"
                  viewBox="0 0 24 24"
                  className="w-5 h-5"
                >
                  <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" />
                </svg>
                Instagram Creators
              </Link>
            </div>
          </div>
        </section>

        <section className="container mx-auto px-6 pb-16">
          <div className="rounded-3xl bg-white/90 p-10 shadow-lg">
            <header className="mb-8">
              <h2 className="text-2xl font-semibold text-black">{t("network.title")}</h2>
              <p className="mt-2 max-w-2xl text-sm text-black/60">{t("network.description")}</p>
            </header>
            <CreatorUniverse
              creators={creatorsData}
              edges={edgesData}
              clusters={clustersData}
              trendingKeywords={[]}
            />
          </div>
        </section>
      </div>
      
      {/* 返回顶部按钮 */}
      {showScrollTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-8 right-8 z-50 flex h-12 w-12 items-center justify-center rounded-full bg-blue-600 text-white shadow-lg transition-all hover:bg-blue-700 hover:scale-110 active:scale-95"
          aria-label="返回顶部"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={2.5}
            stroke="currentColor"
            className="h-6 w-6"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M4.5 15.75l7.5-7.5 7.5 7.5"
            />
          </svg>
        </button>
      )}
    </main>
  );
}
