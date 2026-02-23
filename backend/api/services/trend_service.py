"""
Trend-based Content Generation Service
基于趋势数据的内容生成服务
"""
import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import numpy as np
from openai import OpenAI

logger = logging.getLogger(__name__)


class TrendService:
    """趋势内容生成服务"""
    
    # Category mappings (fallback for keyword-based categorization)
    CATEGORY_KEYWORDS = {
        'Finance': ['finance', 'invest', 'money', 'debt', 'wealth', 'budget'],
        'Wellness': ['mental', 'wellness', 'psychology', 'trauma', 'health', 'mindfulness'],
        'Food': ['food', 'cook', 'recipe', 'kitchen', 'meal'],
        'Fitness': ['fitness', 'workout', 'sport', 'exercise', 'training'],
        'Fashion': ['fashion', 'style', 'outfit', 'clothing', 'trend'],
        'Tech': ['tech', 'technology', 'software', 'coding', 'ai', 'digital'],
        'Celebrity': ['celebrity', 'famous', 'public figure', 'influencer', 'star'],
        'Lifestyle': []  # catch-all for others
    }
    
    def __init__(self):
        """初始化服务"""
        from database.repositories import (
            UserProfileRepository,
            UserSnapshotRepository,
            PostEmbeddingRepository
        )
        
        self.profile_repo = UserProfileRepository()
        self.snapshot_repo = UserSnapshotRepository()
        self.post_repo = PostEmbeddingRepository()
        
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY环境变量未设置")
        self.client = OpenAI(api_key=api_key)
    
    def categorize_creator(self, profile: Dict[str, Any]) -> str:
        """
        将创作者分类到某个类别（基于关键词匹配的后备方案）
        
        Args:
            profile: 创作者档案
            
        Returns:
            类别名称
        """
        # Extract interests and topics
        interests = profile.get('profile_data', {}).get('user_style', {}).get('interests', [])
        topics = profile.get('profile_data', {}).get('content_topics', [])
        
        # Combine all text
        all_text = ' '.join(interests + topics).lower()
        
        # Check each category
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            if category == 'Lifestyle':
                continue  # Skip Lifestyle (it's the default)
            
            if any(kw in all_text for kw in keywords):
                return category
        
        return 'Lifestyle'
    
    def get_creators_by_category(self, category: str, platform: str = "instagram") -> List[Dict[str, Any]]:
        """
        获取指定类别的创作者（使用primary_category字段）
        
        Args:
            category: 类别名称 (Lifestyle, Fashion, Food, Fitness, Tech, Wellness, Finance, Celebrity)
            platform: 平台
            
        Returns:
            创作者列表
        """
        # Get all profiles
        profiles = self.profile_repo.get_all_profiles(platform=platform)
        
        # Filter by primary_category
        categorized = []
        for profile in profiles:
            primary_category = profile.get('profile_data', {}).get('primary_category')
            # Normalize category names (case-insensitive match)
            # Skip profiles with None primary_category
            if primary_category and primary_category.lower() == category.lower():
                categorized.append(profile)
        
        # Fallback: if no profiles found with stored categories, use old keyword matching
        if not categorized:
            logger.warning(f"No profiles with stored category '{category}', falling back to keyword matching")
            for profile in profiles:
                if self.categorize_creator(profile) == category.lower():
                    categorized.append(profile)
        
        return categorized
    
    def analyze_posts(self, creators: List[Dict[str, Any]], platform: str = "instagram") -> Dict[str, Any]:
        """
        分析创作者的帖子数据，使用实际粉丝数计算真实的互动率
        
        Args:
            creators: 创作者列表
            platform: 平台
            
        Returns:
            分析结果
        """
        all_posts = []
        creator_followers = {}  # Store follower counts for each creator
        
        # Collect posts and follower counts from all creators
        for creator in creators:
            user_id = creator.get('user_id')
            
            # Get follower count from raw_api_responses
            follower_count = self.profile_repo.get_follower_count(user_id, platform)
            if follower_count:
                creator_followers[user_id] = follower_count
            
            # Try to get from post_embeddings first (has more detailed data)
            posts = self.post_repo.get_by_user_id(user_id, platform=platform)
            
            if posts:
                # Tag each post with user_id for follower lookup
                for post in posts:
                    post['_user_id'] = user_id
                all_posts.extend(posts)
            else:
                # Fallback to snapshots
                snapshot = self.snapshot_repo.get_by_user_id(user_id, platform=platform)
                if snapshot and 'notes' in snapshot:
                    for post in snapshot['notes']:
                        post['_user_id'] = user_id
                    all_posts.extend(snapshot['notes'])
        
        if not all_posts:
            return {
                'total_posts': 0,
                'avg_likes': 0,
                'avg_comments': 0,
                'avg_engagement': 0,
                'engagement_rate': 0.0,
                'top_posts': [],
                'common_topics': []
            }
        
        # Calculate metrics
        likes = [p.get('like_count', p.get('liked_count', 0)) for p in all_posts]
        comments = [p.get('comment_count', 0) for p in all_posts]
        
        # Calculate engagement rate (likes + comments) / follower_count for each post
        engagement_rates = []
        for post in all_posts:
            user_id = post.get('_user_id')
            if user_id and user_id in creator_followers:
                follower_count = creator_followers[user_id]
                like_count = post.get('like_count', post.get('liked_count', 0))
                comment_count = post.get('comment_count', 0)
                
                # Engagement rate as percentage
                rate = ((like_count + comment_count) / follower_count) * 100
                engagement_rates.append(rate)
        
        # Calculate average engagement rate
        avg_engagement_rate = np.mean(engagement_rates) if engagement_rates else 0
        
        # Calculate raw totals
        engagements = [l + c for l, c in zip(likes, comments)]
        
        # Sort posts by engagement
        posts_with_engagement = [
            {**post, 'engagement': eng}
            for post, eng in zip(all_posts, engagements)
        ]
        posts_with_engagement.sort(key=lambda x: x['engagement'], reverse=True)
        
        # Get top performing posts
        top_posts = posts_with_engagement[:10]
        
        # Extract common themes from top posts
        top_captions = [
            p.get('caption', p.get('desc', p.get('title', '')))
            for p in top_posts
            if p.get('caption') or p.get('desc') or p.get('title')
        ]
        
        # Calculate raw averages from established creators
        raw_avg_likes = int(np.mean(likes)) if likes else 0
        raw_avg_comments = int(np.mean(comments)) if comments else 0
        raw_avg_engagement = int(np.mean(engagements)) if engagements else 0
        
        # Calculate engagement ratio (likes:comments)
        engagement_ratio = round(raw_avg_likes / raw_avg_comments, 1) if raw_avg_comments > 0 else 274.5
        
        # Calculate expected engagement for a target account size (e.g., 10K followers)
        target_followers = 10000
        total_expected_engagement = int((avg_engagement_rate / 100) * target_followers) if avg_engagement_rate > 0 else 0
        
        # Split engagement based on actual like:comment ratio
        # If ratio is 274.5:1, then likes = 274.5/(274.5+1) = 99.6% of engagement
        if engagement_ratio > 0:
            comment_fraction = 1 / (engagement_ratio + 1)
            like_fraction = engagement_ratio / (engagement_ratio + 1)
            expected_comments = int(total_expected_engagement * comment_fraction)
            expected_likes = total_expected_engagement - expected_comments
        else:
            expected_likes = total_expected_engagement
            expected_comments = 0
        
        # Extract evidence from top performing posts
        evidence = self._extract_evidence(top_posts[:5])
        
        return {
            'total_posts': len(all_posts),
            # Projected metrics for ~10K follower account
            'avg_likes': expected_likes,
            'avg_comments': expected_comments,
            'avg_engagement': expected_likes + expected_comments,
            # Raw metrics from established creators
            'raw_avg_likes': raw_avg_likes,
            'raw_avg_comments': raw_avg_comments,
            'raw_avg_engagement': raw_avg_engagement,
            # Engagement rate as percentage
            'engagement_rate': round(avg_engagement_rate, 2),
            # Engagement ratio (likes:comments ratio)
            'engagement_ratio': engagement_ratio,
            'top_posts': top_posts[:5],  # Top 5 for analysis
            'top_captions': top_captions[:10],
            # Evidence extracted from top posts
            'evidence': evidence
        }
    
    def _extract_evidence(self, top_posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Extract evidence from top-performing posts
        
        Args:
            top_posts: List of top performing posts
            
        Returns:
            Evidence dictionary with keywords, hooks, hashtags, and samples
        """
        import re
        from collections import Counter
        
        captions = []
        all_hashtags = []
        hooks = []
        
        for post in top_posts:
            caption = post.get('caption', post.get('desc', post.get('title', '')))
            if caption:
                captions.append(caption)
                
                # Extract hooks (first sentence or first 100 chars)
                first_line = caption.split('\n')[0].strip()
                if len(first_line) > 10:
                    hooks.append(first_line[:150] + ('...' if len(first_line) > 150 else ''))
                
                # Extract hashtags
                hashtags = re.findall(r'#\w+', caption)
                all_hashtags.extend(hashtags)
        
        # Extract keywords (simple approach - most common words)
        all_text = ' '.join(captions).lower()
        # Remove common stopwords
        stopwords = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their', 'what', 'when', 'where', 'who', 'which',
            'how', 'why', 'all', 'some', 'any', 'each', 'every', 'both', 'few', 'more', 'most', 'other', 'such', 'only', 'own', 'same', 'so', 'than',
            'too', 'very', 'just', 'from', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again', 'further',
            'then', 'once', 'here', 'there', 'about', 'because', 'much', 'many', 'part', 'way', 'ways', 'get', 'getting', 'got', 'make', 'making',
            'made', 'take', 'taking', 'took', 'come', 'coming', 'came', 'give', 'giving', 'gave', 'know', 'knowing', 'knew', 'think', 'thinking',
            'thought', 'see', 'seeing', 'saw', 'want', 'wanting', 'wanted', 'use', 'using', 'used', 'find', 'finding', 'found', 'tell', 'telling',
            'told', 'ask', 'asking', 'asked', 'work', 'working', 'worked', 'seem', 'seeming', 'seemed', 'feel', 'feeling', 'felt', 'try', 'trying',
            'tried', 'leave', 'leaving', 'left', 'call', 'calling', 'called', 'keep', 'keeping', 'kept', 'let', 'letting', 'begin', 'beginning',
            'began', 'help', 'helping', 'helped', 'show', 'showing', 'showed', 'hear', 'hearing', 'heard', 'play', 'playing', 'played', 'run',
            'running', 'ran', 'move', 'moving', 'moved', 'live', 'living', 'lived', 'believe', 'believing', 'believed', 'bring', 'bringing',
            'brought', 'happen', 'happening', 'happened', 'write', 'writing', 'wrote', 'provide', 'providing', 'provided', 'sit', 'sitting',
            'sat', 'stand', 'standing', 'stood', 'lose', 'losing', 'lost', 'pay', 'paying', 'paid', 'meet', 'meeting', 'met', 'include',
            'including', 'included', 'continue', 'continuing', 'continued', 'set', 'setting', 'learn', 'learning', 'learned', 'change',
            'changing', 'changed', 'lead', 'leading', 'led', 'understand', 'understanding', 'understood', 'watch', 'watching', 'watched',
            'follow', 'following', 'followed', 'stop', 'stopping', 'stopped', 'create', 'creating', 'created', 'speak', 'speaking', 'spoke',
            'read', 'reading', 'allow', 'allowing', 'allowed', 'add', 'adding', 'added', 'spend', 'spending', 'spent', 'grow', 'growing',
            'grew', 'open', 'opening', 'opened', 'walk', 'walking', 'walked', 'win', 'winning', 'won', 'offer', 'offering', 'offered',
            'remember', 'remembering', 'remembered', 'love', 'loving', 'loved', 'consider', 'considering', 'considered', 'appear',
            'appearing', 'appeared', 'buy', 'buying', 'bought', 'wait', 'waiting', 'waited', 'serve', 'serving', 'served', 'die',
            'dying', 'died', 'send', 'sending', 'sent', 'expect', 'expecting', 'expected', 'build', 'building', 'built', 'stay',
            'staying', 'stayed', 'fall', 'falling', 'fell', 'cut', 'cutting', 'reach', 'reaching', 'reached', 'kill', 'killing',
            'killed', 'remain', 'remaining', 'remained', 'suggest', 'suggesting', 'suggested', 'raise', 'raising', 'raised',
            'pass', 'passing', 'passed', 'sell', 'selling', 'sold', 'require', 'requiring', 'required', 'report', 'reporting',
            'reported', 'decide', 'deciding', 'decided', 'pull', 'pulling', 'pulled'
        }
        words = re.findall(r'\b[a-z]{4,}\b', all_text)  # Words 4+ letters
        filtered_words = [w for w in words if w not in stopwords and not w.startswith('#')]
        word_counts = Counter(filtered_words)
        top_keywords = [word for word, count in word_counts.most_common(10)]
        
        # Get most common hashtags
        hashtag_counts = Counter(all_hashtags)
        top_hashtags = [tag for tag, count in hashtag_counts.most_common(10)]
        
        # Analyze hooks with GPT to explain why they're successful
        hooks_with_explanations = self._analyze_hooks(hooks[:3])
        
        return {
            'keywords': top_keywords,
            'hooks': hooks_with_explanations,  # Hooks with explanations
            'hashtags': top_hashtags
        }
    
    def _analyze_hooks(self, hooks: List[str]) -> List[Dict[str, str]]:
        """
        Analyze why each hook is successful using GPT
        
        Args:
            hooks: List of hook texts
            
        Returns:
            List of dicts with 'text' and 'reason' keys
        """
        if not hooks:
            return []
        
        try:
            prompt = f"""Analyze these successful Instagram post hooks and explain in ONE SHORT SENTENCE (10-15 words max) why each is effective.

Hooks:
{chr(10).join([f'{i+1}. "{hook}"' for i, hook in enumerate(hooks)])}

For each hook, provide a brief reason focusing on ONE key technique (e.g., "Uses storytelling", "Creates curiosity", "References specific location", "Relatable moment", "Surprising statement", etc.)

Return as JSON array:
[
  {{"hook": "hook text 1", "reason": "one-sentence explanation"}},
  {{"hook": "hook text 2", "reason": "one-sentence explanation"}},
  ...
]

Keep explanations concise and actionable."""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a social media expert analyzing successful content hooks. Return ONLY valid JSON, no markdown."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            
            import json
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
                content = content.strip()
            
            result = json.loads(content)
            return result
            
        except Exception as e:
            print(f"⚠️  Failed to analyze hooks: {e}")
            # Fallback to hooks without explanations
            return [{'hook': hook, 'reason': ''} for hook in hooks]
    
    def build_trend_prompt(
        self,
        category: str,
        analysis: Dict[str, Any],
        platform: str = "instagram",
        tone: str = "engaging",
        length: str = "medium",
        format: str = "post"
    ) -> str:
        """
        构建趋势生成提示词
        
        Args:
            category: 类别
            analysis: 分析数据
            platform: 平台
            tone: 语气
            length: 长度
            format: 格式
            
        Returns:
            提示词
        """
        category_names = {
            'Finance': 'Finance & Money',
            'Wellness': 'Mental Health & Wellness',
            'Food': 'Food & Cooking',
            'Fitness': 'Fitness & Sports',
            'Fashion': 'Fashion & Style',
            'Tech': 'Technology & Digital',
            'Celebrity': 'Celebrity & Public Figures',
            'Lifestyle': 'Lifestyle & Entertainment'
        }
        
        category_name = category_names.get(category, category)
        
        # Build context from top posts
        top_examples = "\n".join([
            f"- {caption[:150]}..."
            for caption in analysis.get('top_captions', [])[:5]
            if caption
        ])
        
        prompt = f"""Based on analysis of {analysis['total_posts']} high-performing posts in the {category_name} category on Instagram:

ENGAGEMENT BENCHMARKS:
- Average Engagement Rate: {analysis.get('engagement_rate', 0)}% (of followers)
- Expected performance for ~10K follower account: {analysis['avg_likes']:,} likes, {analysis['avg_comments']:,} comments
- Typical engagement ratio: {analysis.get('engagement_ratio', 'N/A')}:1 (likes:comments)

TOP PERFORMING CONTENT EXAMPLES:
{top_examples if top_examples else "No examples available"}

Generate an Instagram post that is optimized for maximum engagement in this category. The post should:
1. Follow the successful patterns from the top-performing content
2. Use engaging hooks and storytelling techniques that work in this niche
3. Include relevant topics and themes that resonate with this audience
4. Be authentic and valuable to the target audience
"""
        
        # Add customization instructions
        tone_instructions = {
            "engaging": """Use an ENGAGING, story-driven tone:
            - Include emotion and personal connection
            - Ask rhetorical questions to involve the reader
            - Use 'you' and 'we' to create community
            - Add excitement with varied sentence lengths
            - Balance inspiration with authenticity
            - Example: 'Ever felt like...? Here's what changed everything for me...'""",
            
            "professional": """Use a PROFESSIONAL, authoritative tone:
            - Write with expertise and credibility
            - Use industry terminology appropriately
            - Reference data, research, or proven methods when relevant
            - Avoid slang, excessive emojis, or casual phrases
            - Maintain polished, articulate language
            - Example: 'Research shows that... Industry experts recommend... The key factor is...'""",
            
            "casual": """Use a CASUAL, friend-to-friend tone:
            - Write like you're texting your bestie
            - Use contractions (you're, don't, can't)
            - Include slang and colloquial expressions
            - Keep it super relatable and laid-back
            - Use lots of emojis naturally
            - Example: 'Okay so like... ngl this totally changed my life... you're gonna love this...'"""
        }
        
        length_instructions = {
            "short": "Keep it brief and punchy (50-100 words). Get to the point quickly.",
            "medium": "Make it medium length (100-200 words) with good detail.",
            "long": "Create a comprehensive, in-depth post (200-400 words) with full context."
        }
        
        format_instructions = {
            "post": """Format as a NARRATIVE POST with natural flow and storytelling:
            - Write in flowing paragraphs (not lists)
            - Use conversational, story-like language
            - Include natural transitions between ideas
            - Add emojis throughout for engagement
            - End with an inspiring closing line
            - Put hashtags at the very end
            Example structure: Opening hook → Personal story/insight → Key points woven into narrative → Closing thought → Hashtags""",
            
            "bullets": """Format as SCANNABLE BULLET POINTS for quick reading:
            - Start with a brief intro line (1 sentence max)
            - Use bullet points (• or numbered list) for each key point
            - Each bullet should be concise and actionable
            - Use emojis as bullet markers or at start of each point
            - NO paragraph text - only lists
            - End with hashtags
            Example: Brief intro → • Point 1 → • Point 2 → • Point 3 → Hashtags""",
            
            "script": """Format as a CONTENT SCRIPT with clearly labeled sections:
            - **HOOK:** (First 1-2 sentences to grab attention)
            - **SETUP:** (Context or problem statement)
            - **MAIN CONTENT:** (Key points, tips, or story)
            - **CALL-TO-ACTION:** (What you want audience to do)
            - **HASHTAGS:** (At the end)
            Use clear section headers with asterisks or caps. This is for someone to read and recreate the content."""
        }
        
        customization = f"""

CUSTOMIZATION REQUIREMENTS:
- Tone: {tone_instructions.get(tone, tone_instructions['engaging'])}
- Length: {length_instructions.get(length, length_instructions['medium'])}
- Format: {format_instructions.get(format, format_instructions['post'])}

You MUST follow the format instructions exactly. The output should look visually different based on the format chosen.

Output Format:
Caption: [Your content here - following the format structure above]

Hashtags: [Relevant hashtags]

Key Strategy: [Why this will perform well]"""
        
        prompt += customization

        return prompt
    
    async def generate_trend_content(
        self,
        category: str,
        platform: str = "instagram",
        tone: str = "engaging",
        length: str = "medium",
        format: str = "post"
    ) -> Dict[str, Any]:
        """
        生成基于趋势的内容
        
        Args:
            category: 类别
            platform: 平台
            tone: 语气
            length: 长度
            format: 格式
            
        Returns:
            生成结果
        """
        # Validate category (case-insensitive)
        valid_categories = ['finance', 'wellness', 'food', 'fitness', 'lifestyle', 'tech', 'fashion']
        if category.lower() not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        
        # Get creators in this category
        creators = self.get_creators_by_category(category, platform)
        logger.info(f"Found {len(creators)} creators in category '{category}'")
        
        if not creators:
            raise ValueError(f"No creators found in category '{category}'")
        
        # Analyze their posts
        analysis = self.analyze_posts(creators, platform)
        logger.info(f"Analyzed {analysis['total_posts']} posts from {len(creators)} creators")
        
        # Extract evidence
        evidence = analysis.get('evidence', {})
        
        # Build prompt with customization
        prompt = self.build_trend_prompt(category, analysis, platform, tone, length, format)
        
        # Generate content using OpenAI
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional Instagram content strategist specializing in data-driven content creation. You analyze engagement patterns and create optimized posts."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            generated_content = response.choices[0].message.content.strip()
            
            return {
                "success": True,
                "content": generated_content,
                "category": category,
                "creators_analyzed": len(creators),
                "posts_analyzed": analysis['total_posts'],
                "insights": {
                    "avg_likes": analysis['avg_likes'],
                    "avg_comments": analysis['avg_comments'],
                    "avg_engagement": analysis['avg_engagement'],
                    "raw_avg_likes": analysis['raw_avg_likes'],
                    "raw_avg_comments": analysis['raw_avg_comments'],
                    "raw_avg_engagement": analysis['raw_avg_engagement'],
                    "engagement_rate": analysis['engagement_rate'],
                    "engagement_ratio": analysis['engagement_ratio']
                },
                "evidence": evidence
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise ValueError(f"Failed to generate content: {str(e)}")
