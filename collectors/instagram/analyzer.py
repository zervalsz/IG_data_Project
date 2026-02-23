#!/usr/bin/env python3
"""
Instagram Data Analyzer
Analyzes Instagram user data using ChatGPT or Gemini API and generates embeddings
"""

import os
import json
from typing import Dict, List, Any, Optional
import time
import requests
# Try to import FlagEmbedding optionally; if unavailable, embeddings step will be skipped
try:
    from FlagEmbedding import FlagModel
    FLAG_EMBEDDING_AVAILABLE = True
except Exception as e:
    FlagModel = None
    FLAG_EMBEDDING_AVAILABLE = False
    print("⚠️  Warning: FlagEmbedding not available; local embeddings will be skipped.\n  Reason:", e)


class IGAnalyzer:
    """Instagram data analyzer using ChatGPT or Gemini"""
    
    def __init__(self, provider: str = "openai", embedding_model: Optional[FlagModel] = None):
        """
        Initialize the analyzer
        
        Args:
            provider: "openai" or "gemini"
            embedding_model: FlagModel instance for generating embeddings
        """
        self.provider = provider.lower()
        self.embedding_model = embedding_model
        
        if self.provider == "openai":
            self.api_key = os.environ.get("OPENAI_API_KEY")
            self.model = os.environ.get("CHAT_MODEL", "gpt-4o-mini")
            self.api_url = "https://api.openai.com/v1/chat/completions"
            
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables")
                
        elif self.provider == "gemini":
            self.api_key = os.environ.get("GEMINI_API_KEY")
            self.model = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
            self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
            
            if not self.api_key:
                raise ValueError("GEMINI_API_KEY not found in environment variables")
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def build_analysis_prompt(self, user_info: Dict[str, Any], posts: List[Dict[str, Any]]) -> str:
        """
        Build a prompt for analyzing Instagram user profile
        
        Args:
            user_info: User profile information
            posts: List of user's posts
            
        Returns:
            Analysis prompt string
        """
        # Extract user information
        username = user_info.get('username', 'Unknown')
        bio = user_info.get('bio', '')
        follower_count = user_info.get('followers', 0)
        following_count = user_info.get('following', 0)
        posts_count = user_info.get('posts_count', 0)
        
        # Build posts summary
        posts_summary = []
        for post in posts[:20]:  # Limit to 20 recent posts
            caption = post.get('caption', '')
            likes = post.get('likes', 0)
            comments = post.get('comments', 0)
            hashtags = post.get('hashtags', [])
            
            if isinstance(hashtags, list):
                hashtags_str = ' '.join(hashtags)
            else:
                hashtags_str = str(hashtags)
            
            post_summary = f"Caption: {caption}\nLikes: {likes}, Comments: {comments}\nHashtags: {hashtags_str}"
            posts_summary.append(post_summary)
        
        posts_text = "\n\n".join(posts_summary) if posts_summary else "No posts available"
        
        prompt = f"""Analyze this Instagram user's profile and content to create a comprehensive profile.

User Information:
- Username: {username}
- Bio: {bio}
- Followers: {follower_count}
- Following: {following_count}
- Total Posts: {posts_count}

Recent Posts (up to 20):
{posts_text}

Please provide analysis in JSON format with the following structure:
{{
    "user_style": {{
        "persona": "2-3 sentence description of the user's persona",
        "tone": "Words describing their writing/posting tone",
        "interests": ["interest1", "interest2", "interest3"]
    }},
    "content_topics": ["topic1", "topic2", "topic3"],
    "primary_category": "PrimaryCategory",
    "categories": ["PrimaryCategory", "SecondaryCategory"],
    "posting_pattern": {{
        "frequency": "daily/weekly/monthly/irregular",
        "best_time_to_post": "estimated best posting time",
        "content_mix": ["type1", "type2"]
    }},
    "audience_type": ["audience_segment1", "audience_segment2"],
    "engagement_style": "description of how they engage with followers",
    "brand_fit": ["brand_type1", "brand_type2"]
}}

CATEGORY RULES:
1. "primary_category": Choose the ONE category that best represents this creator's main focus
2. "categories": Array with primary category first, then optionally ONE secondary category if they regularly post about it (must be 20%+ of content)

Available categories:
- Finance (money, investing, budgeting, wealth building, financial education)
- Food (cooking, recipes, meals, restaurants, culinary content)
- Fitness (workout routines, sports, exercise, physical training)
- Fashion (style, outfits, clothing, beauty, trends)
- Tech (technology, software, digital tools, AI, gadgets)
- Wellness (mental health professionals, therapists, mindfulness coaches, psychology)
- Celebrity (famous public figures, actors, athletes, musicians, highly influential personalities with millions of followers)
- Lifestyle (daily vlogs, general entertainment, life moments - use ONLY if no other category fits)

IMPORTANT: 
- Be STRICT with category assignment. Only assign Wellness if they are mental health professionals.
- Use Celebrity for well-known public figures, entertainers, or highly influential personalities.
- Lifestyle is a catch-all - only use if content doesn't fit other categories.
- Most creators should have only 1 category. Add secondary ONLY if truly significant.

Return ONLY valid JSON, no additional text."""
        
        return prompt
    
    def call_openai(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call OpenAI API with retry logic for rate limits"""
        max_retries = 5
        backoff = 1  # Start with 1 second
        
        for attempt in range(1, max_retries + 1):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert social media analyst. Return only valid JSON format responses."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
                
                response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()
                
                # Parse JSON from response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    return json.loads(json_str)
                
                return None
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 and attempt < max_retries:
                    # Rate limited - wait and retry
                    print(f"⚠️  OpenAI Rate Limited (429). Attempt {attempt}/{max_retries}. Waiting {backoff}s before retry...")
                    time.sleep(backoff)
                    backoff *= 2  # Exponential backoff
                    continue
                else:
                    # Not a 429 or final attempt
                    print(f"❌ OpenAI API Error (HTTP {e.response.status_code}): {e}")
                    return None
            except Exception as e:
                print(f"❌ OpenAI API Error: {e}")
                return None
        
        print(f"❌ OpenAI API: Max retries ({max_retries}) exceeded")
        return None
    
    def call_gemini(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call Google Gemini API with retry logic for rate limits"""
        max_retries = 5
        backoff = 1  # Start with 1 second
        
        for attempt in range(1, max_retries + 1):
            try:
                headers = {
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": prompt
                                }
                            ]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 1000
                    }
                }
                
                url = f"{self.api_url}?key={self.api_key}"
                response = requests.post(url, json=payload, headers=headers, timeout=30)
                response.raise_for_status()
                
                result = response.json()
                content = result['candidates'][0]['content']['parts'][0]['text'].strip()
                
                # Parse JSON from response
                json_start = content.find('{')
                json_end = content.rfind('}') + 1
                if json_start >= 0 and json_end > json_start:
                    json_str = content[json_start:json_end]
                    return json.loads(json_str)
                
                return None
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429 and attempt < max_retries:
                    # Rate limited - wait and retry
                    print(f"⚠️  Gemini Rate Limited (429). Attempt {attempt}/{max_retries}. Waiting {backoff}s before retry...")
                    time.sleep(backoff)
                    backoff *= 2  # Exponential backoff
                    continue
                else:
                    # Not a 429 or final attempt
                    print(f"❌ Gemini API Error (HTTP {e.response.status_code}): {e}")
                    return None
            except Exception as e:
                print(f"❌ Gemini API Error: {e}")
                return None
        
        print(f"❌ Gemini API: Max retries ({max_retries}) exceeded")
        return None
    
    def analyze_user(self, user_info: Dict[str, Any], posts: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Analyze Instagram user profile
        
        Args:
            user_info: User profile information
            posts: List of user's posts
            
        Returns:
            Analysis result with embeddings
        """
        print(f"\n🤖 Analyzing user: {user_info.get('username', 'Unknown')} using {self.provider}...")
        
        # Build prompt
        prompt = self.build_analysis_prompt(user_info, posts)
        
        # Call API based on provider
        if self.provider == "openai":
            analysis = self.call_openai(prompt)
        else:
            analysis = self.call_gemini(prompt)
        
        if not analysis:
            print(f"❌ Failed to analyze user")
            return None
        
        # Generate embedding from user_style if embedding model is available
        if self.embedding_model:
            try:
                user_style_text = analysis.get('user_style', {})
                if user_style_text:
                    # Convert user_style dict to text for embedding
                    persona = user_style_text.get('persona', '')
                    tone = user_style_text.get('tone', '')
                    interests = user_style_text.get('interests', [])
                    interests_text = ', '.join(interests) if isinstance(interests, list) else str(interests)
                    
                    text_for_embedding = f"{persona} {tone} {interests_text}"
                    
                    embedding = self.embedding_model.encode(text_for_embedding)
                    analysis['user_style_embedding'] = embedding.tolist()
                    print(f"✅ Generated embedding (dimension: {len(embedding)})")
            except Exception as e:
                print(f"⚠️  Warning: Failed to generate embedding: {e}")
        
        return analysis


def analyze_user_profile(user_info: Dict[str, Any], posts: List[Dict[str, Any]], 
                        embedding_model: Optional[FlagModel] = None) -> Optional[Dict[str, Any]]:
    """
    Convenience function to analyze user profile
    
    Args:
        user_info: User profile information
        posts: List of user's posts
        embedding_model: FlagModel instance for embeddings
        
    Returns:
        Analysis result
    """
    provider = os.environ.get("AI_PROVIDER", "openai")
    analyzer = IGAnalyzer(provider=provider, embedding_model=embedding_model)
    return analyzer.analyze_user(user_info, posts)
