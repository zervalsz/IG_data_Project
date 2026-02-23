"""
Style Generation Service
风格生成业务逻辑层 - 从数据库读取数据
"""

import os
from typing import Dict, List, Any, Optional
from openai import OpenAI

from database import (
    UserProfileRepository,
    UserSnapshotRepository,
    StylePromptRepository
)


class StyleGenerationService:
    """风格生成服务"""
    
    def __init__(self):
        # 初始化数据仓库
        self.profile_repo = UserProfileRepository()
        self.snapshot_repo = UserSnapshotRepository()
        self.prompt_repo = StylePromptRepository()
        
        # Lazy initialization for OpenAI client (only when needed for generation)
        self.client = None
        
        print("✅ StyleGenerationService 初始化完成")
    
    def _ensure_client(self):
        """Lazily initialize OpenAI API client when needed"""
        if self.client is None:
            # 初始化OpenAI API客户端
            api_key = os.getenv("OPENAI_API_KEY", "")
            if not api_key:
                raise ValueError("❌ OPENAI_API_KEY环境变量未设置")
            
            self.client = OpenAI(
                api_key=api_key
            )
            print("✅ OpenAI API client initialized")
    
    def get_available_creators(self, platform: str = "xiaohongshu") -> List[Dict[str, Any]]:
        """
        获取可用的创作者列表
        
        Args:
            platform: 平台类型
            
        Returns:
            创作者列表 [{"name": "xxx", "user_id": "xxx", "topics": [...], "style": "xxx"}, ...]
        """
        try:
            profiles = self.profile_repo.get_all_profiles(platform=platform)
            
            creators = []
            for profile in profiles:
                # For Instagram, user_id is the primary identifier
                user_id = profile.get("user_id", "未知")
                nickname = profile.get("nickname") or user_id  # Use user_id as display name if no nickname
                
                # 从profile_data中提取topics和style
                profile_data = profile.get("profile_data", {})
                topics = []
                style = "未知风格"
                
                if isinstance(profile_data, dict):
                    # 尝试提取topics (检查content_topics, topics, 关键主题)
                    if "content_topics" in profile_data:
                        topics = profile_data["content_topics"]
                    elif "topics" in profile_data:
                        topics = profile_data["topics"]
                    elif "关键主题" in profile_data:
                        topics = profile_data["关键主题"]
                    
                    # 尝试提取style - Instagram profiles have it in user_style.tone
                    user_style = profile_data.get("user_style", {})
                    if isinstance(user_style, dict) and "tone" in user_style:
                        style = user_style["tone"]
                    elif "content_style" in profile_data:
                        style_list = profile_data["content_style"]
                        style = ", ".join(style_list) if isinstance(style_list, list) else str(style_list)
                    elif "style" in profile_data:
                        style = profile_data["style"]
                    elif "风格" in profile_data:
                        style = profile_data["风格"]
                    elif "写作风格" in profile_data:
                        style = profile_data["写作风格"]
                
                creators.append({
                    "name": nickname,
                    "user_id": user_id,
                    "topics": topics if isinstance(topics, list) else [str(topics)],
                    "style": str(style) if style else "未知风格"
                })
            
            return creators
            
        except Exception as e:
            print(f"❌ 获取创作者列表失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def load_creator_profile(self, creator_name: str, platform: str = "xiaohongshu") -> Optional[Dict[str, Any]]:
        """
        加载创作者档案
        
        Args:
            creator_name: 创作者昵称
            platform: 平台类型
            
        Returns:
            档案数据 or None
        """
        try:
            profile = self.profile_repo.get_profile_by_nickname(creator_name, platform)
            if not profile:
                print(f"⚠️  未找到创作者档案: {creator_name}")
                return None
            
            # 返回profile_data部分
            return profile.get("profile_data", {})
            
        except Exception as e:
            print(f"❌ 加载创作者档案失败: {e}")
            return None
    
    def load_creator_notes(self, creator_name: str, platform: str = "xiaohongshu", limit: int = 5) -> List[Dict[str, Any]]:
        """
        加载创作者的笔记样本
        
        Args:
            creator_name: 创作者昵称
            platform: 平台类型
            limit: 返回笔记数量
            
        Returns:
            笔记列表
        """
        try:
            # 先获取user_id
            profile = self.profile_repo.get_profile_by_nickname(creator_name, platform)
            if not profile:
                print(f"⚠️  未找到创作者: {creator_name}")
                return []
            
            user_id = profile.get("user_id", "")
            if not user_id:
                print(f"⚠️  创作者缺少user_id: {creator_name}")
                return []
            
            # 获取笔记/帖子
            if platform == "instagram":
                # For Instagram, get posts from user_snapshots
                snapshot = self.snapshot_repo.get_by_user_id(user_id, platform)
                if snapshot and 'posts' in snapshot:
                    posts = snapshot['posts'][:limit]
                    print(f"✅ 加载了 {len(posts)} 条Instagram帖子")
                    return posts
                else:
                    print(f"⚠️  未找到Instagram帖子")
                    return []
            else:
                # For XiaoHongShu, use existing notes method
                notes = self.snapshot_repo.get_notes(user_id, platform, limit)
                return notes
            
        except Exception as e:
            print(f"❌ 加载创作者笔记失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def build_style_prompt(
        self,
        creator_profile: Dict[str, Any],
        sample_notes: List[Dict[str, Any]],
        user_topic: str,
        creator_name: str,
        platform: str = "xiaohongshu",
        tone: str = "engaging",
        length: str = "medium",
        format: str = "post"
    ) -> str:
        """
        构建风格生成提示词
        
        Args:
            creator_profile: 创作者档案
            sample_notes: 样本笔记
            user_topic: 用户输入的主题
            creator_name: 创作者昵称
            platform: 平台
            tone: 语气 (engaging/professional/casual)
            length: 长度 (short/medium/long)
            format: 格式 (post/bullets/script)
            
        Returns:
            完整的提示词
        """
        try:
            # 从数据库获取提示词模板
            prompt_data = self.prompt_repo.get_by_type("style_generation")
            if not prompt_data:
                print("⚠️  未找到提示词模板，使用默认模板")
                template = self._get_default_template(platform)
            else:
                template = prompt_data.get("template", self._get_default_template(platform))
            
            # 提取档案信息
            topics = ", ".join(creator_profile.get("content_topics", creator_profile.get("topics", [])))
            
            # Get detailed style information
            user_style = creator_profile.get("user_style", {})
            persona = user_style.get("persona", "")
            tone = user_style.get("tone", "")
            interests = ", ".join(user_style.get("interests", []))
            
            # Combine style information
            content_style = f"{persona}\n\nTone: {tone}\nInterests: {interests}" if persona else creator_profile.get("content_style", "")
            
            value_points = "\n".join([f"- {vp}" for vp in creator_profile.get("value_points", [])])
            
            # 格式化样本笔记
            sample_notes_text = ""
            if platform == "instagram":
                # For Instagram, format as actual captions from posts
                for i, note in enumerate(sample_notes, 1):
                    # Instagram posts have 'caption' field which might be a dict with 'text'
                    caption = ""
                    if 'caption' in note:
                        if isinstance(note['caption'], dict):
                            caption = note['caption'].get('text', '')
                        else:
                            caption = note['caption']
                    
                    like_count = note.get('like_count', 0)
                    if caption:
                        # Show full caption (truncate if too long)
                        display_caption = caption[:800] if len(caption) > 800 else caption
                        sample_notes_text += f"\n--- Example Post {i} ({like_count:,} likes) ---\n{display_caption}\n"
                
                # If no captions found, add a note
                if not sample_notes_text.strip():
                    sample_notes_text = "\n(No sample posts available - rely on creator profile description)\n"
            else:
                # XiaoHongShu format
                for i, note in enumerate(sample_notes, 1):
                    title = note.get("title", "")
                    desc = note.get("desc", note.get("description", ""))
                    sample_notes_text += f"\n【笔记{i}】\n标题：{title}\n内容：{desc}\n"
            
            # 填充模板
            prompt = template.format(
                nickname=creator_name,
                topics=topics,
                content_style=content_style,
                value_points=value_points,
                sample_notes=sample_notes_text,
                user_topic=user_topic
            )
            
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
                "short": "Keep it brief and concise (50-100 words or 1-2 sentences).",
                "medium": "Make it medium length (100-200 words or 2-4 paragraphs).",
                "long": "Create a comprehensive post (200-400 words or 4-6 paragraphs)."
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
            
            customization = f"""\n\nIMPORTANT CUSTOMIZATION:
- Tone: {tone_instructions.get(tone, tone_instructions['engaging'])}
- Length: {length_instructions.get(length, length_instructions['medium'])}
- Format: {format_instructions.get(format, format_instructions['post'])}

You MUST follow the format instructions exactly. The output should look visually different based on the format chosen."""
            prompt += customization
            
            return prompt
            
        except Exception as e:
            print(f"❌ 构建提示词失败: {e}")
            return self._get_fallback_prompt(creator_name, user_topic, platform)
    
    def generate_content(
        self,
        creator_name: str,
        user_topic: str,
        platform: str = "xiaohongshu",
        tone: str = "engaging",
        length: str = "medium",
        format: str = "post"
    ) -> Dict[str, Any]:
        """
        生成风格化内容
        
        Args:
            creator_name: 创作者昵称
            user_topic: 用户主题
            platform: 平台类型
            tone: 语气
            length: 长度
            format: 格式
            
        Returns:
            生成结果 {"success": bool, "content": str, "error": str}
        """
        try:
            # Ensure DeepSeek API client is initialized
            self._ensure_client()
            
            # 1. 加载创作者档案
            print(f"📥 加载创作者档案: {creator_name}")
            creator_profile = self.load_creator_profile(creator_name, platform)
            if not creator_profile:
                return {
                    "success": False,
                    "content": "",
                    "error": f"未找到创作者档案: {creator_name}"
                }
            
            # 2. 加载笔记样本
            print(f"📥 加载笔记样本...")
            sample_notes = self.load_creator_notes(creator_name, platform, limit=5)
            if not sample_notes:
                print("⚠️  未找到笔记样本，将基于档案信息生成")
            
            # 3. 构建提示词
            print(f"🔨 构建提示词...")
            prompt = self.build_style_prompt(
                creator_profile,
                sample_notes,
                user_topic,
                creator_name,
                platform,
                tone,
                length,
                format
            )
            
            # 4. 调用OpenAI API
            print(f"🤖 调用OpenAI API生成内容...")
            # Use English system message for Instagram
            system_message = "You are a professional content creation assistant." if platform == "instagram" else "你是一位专业的内容创作助手。"
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # 5. 提取生成内容
            generated_content = response.choices[0].message.content
            print(f"✅ 内容生成成功")
            
            return {
                "success": True,
                "content": generated_content,
                "error": ""
            }
            
        except Exception as e:
            error_msg = f"生成失败: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "content": "",
                "error": error_msg
            }
    
    def _get_default_template(self, platform: str = "xiaohongshu") -> str:
        """获取默认提示词模板"""
        if platform == "instagram":
            return """You are an expert at mimicking Instagram creator voices with precision.

【Creator Profile】
Username: @{nickname}
Content Topics: {topics}
Overall Style: {content_style}
Key Values: {value_points}

【Actual Posts from @{nickname}】
Study these REAL captions to understand their authentic voice:

{sample_notes}

【Style Analysis Instructions】
Before writing, analyze the creator's patterns:
1. **Opening Hooks**: How do they start posts? (specific moments, people, places, or declarations)
2. **Personal Details**: Do they reference specific times (4am), brands they own, family members, locations?
3. **Emotional Range**: What emotions do they express? (gratitude, humor, vulnerability, motivation)
4. **Signature Phrases**: Any catchphrases, sign-offs, or recurring words?
5. **Emoji Style**: How many emojis? Where placed? What types?
6. **Structure**: How do they organize thoughts? (story → reflection → gratitude? or bullets? or stream-of-consciousness?)
7. **Length & Rhythm**: Short punchy sentences? Long flowing paragraphs? Mix of both?

【Task】
Write an Instagram caption in @{nickname}'s EXACT voice about: "{user_topic}"

【Critical Requirements】
✓ Use SPECIFIC, CONCRETE details (not generic advice)
✓ Match their natural rhythm and sentence structure
✓ Include their signature elements and recurring themes
✓ Capture their authentic emotional range
✓ Mirror their emoji usage pattern exactly
✓ If they have catchphrases or sign-offs, use them appropriately
✓ Sound like THEM, not a generic motivational account

【Output Format】
Caption:
[Write the authentic caption here - make it sound like they actually wrote it]

Hashtags:
#hashtag1 #hashtag2 #hashtag3
"""
        else:
            return """你是一位经验丰富的小红书内容创作者，擅长模仿不同博主的风格进行创作。

【被模仿者档案】
昵称：{nickname}
内容主题：{topics}
内容风格：{content_style}
价值点：{value_points}

【参考笔记】（以下是该博主的典型笔记）
{sample_notes}

【任务】
请以这位博主的风格，为主题"{user_topic}"创作一篇小红书笔记。

【要求】
1. 文案风格要高度贴近该博主的特点
2. 保持该博主常用的表达方式和语气
3. 体现该博主的价值观和内容侧重点
4. 标题要吸引人，正文要有亮点
5. 适当添加emoji增加活力
6. 最后给出3-5个相关话题标签

【输出格式】
标题：[在这里输出标题]

正文：
[在这里输出正文内容]

话题标签：
#标签1 #标签2 #标签3
"""
    
    def _get_fallback_prompt(self, creator_name: str, user_topic: str, platform: str = "xiaohongshu") -> str:
        """获取降级提示词"""
        if platform == "instagram":
            return f"""Create an Instagram post in the style of "{creator_name}" about the topic: "{user_topic}"

Requirements:
1. Engaging caption
2. Authentic and valuable content
3. Add appropriate emojis
4. Include 3-5 hashtags

Output format:
Caption: [caption]
Hashtags: #hashtag1 #hashtag2
"""
        else:
            return f"""请以"{creator_name}"的风格，为主题"{user_topic}"创作一篇小红书笔记。

要求：
1. 标题吸引人
2. 内容真实有价值
3. 添加适当的emoji
4. 给出3-5个话题标签

输出格式：
标题：[标题]
正文：[正文]
话题标签：#标签1 #标签2
"""
