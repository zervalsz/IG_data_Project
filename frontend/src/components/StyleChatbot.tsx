"use client";

import { useState, useEffect } from "react";
import { getApiBaseUrl } from "@/lib/config";

interface Creator {
  name: string;
  topics: string[];
  style: string;
  user_id: string;
}

interface GenerateResult {
  success: boolean;
  content: string;  // Backend returns 'content', not 'generated_content'
  error: string;
}

export function StyleChatbot() {
  const [creators, setCreators] = useState<Creator[]>([]);
  const [selectedCreator, setSelectedCreator] = useState<string>("");
  const [userInput, setUserInput] = useState<string>("");
  const [generatedContent, setGeneratedContent] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  // 加载可用创作者列表
  useEffect(() => {
    const loadCreators = async () => {
      try {
        const API_URL = getApiBaseUrl();
        console.log('[StyleChatbot] API URL:', API_URL);
        // Fetch Instagram creators only
        const response = await fetch(`${API_URL}/api/style/creators?platform=instagram`);
        const data = await response.json();
        
        if (data.success) {
          setCreators(data.creators);
          // Default to first Instagram creator with data
          const defaultCreator = data.creators.find((c: Creator) => 
            c.name === "mondaypunday" || c.name === "herfirst100k"
          ) || data.creators[0];
          if (defaultCreator) {
            setSelectedCreator(defaultCreator.name);
          }
        }
      } catch (err) {
        console.error("Failed to load creators:", err);
        setError("Unable to load creator list");
      }
    };

    loadCreators();
  }, []);

  const handleGenerate = async () => {
    if (!selectedCreator || !userInput.trim()) {
      setError("Please select a creator and enter content description");
      return;
    }

    setLoading(true);
    setError("");
    setGeneratedContent("");

    try {
      const API_URL = getApiBaseUrl();
      const response = await fetch(`${API_URL}/api/style/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          creator_name: selectedCreator,
          user_input: userInput,
          platform: 'instagram', // Specify Instagram platform
        }),
      });

      const data: GenerateResult = await response.json();

      if (data.success) {
        setGeneratedContent(data.content);  // Use 'content' from backend
      } else {
        setError(data.error || "Generation failed");
      }
    } catch (err) {
      console.error("Content generation failed:", err);
      setError("Generation failed, please check if API service is running");
    } finally {
      setLoading(false);
    }
  };

  const selectedCreatorInfo = creators.find(c => c.name === selectedCreator);

  return (
    <div className="space-y-6">
      {/* 头部 */}
      <div className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm">
        <h2 className="text-2xl font-semibold text-black mb-2">
          ✍️ AI风格模仿生成器
        </h2>
        <p className="text-sm text-black/60">
          选择一位创作者，输入你想创作的内容，AI将模仿TA的风格为你生成小红书文案
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* 左侧：输入区 */}
        <div className="space-y-4">
          {/* 创作者选择 */}
          <div className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm">
            <label className="block text-sm font-semibold text-black mb-3">
              选择要模仿的创作者
            </label>
            <select
              value={selectedCreator}
              onChange={(e) => setSelectedCreator(e.target.value)}
              className="w-full rounded-lg border border-black/20 bg-white px-4 py-3 text-black focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
            >
              <option value="">-- 请选择 --</option>
              {creators.map((creator) => (
                <option key={creator.name} value={creator.name}>
                  {creator.name}
                </option>
              ))}
            </select>

            {/* 显示创作者信息 */}
            {selectedCreatorInfo && (
              <div className="mt-4 rounded-lg bg-blue-50 p-4">
                <h4 className="text-sm font-semibold text-black mb-2">
                  创作者画像
                </h4>
                <div className="space-y-1 text-sm text-black/70">
                  <p><strong>主要话题：</strong></p>
                  <div className="flex flex-wrap gap-2 mt-1">
                    {selectedCreatorInfo.topics.slice(0, 5).map((topic, idx) => (
                      <span
                        key={idx}
                        className="rounded-full bg-blue-100 px-3 py-1 text-xs text-blue-700"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* 内容输入 */}
          <div className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm">
            <label className="block text-sm font-semibold text-black mb-3">
              你想创作什么内容？
            </label>
            <textarea
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              placeholder="例如：介绍一下ChatGPT的最新功能更新..."
              rows={6}
              className="w-full rounded-lg border border-black/20 bg-white px-4 py-3 text-black placeholder:text-black/40 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 resize-none"
            />
            
            <div className="mt-4 flex items-center gap-3">
              <button
                onClick={handleGenerate}
                disabled={loading || !selectedCreator || !userInput.trim()}
                className="flex-1 rounded-lg bg-blue-600 px-6 py-3 text-white font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? "生成中..." : "🚀 生成文案"}
              </button>
            </div>

            {error && (
              <div className="mt-3 rounded-lg bg-red-50 border border-red-200 p-3 text-sm text-red-600">
                ❌ {error}
              </div>
            )}
          </div>
        </div>

        {/* 右侧：生成结果 */}
        <div className="rounded-2xl border border-black/10 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-black mb-4">
            📝 生成的文案
          </h3>
          
          {loading && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center">
                <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-blue-600 border-r-transparent"></div>
                <p className="mt-3 text-sm text-black/60">AI正在创作中...</p>
              </div>
            </div>
          )}

          {!loading && !generatedContent && (
            <div className="flex items-center justify-center py-12 text-black/40">
              <div className="text-center">
                <div className="text-4xl mb-2">✨</div>
                <p className="text-sm">生成的文案将显示在这里</p>
              </div>
            </div>
          )}

          {!loading && generatedContent && (
            <div className="space-y-4">
              <div className="rounded-lg bg-gradient-to-br from-blue-50 to-purple-50 p-6">
                <pre className="whitespace-pre-wrap font-sans text-sm text-black/80 leading-relaxed">
                  {generatedContent}
                </pre>
              </div>
              
              <button
                onClick={() => {
                  navigator.clipboard.writeText(generatedContent);
                  alert("文案已复制到剪贴板！");
                }}
                className="w-full rounded-lg border-2 border-blue-600 bg-white px-4 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 transition-colors"
              >
                📋 复制文案
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
