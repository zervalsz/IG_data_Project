"""
Style Generation API Router - 使用Service层
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict

from api.services import StyleGenerationService

router = APIRouter(prefix="/api/style", tags=["style"])

# 初始化服务（懒加载）
_style_service = None


def get_style_service() -> StyleGenerationService:
    """获取风格生成服务实例"""
    global _style_service
    if _style_service is None:
        _style_service = StyleGenerationService()
    return _style_service


# =====================================================
# Request/Response Models
# =====================================================

class GenerateRequest(BaseModel):
    """生成请求模型"""
    creator_name: str
    user_input: str  # 改为user_input以匹配前端
    platform: str = "xiaohongshu"  # 可选字段，默认小红书
    tone: str = "engaging"  # 语气选项
    length: str = "medium"  # 长度选项
    format: str = "post"  # 格式选项


class ConsistencyEvidence(BaseModel):
    """一致性证据项"""
    metric: str
    status: str
    detail: str


class ConsistencyScore(BaseModel):
    """风格一致性评分"""
    overall_score: int
    level: str
    evidence: List[ConsistencyEvidence]
    explanation: str


class GenerateResponse(BaseModel):
    """生成响应模型"""
    success: bool
    content: str
    consistency_score: ConsistencyScore = None
    error: str = ""


class CreatorInfo(BaseModel):
    """创作者信息"""
    id: str
    name: str


# =====================================================
# API Endpoints
# =====================================================

@router.get("/creators")
async def list_creators(platform: str = None):
    """
    获取可用的创作者列表
    
    Args:
        platform: 平台类型（可选，不指定则返回所有平台）
        
    Returns:
        创作者列表，包含success标志
    """
    try:
        service = get_style_service()
        
        # 如果未指定platform，返回所有平台的创作者
        if platform is None:
            all_creators = []
            for plat in ["xiaohongshu", "instagram"]:
                creators = service.get_available_creators(plat)
                # 为每个创作者添加platform字段
                for creator in creators:
                    creator["platform"] = plat
                all_creators.extend(creators)
            
            return {
                "success": True,
                "creators": all_creators
            }
        else:
            creators = service.get_available_creators(platform)
            # 添加platform字段
            for creator in creators:
                creator["platform"] = platform
            
            return {
                "success": True,
                "creators": creators
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取创作者列表失败: {str(e)}")


@router.post("/generate", response_model=GenerateResponse)
async def generate_style_content(request: GenerateRequest):
    """
    生成风格化内容
    
    Args:
        request: 生成请求（创作者名称、主题、平台、语气、长度、格式）
        
    Returns:
        生成结果
    """
    try:
        service = get_style_service()
        result = service.generate_content(
            creator_name=request.creator_name,
            user_topic=request.user_input,  # 使用user_input字段
            platform=request.platform,
            tone=request.tone,
            length=request.length,
            format=request.format
        )
        return result
    except Exception as e:
        return GenerateResponse(
            success=False,
            content="",
            error=f"生成失败: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "service": "style_generation"}
