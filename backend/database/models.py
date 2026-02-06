"""
Data Models & Schemas
MongoDB数据模型定义
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class PlatformType(str, Enum):
    """平台类型枚举"""
    XIAOHONGSHU = "xiaohongshu"
    INSTAGRAM = "instagram"


# =====================================================
# 1. User Profile Models
# =====================================================

class UserProfileData(BaseModel):
    """用户档案数据"""
    topics: List[str] = Field(default_factory=list, description="内容主题")
    content_style: str = Field(default="", description="内容风格")
    value_points: List[str] = Field(default_factory=list, description="价值点")
    engagement: Dict[str, Any] = Field(default_factory=dict, description="互动数据")


class UserProfile(BaseModel):
    """用户档案完整模型"""
    platform: PlatformType
    user_id: str
    nickname: str
    profile_data: UserProfileData
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# =====================================================
# 2. User Snapshot Models
# =====================================================

class NoteData(BaseModel):
    """笔记数据"""
    note_id: str = Field(alias="id")
    title: str = Field(default="")
    desc: str = Field(default="")
    liked_count: int = Field(default=0, alias="likes")
    collected_count: int = Field(default=0, alias="collects")
    comment_count: int = Field(default=0, alias="comments")
    share_count: int = Field(default=0, alias="shares")
    
    class Config:
        populate_by_name = True


class UserSnapshot(BaseModel):
    """用户笔记快照"""
    platform: PlatformType
    user_id: str
    notes: List[Dict[str, Any]]  # 原始笔记数据
    total_notes: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now)


# =====================================================
# 3. User Embedding Models
# =====================================================

class UserEmbedding(BaseModel):
    """用户向量embedding"""
    user_id: str
    platform: PlatformType
    embedding: List[float]  # 512维向量
    model: str = "BAAI/bge-small-zh-v1.5"
    dimension: int = 512
    created_at: datetime = Field(default_factory=datetime.now)


# =====================================================
# 3.5 Post Embedding Models
# =====================================================

class PostEmbedding(BaseModel):
    """帖子多模态embedding"""
    post_id: str
    user_id: str
    username: str
    platform: PlatformType
    embedding: List[float]  # 多模态向量
    caption: str = ""
    objects: List[str] = Field(default_factory=list)
    ocr_text: List[str] = Field(default_factory=list)
    like_count: int = 0
    comment_count: int = 0
    play_count: Optional[int] = None
    media_urls: List[str] = Field(default_factory=list)
    model: str = "all-MiniLM-L6-v2"
    dimension: int = 384
    created_at: datetime = Field(default_factory=datetime.now)


# =====================================================
# 4. Creator Network Models
# =====================================================

class CreatorNode(BaseModel):
    """创作者节点"""
    id: str
    name: str
    platform: PlatformType
    category: str = "creator"


class CreatorEdge(BaseModel):
    """创作者关系边"""
    source: str
    target: str
    similarity: float
    label: str = ""


class CreatorNetwork(BaseModel):
    """创作者网络"""
    platform: PlatformType
    network_data: Dict[str, Any]  # {creators: [...], edges: [...]}
    created_at: datetime = Field(default_factory=datetime.now)


# =====================================================
# 5. Style Prompt Models
# =====================================================

class StylePromptType(str, Enum):
    """提示词类型"""
    STYLE_GENERATION = "style_generation"
    CONTENT_ANALYSIS = "content_analysis"


class StylePrompt(BaseModel):
    """风格生成提示词模板"""
    platform: PlatformType
    prompt_type: StylePromptType
    name: str = Field(description="模板名称")
    template: str = Field(description="提示词模板")
    variables: List[str] = Field(default_factory=list, description="模板变量")
    description: str = Field(default="", description="模板描述")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


# =====================================================
# 6. Platform Config Models
# =====================================================

class PlatformAPIConfig(BaseModel):
    """平台API配置"""
    base_url: str
    endpoints: Dict[str, str]
    headers: Dict[str, str] = Field(default_factory=dict)


class PlatformConfig(BaseModel):
    """平台配置"""
    platform: PlatformType
    api_config: PlatformAPIConfig
    auth_token: str = Field(default="", description="认证令牌")
    enabled: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
