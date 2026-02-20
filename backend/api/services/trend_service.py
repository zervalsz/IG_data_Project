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
    
    # Category mappings
    CATEGORY_KEYWORDS = {
        'finance': ['finance', 'invest', 'money', 'debt', 'wealth', 'budget'],
        'wellness': ['mental', 'wellness', 'psychology', 'trauma', 'health', 'mindfulness'],
        'food': ['food', 'cook', 'recipe', 'kitchen', 'meal'],
        'fitness': ['fitness', 'workout', 'sport', 'exercise', 'training'],
        'lifestyle': []  # catch-all for others
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
        将创作者分类到某个类别
        
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
            if category == 'lifestyle':
                continue  # Skip lifestyle (it's the default)
            
            if any(kw in all_text for kw in keywords):
                return category
        
        return 'lifestyle'
    
    def get_creators_by_category(self, category: str, platform: str = "instagram") -> List[Dict[str, Any]]:
        """
        获取指定类别的创作者
        
        Args:
            category: 类别名称
            platform: 平台
            
        Returns:
            创作者列表
        """
        # Get all profiles
        profiles = self.profile_repo.get_all_profiles(platform=platform)
        
        # Filter by category
        categorized = []
        for profile in profiles:
            if self.categorize_creator(profile) == category:
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
            'top_captions': top_captions[:10]
        }
    
    def build_trend_prompt(
        self,
        category: str,
        analysis: Dict[str, Any],
        platform: str = "instagram"
    ) -> str:
        """
        构建趋势生成提示词
        
        Args:
            category: 类别
            analysis: 分析数据
            platform: 平台
            
        Returns:
            提示词
        """
        category_names = {
            'finance': 'Finance & Money',
            'wellness': 'Mental Health & Wellness',
            'food': 'Food & Cooking',
            'fitness': 'Fitness & Sports',
            'lifestyle': 'Lifestyle & Entertainment'
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

Format the output as:
Caption: [Your engaging caption here]

Hashtags: [Relevant hashtags for maximum reach]

Key Strategy: [Brief explanation of why this content will perform well based on the data]"""

        return prompt
    
    async def generate_trend_content(
        self,
        category: str,
        platform: str = "instagram"
    ) -> Dict[str, Any]:
        """
        生成基于趋势的内容
        
        Args:
            category: 类别
            platform: 平台
            
        Returns:
            生成结果
        """
        # Validate category
        valid_categories = ['finance', 'wellness', 'food', 'fitness', 'lifestyle']
        if category not in valid_categories:
            raise ValueError(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        
        # Get creators in this category
        creators = self.get_creators_by_category(category, platform)
        logger.info(f"Found {len(creators)} creators in category '{category}'")
        
        if not creators:
            raise ValueError(f"No creators found in category '{category}'")
        
        # Analyze their posts
        analysis = self.analyze_posts(creators, platform)
        logger.info(f"Analyzed {analysis['total_posts']} posts from {len(creators)} creators")
        
        # Build prompt
        prompt = self.build_trend_prompt(category, analysis, platform)
        
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
                }
            }
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise ValueError(f"Failed to generate content: {str(e)}")
