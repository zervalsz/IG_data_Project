"""
Trend-based content generation router
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/trend")


class TrendGenerateRequest(BaseModel):
    """趋势生成请求"""
    category: str = Field(..., description="类别: finance, wellness, food, fitness, lifestyle")
    platform: str = Field(default="instagram", description="平台")


class TrendGenerateResponse(BaseModel):
    """趋势生成响应"""
    success: bool
    content: str
    insights: Optional[Dict[str, Any]] = None
    category: str
    creators_analyzed: int = 0
    posts_analyzed: int = 0


@router.post("/generate", response_model=TrendGenerateResponse)
async def generate_trend_content(request: TrendGenerateRequest):
    """
    基于趋势数据生成内容
    
    分析指定类别中所有创作者的帖子，识别高参与度内容模式，
    生成优化的内容建议
    """
    try:
        from api.services.trend_service import TrendService
        
        service = TrendService()
        result = await service.generate_trend_content(
            category=request.category,
            platform=request.platform
        )
        
        return TrendGenerateResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Trend generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@router.get("/categories")
async def get_categories():
    """获取可用的内容类别"""
    return {
        "categories": [
            {
                "id": "finance",
                "name": "Finance & Money",
                "icon": "💰",
                "description": "Personal finance, investing, money management"
            },
            {
                "id": "wellness",
                "name": "Mental Health & Wellness",
                "icon": "🧘",
                "description": "Mental health, psychology, self-care"
            },
            {
                "id": "food",
                "name": "Food & Cooking",
                "icon": "🍳",
                "description": "Recipes, cooking tips, food culture"
            },
            {
                "id": "fitness",
                "name": "Fitness & Sports",
                "icon": "💪",
                "description": "Workouts, fitness challenges, health"
            },
            {
                "id": "lifestyle",
                "name": "Lifestyle & Entertainment",
                "icon": "✨",
                "description": "Dating, comedy, travel, general lifestyle"
            }
        ]
    }
